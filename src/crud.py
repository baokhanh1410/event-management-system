import pandas as pd
from sqlalchemy import text

def get_all_events(session):
    """Lấy danh sách sự kiện kèm thông tin địa điểm và ban tổ chức."""
    query = text("""
        SELECT e.event_id, e.event_name, e.event_date, v.venue_name, o.organizer_name, e.status, e.category
        FROM events e
        JOIN venues v ON e.venue_id = v.venue_id
        LEFT JOIN organizers o ON e.organizer_id = o.organizer_id
        ORDER BY e.event_date DESC
    """)
    with session.get_bind().connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def create_event(session, name, start_datetime, end_datetime, venue_id, org_id, category, price):
    query = text("""
        INSERT INTO events (event_name, event_date, end_time, venue_id, organizer_id, category, base_price)
        VALUES (:name, :start, :end, :v_id, :o_id, :cat, :price)
    """)
    try:
        session.execute(query, {
            "name": name, "start": start_datetime, "end": end_datetime,
            "v_id": venue_id, "o_id": org_id, "cat": category, "price": price
        })
        session.commit()
        return True, "Thêm sự kiện thành công!"
    except Exception as e:
        # Trigger check_venue_conflict
        session.rollback()
        return False, f"Lỗi: {str(e).split(']')[1] if ']' in str(e) else e}"