import pandas as pd
from sqlalchemy import text

# ============================================================
# PHẦN 1: EVENTS — CRUD cho quản lý sự kiện
# ============================================================

def get_all_events(session):
    """Lấy danh sách sự kiện kèm thông tin địa điểm, ban tổ chức và danh sách thể loại."""
    query = text("""
        SELECT e.event_id, e.event_name, e.event_date, v.venue_name, o.organizer_name, e.status, e.base_price,
               GROUP_CONCAT(c.category_name SEPARATOR ', ') as categories
        FROM events e
        JOIN venues v ON e.venue_id = v.venue_id
        LEFT JOIN organizers o ON e.organizer_id = o.organizer_id
        LEFT JOIN event_categories ec ON e.event_id = ec.event_id
        LEFT JOIN categories c ON ec.category_id = c.category_id
        GROUP BY e.event_id, e.event_name, e.event_date, v.venue_name, o.organizer_name, e.status, e.base_price
        ORDER BY e.event_date DESC
    """)
    with session.get_bind().connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def get_guest_registered_events(session, guest_id):
    """Lấy danh sách sự kiện mà guest ĐÃ ĐĂNG KÝ."""
    query = text("""
        SELECT e.event_id, e.event_name, e.event_date, v.venue_name, o.organizer_name, e.status, e.base_price,
               GROUP_CONCAT(c.category_name SEPARATOR ', ') as categories
        FROM events e
        JOIN registrations r ON e.event_id = r.event_id
        JOIN venues v ON e.venue_id = v.venue_id
        LEFT JOIN organizers o ON e.organizer_id = o.organizer_id
        LEFT JOIN event_categories ec ON e.event_id = ec.event_id
        LEFT JOIN categories c ON ec.category_id = c.category_id
        WHERE r.guest_id = :gid
        GROUP BY e.event_id, e.event_name, e.event_date, v.venue_name, o.organizer_name, e.status, e.base_price
        ORDER BY e.event_date DESC
    """)
    with session.get_bind().connect() as conn:
        df = pd.read_sql(query, conn, params={"gid": guest_id})
    return df

def get_categories(session):
    """Lấy danh sách các thể loại phục vụ dropdown."""
    query = text("SELECT category_id, category_name FROM categories ORDER BY category_name ASC")
    with session.get_bind().connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def create_event(session, name, start_datetime, end_datetime, venue_id, org_id, category_ids, price):
    """Thêm sự kiện mới vào database."""
    query = text("""
        INSERT INTO events (event_name, event_date, end_time, venue_id, organizer_id, base_price)
        VALUES (:name, :start, :end, :v_id, :o_id, :price)
    """)
    try:
        session.execute(query, {
            "name": name, "start": start_datetime, "end": end_datetime,
            "v_id": venue_id, "o_id": org_id, "price": price
        })
        # Lấy ID của sự kiện vừa tạo
        result = session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
        new_event_id = result[0]
        
        # Insert categories
        if category_ids:
            cat_query = text("INSERT INTO event_categories (event_id, category_id) VALUES (:eid, :cid)")
            for cid in category_ids:
                session.execute(cat_query, {"eid": new_event_id, "cid": cid})
                
        session.commit()
        return True, "Thêm sự kiện thành công!"
    except Exception as e:
        # Trigger check_venue_conflict
        session.rollback()
        error_msg = str(e)
        # Trích xuất phần message sau dấu ] nếu có (từ MySQL error format)
        if ']' in error_msg:
            parts = error_msg.split(']', 1)
            error_msg = parts[1].strip() if len(parts) > 1 else error_msg
        return False, f"Lỗi: {error_msg}"

def get_event_by_id(session, event_id):
    """Lấy thông tin chi tiết một sự kiện theo ID."""
    query = text("""
        SELECT event_id, event_name, event_date, end_time, venue_id, organizer_id, status, base_price
        FROM events
        WHERE event_id = :eid
    """)
    cat_query = text("SELECT category_id FROM event_categories WHERE event_id = :eid")
    
    with session.get_bind().connect() as conn:
        df = pd.read_sql(query, conn, params={"eid": event_id})
        cats_df = pd.read_sql(cat_query, conn, params={"eid": event_id})
        
    if not df.empty:
        df['category_ids'] = [cats_df['category_id'].tolist()]
    return df

def update_event(session, event_id, name, start_datetime, end_datetime, venue_id, org_id, category_ids, price):
    """Cập nhật thông tin sự kiện."""
    query = text("""
        UPDATE events
        SET event_name = :name, event_date = :start, end_time = :end,
            venue_id = :v_id, organizer_id = :o_id, base_price = :price
        WHERE event_id = :eid
    """)
    try:
        session.execute(query, {
            "name": name, "start": start_datetime, "end": end_datetime,
            "v_id": venue_id, "o_id": org_id, "price": price,
            "eid": event_id
        })
        
        # Xoá mapping cũ và thêm mới
        session.execute(text("DELETE FROM event_categories WHERE event_id = :eid"), {"eid": event_id})
        if category_ids:
            cat_query = text("INSERT INTO event_categories (event_id, category_id) VALUES (:eid, :cid)")
            for cid in category_ids:
                session.execute(cat_query, {"eid": event_id, "cid": cid})
                
        session.commit()
        return True, "Cập nhật sự kiện thành công!"
    except Exception as e:
        session.rollback()
        error_msg = str(e)
        if ']' in error_msg:
            parts = error_msg.split(']', 1)
            error_msg = parts[1].strip() if len(parts) > 1 else error_msg
        return False, f"Lỗi: {error_msg}"

# ============================================================
# PHẦN 2: ATTENDANCE — CRUD cho đăng ký & check-in
# ============================================================

def get_events_list(session):
    """Trả danh sách (event_id, event_name) cho dropdown."""
    query = text("""
        SELECT event_id, event_name FROM events ORDER BY event_date DESC
    """)
    with session.get_bind().connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def get_available_events_for_guest(session, guest_id):
    """Trả danh sách (event_id, event_name) mà guest CHƯA ĐĂNG KÝ cho dropdown."""
    query = text("""
        SELECT event_id, event_name 
        FROM events 
        WHERE event_id NOT IN (
            SELECT event_id FROM registrations WHERE guest_id = :gid
        )
        ORDER BY event_date DESC
    """)
    with session.get_bind().connect() as conn:
        df = pd.read_sql(query, conn, params={"gid": guest_id})
    return df

def get_guests_list(session):
    """Trả danh sách (guest_id, guest_name) cho dropdown."""
    query = text("""
        SELECT guest_id, guest_name FROM guests ORDER BY guest_name ASC
    """)
    with session.get_bind().connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def get_registrations_by_event(session, event_id):
    """Lấy danh sách đăng ký theo sự kiện, JOIN với guests để hiển thị tên."""
    query = text("""
        SELECT r.registration_id, g.guest_name, g.guest_email, g.phone_number,
               r.registration_date, r.attendance_status, r.feedback_rating
        FROM registrations r
        JOIN guests g ON r.guest_id = g.guest_id
        WHERE r.event_id = :eid
        ORDER BY r.registration_date DESC
    """)
    with session.get_bind().connect() as conn:
        df = pd.read_sql(query, conn, params={"eid": event_id})
    return df

def get_guest_own_registrations(session, event_id, guest_id):
    """Lấy danh sách đăng ký của một guest cho một sự kiện cụ thể."""
    query = text("""
        SELECT r.registration_id, g.guest_name, g.guest_email, g.phone_number,
               r.registration_date, r.attendance_status, r.feedback_rating
        FROM registrations r
        JOIN guests g ON r.guest_id = g.guest_id
        WHERE r.event_id = :eid AND r.guest_id = :gid
        ORDER BY r.registration_date DESC
    """)
    with session.get_bind().connect() as conn:
        df = pd.read_sql(query, conn, params={"eid": event_id, "gid": guest_id})
    return df

def create_registration(session, event_id, guest_id):
    """Đăng ký khách mời cho sự kiện. Kiểm tra trùng lặp trước khi insert."""
    # Kiểm tra đã đăng ký chưa
    check_query = text("""
        SELECT COUNT(*) as cnt FROM registrations
        WHERE event_id = :eid AND guest_id = :gid
    """)
    result = session.execute(check_query, {"eid": event_id, "gid": guest_id}).fetchone()
    if result[0] > 0:
        return False, "Khách đã đăng ký sự kiện này rồi!"

    # Insert registration mới
    insert_query = text("""
        INSERT INTO registrations (event_id, guest_id, registration_date, attendance_status, feedback_rating)
        VALUES (:eid, :gid, NOW(), 0, 0)
    """)
    try:
        session.execute(insert_query, {"eid": event_id, "gid": guest_id})
        session.commit()
        return True, "Đăng ký thành công!"
    except Exception as e:
        session.rollback()
        return False, f"Lỗi: {str(e)}"

def check_in_guest(session, registration_id):
    """Gọi Stored Procedure sp_check_in_guest để check-in khách mời."""
    try:
        session.execute(text("CALL sp_check_in_guest(:rid)"), {"rid": registration_id})
        session.commit()
        return True, "Check-in thành công!"
    except Exception as e:
        session.rollback()
        error_msg = str(e)
        # Trích xuất message từ SIGNAL SQLSTATE '45000'
        if ']' in error_msg:
            parts = error_msg.split(']', 1)
            error_msg = parts[1].strip() if len(parts) > 1 else error_msg
        return False, f"{error_msg}"

def get_attendance_summary(session):
    """Lấy thống kê tỉ lệ tham dự từ View vw_event_attendance_summary."""
    query = text("""
        SELECT * FROM vw_event_attendance_summary
    """)
    with session.get_bind().connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def get_guest_profile(session, guest_id):
    """Lấy thông tin khách mời (Guest) theo ID."""
    query = text("""
        SELECT guest_name, guest_email, phone_number
        FROM guests
        WHERE guest_id = :gid
    """)
    result = session.execute(query, {"gid": guest_id}).fetchone()
    if result:
        return {
            "name": result[0],
            "email": result[1],
            "phone": result[2]
        }
    return None

# ============================================================
# PHẦN 3: FINANCE — CRUD cho quản lý tài chính
# ============================================================

def get_finance_summary(session):
    """Lấy tổng hợp tài chính từ View vw_finance_summary."""
    query = text("""
        SELECT * FROM vw_finance_summary
    """)
    with session.get_bind().connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def get_finance_by_event(session, event_id):
    """Lấy chi tiết tài chính của 1 sự kiện."""
    query = text("""
        SELECT finance_id, planned_budget, actual_cost
        FROM event_finance
        WHERE event_id = :eid
    """)
    result = session.execute(query, {"eid": event_id}).fetchone()
    if result:
        return {
            "finance_id": result[0],
            "planned_budget": float(result[1]),
            "actual_cost": float(result[2])
        }
    return None

def update_finance(session, finance_id, planned_budget, actual_cost):
    """Cập nhật bản ghi tài chính."""
    query = text("""
        UPDATE event_finance
        SET planned_budget = :pb, actual_cost = :ac
        WHERE finance_id = :fid
    """)
    try:
        session.execute(query, {
            "pb": planned_budget, "ac": actual_cost,
            "fid": finance_id
        })
        session.commit()
        return True, "Cập nhật tài chính thành công!"
    except Exception as e:
        session.rollback()
        return False, f"Lỗi: {str(e)}"

# ============================================================
# PHẦN 4: RECOMMENDATION — Lấy dữ liệu cho ML
# ============================================================

def get_data_for_recommendation(session):
    """
    Lấy dữ liệu huấn luyện cho XGBoost từ lịch sử đăng ký,
    bao gồm event_id, guest_id, categories, base_price, và attendance_status (Target).
    """
    query = text("""
        SELECT 
            r.guest_id,
            e.event_id,
            e.base_price,
            r.attendance_status,
            GROUP_CONCAT(c.category_name SEPARATOR ', ') as categories
        FROM registrations r
        JOIN events e ON r.event_id = e.event_id
        LEFT JOIN event_categories ec ON e.event_id = ec.event_id
        LEFT JOIN categories c ON ec.category_id = c.category_id
        GROUP BY r.guest_id, e.event_id, e.base_price, r.attendance_status
    """)
    with session.get_bind().connect() as conn:
        df = pd.read_sql(query, conn)
    return df