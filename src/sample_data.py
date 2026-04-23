import random
from sqlalchemy import text
from faker import Faker
from datetime import datetime, timedelta
fake = Faker()
NUM_ROWS = 510

# Hàm xử lý lỗi dấu nháy đơn trong chuỗi (rất hay gặp với Faker)
def escape_str(text):
    return str(text).replace("'", "''")

def generate_seed_data():
    with open('sql/seed.sql', 'w', encoding='utf-8') as f:
        # Tắt kiểm tra khóa ngoại để quá trình insert không bị lỗi thứ tự
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

        # 1. Sample data for Venues
        f.write("-- Data for Venues\n")
        for i in range(1, NUM_ROWS + 1):
            name = escape_str(fake.company() + " Center")
            addr = escape_str(fake.address().replace('\n', ', '))
            capacity = random.randint(100, 1000)
            f.write(f"INSERT INTO venues (venue_id, venue_name, venue_address, capacity) VALUES ({i}, '{name}', '{addr}', {capacity});\n")

        # 2. Sample data for Organizers
        f.write("\n-- Data for Organizers\n")
        for i in range(1, NUM_ROWS + 1):
            name = escape_str(fake.company())
            addr = escape_str(fake.address().replace('\n', ', '))
            phone = fake.phone_number()[:16]
            f.write(f"INSERT INTO organizers (organizer_id, organizer_name, address, phone_number) VALUES ({i}, '{name}', '{addr}', '{phone}');\n")

        # 3. Sample data for Events (Đã cập nhật end_time)
        f.write("\n-- Data for Events\n")
        categories = ['Conference', 'Workshop', 'Seminar', 'Webinar', 'Concert']
        statuses = ['Upcoming', 'Ongoing', 'Completed', 'Cancelled']
        for i in range(1, NUM_ROWS + 1):
            name = escape_str(fake.catch_phrase() + " Event")
            
            # Tạo thời gian bắt đầu ngẫu nhiên
            start_dt = fake.date_time_between(start_date='-1y', end_date='+1y')
            start_str = start_dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Tạo end_time: cộng thêm từ 1 đến 4 giờ ngẫu nhiên
            end_dt = start_dt + timedelta(hours=random.randint(1, 4))
            end_str = end_dt.strftime('%Y-%m-%d %H:%M:%S')
            
            v_id = random.randint(1, NUM_ROWS)
            o_id = random.randint(1, NUM_ROWS)
            category = random.choice(categories)
            status = random.choice(statuses)
            base_price = round(random.uniform(50.0, 500.0), 2)
            
            # Cập nhật thứ tự cột và giá trị insert cho phù hợp với lệnh ALTER TABLE trước đó
            f.write(f"INSERT INTO events (event_id, event_name, event_date, end_time, venue_id, category, status, base_price, organizer_id) "
                    f"VALUES ({i}, '{name}', '{start_str}', '{end_str}', {v_id}, '{category}', '{status}', {base_price}, {o_id});\n")

        # 4. Sample data for Event Finance
        f.write("\n-- Data for Event Finances\n")
        for i in range(1, NUM_ROWS + 1):
            planned = round(random.uniform(5000.0, 20000.0), 2)
            actual = round(random.uniform(4000.0, 25000.0), 2)
            revenue = round(random.uniform(0.0, 30000.0), 2)
            f.write(f"INSERT INTO event_finance (finance_id, event_id, planned_budget, actual_cost, revenue) VALUES ({i}, {i}, {planned}, {actual}, {revenue});\n")

        # 5. Sample data for Guests
        f.write("\n-- Data for Guests\n")
        for i in range(1, NUM_ROWS + 1):
            name = escape_str(fake.name())
            email = escape_str(fake.unique.email())
            phone = fake.phone_number()[:16]
            f.write(f"INSERT INTO guests (guest_id, guest_name, guest_email, phone_number) VALUES ({i}, '{name}', '{email}', '{phone}');\n")

        # 6. Sample data for Registrations
        f.write("\n-- Data for Registrations\n")
        for i in range(1, NUM_ROWS + 1):
            e_id = random.randint(1, NUM_ROWS)
            g_id = random.randint(1, NUM_ROWS)
            reg_date = fake.date_time_this_year().strftime('%Y-%m-%d %H:%M:%S')
            
            att_status = random.choice([True, False])
            fb_rating = random.randint(1, 5) if att_status else 0 
            att_str = '1' if att_status else '0'
            
            f.write(f"INSERT INTO registrations (registration_id, event_id, guest_id, registration_date, attendance_status, feedback_rating) VALUES ({i}, {e_id}, {g_id}, '{reg_date}', {att_str}, {fb_rating});\n")

        # Bật lại kiểm tra khóa ngoại
        f.write("\nSET FOREIGN_KEY_CHECKS = 1;\n")

    print(f"Successfully generated {NUM_ROWS} rows of sample data for each table in 'sql/seed.sql'.")

def insert_seed_data(session):
    with open('sql/seed.sql', 'r', encoding='utf-8') as f:
        sql_commands = f.read().split(';')
        for command in sql_commands:
            cmd = command.strip()
            if cmd:
                try:
                    session.execute(text(cmd))
                    session.commit()
                except Exception as e:
                    session.rollback()
                    print(f"Error executing command: {cmd}\nError: {e}")
    print("Seed data inserted into the database successfully.")