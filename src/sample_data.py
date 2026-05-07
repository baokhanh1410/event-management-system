import random
import bcrypt
from sqlalchemy import text
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
NUM_EVENTS = 50
NUM_GUESTS = 510

# ============================================================
# HELPER FUNCTIONS
# ============================================================

# Function to handle single quotes in strings (very common with Faker)
def escape_str(text):
    return str(text).replace("'", "''")

# ============================================================
# SEED DATA GENERATION
# ============================================================

def generate_seed_data():
    """Generates SQL insert statements for dummy data and writes to seed.sql"""
    with open('sql/seed.sql', 'w', encoding='utf-8') as f:
        # Disable foreign key checks to avoid order-related insertion errors
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

        # 1. Sample data for Venues
        f.write("-- Data for Venues\n")
        for i in range(1, NUM_EVENTS + 1):
            name = escape_str(fake.company() + " Center")
            addr = escape_str(fake.address().replace('\n', ', '))
            capacity = random.randint(100, 1000)
            f.write(f"INSERT INTO venues (venue_id, venue_name, venue_address, capacity) VALUES ({i}, '{name}', '{addr}', {capacity});\n")

        # 2. Sample data for Organizers
        f.write("\n-- Data for Organizers\n")
        for i in range(1, NUM_EVENTS + 1):
            name = escape_str(fake.company())
            addr = escape_str(fake.address().replace('\n', ', '))
            phone = fake.phone_number()[:16]
            f.write(f"INSERT INTO organizers (organizer_id, organizer_name, address, phone_number) VALUES ({i}, '{name}', '{addr}', '{phone}');\n")

        # 3. Sample data for Categories
        f.write("\n-- Data for Categories\n")
        categories = ['Conference', 'Workshop', 'Seminar', 'Webinar', 'Concert']
        for i, cat in enumerate(categories, 1):
            f.write(f"INSERT INTO categories (category_id, category_name) VALUES ({i}, '{cat}');\n")

        # ============================================================
        # PRE-CALCULATION logic for Attendance & Prices
        # ============================================================
        event_statuses = {}
        event_reg_map = {}  # event_id -> list of (guest_id, att_status, fb_rating)
        
        # Assign random status to each event
        statuses = ['Upcoming', 'Ongoing', 'Completed', 'Cancelled']
        for i in range(1, NUM_EVENTS + 1):
            event_statuses[i] = random.choice(statuses)
        
        # Pre-assign registrations: each guest registers for 1-4 events
        for i in range(1, NUM_EVENTS + 1):
            event_reg_map[i] = []
        
        for g_id in range(1, NUM_GUESTS + 1):
            num_events = random.randint(1, 4)
            selected_events = random.sample(range(1, NUM_EVENTS + 1), num_events)
            for e_id in selected_events:
                # Check-in rate depends on event status
                status = event_statuses[e_id]
                if status == 'Completed':
                    att_status = random.random() < random.uniform(0.7, 0.9)
                elif status in ('Upcoming', 'Cancelled'):
                    att_status = random.random() < random.uniform(0.1, 0.3)
                else:  # Ongoing
                    att_status = random.random() < random.uniform(0.4, 0.6)
                
                fb_rating = random.randint(1, 5) if att_status else 0
                event_reg_map[e_id].append((g_id, att_status, fb_rating))

        # ============================================================
        # 4. Sample data for Events (base_price derived from planned_budget)
        # ============================================================
        f.write("\n-- Data for Events\n")
        event_data = {}  # Save info for Finance data generation later
        for i in range(1, NUM_EVENTS + 1):
            name = escape_str(fake.catch_phrase() + " Event")
            
            # Generate random start time
            start_dt = fake.date_time_between(start_date='-1y', end_date='+1y')
            start_str = start_dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Generate end_time: add 1 to 4 hours randomly
            end_dt = start_dt + timedelta(hours=random.randint(1, 4))
            end_str = end_dt.strftime('%Y-%m-%d %H:%M:%S')
            
            v_id = random.randint(1, NUM_EVENTS)
            o_id = random.randint(1, NUM_EVENTS)
            status = event_statuses[i]
            
            # Independently generate base_price between $20 and $300
            base_price = round(random.uniform(20.0, 300.0), 2)
            
            checkin_count = sum(1 for _, att, _ in event_reg_map[i] if att)
            total_regs = len(event_reg_map[i])
            
            # Compute planned budget based on base_price and expected attendance
            expected_attendance = max(10, int(total_regs * random.uniform(0.8, 1.5)))
            
            # Planned budget should be slightly less than expected revenue to allow for profit
            # e.g., cost is 60% to 85% of expected revenue
            expected_revenue = base_price * expected_attendance
            cost_ratio = random.uniform(0.60, 0.85)
            planned = round(expected_revenue * cost_ratio, 2)
            
            event_data[i] = {'planned': planned, 'checkin_count': checkin_count}
            
            f.write(f"INSERT INTO events (event_id, event_name, event_date, end_time, venue_id, status, base_price, organizer_id) "
                    f"VALUES ({i}, '{name}', '{start_str}', '{end_str}', {v_id}, '{status}', {base_price}, {o_id});\n")

        # 4.1 Sample data for Event Categories
        f.write("\n-- Data for Event Categories\n")
        for i in range(1, NUM_EVENTS + 1):
            num_cats = random.randint(1, 3)
            selected_cats = random.sample(range(1, len(categories) + 1), num_cats)
            for cat_id in selected_cats:
                f.write(f"INSERT INTO event_categories (event_id, category_id) VALUES ({i}, {cat_id});\n")

        # 4.2 Sample data for Event Finance
        # actual_cost = planned_budget × uniform(0.9, 1.1) — variance ±10%
        f.write("\n-- Data for Event Finances\n")
        for i in range(1, NUM_EVENTS + 1):
            planned = event_data[i]['planned']
            actual = round(planned * random.uniform(0.9, 1.1), 2)
            f.write(f"INSERT INTO event_finance (finance_id, event_id, planned_budget, actual_cost) VALUES ({i}, {i}, {planned}, {actual});\n")

        # 5. Sample data for Guests
        f.write("\n-- Data for Guests\n")
        for i in range(1, NUM_GUESTS + 1):
            name = escape_str(fake.name())
            email = escape_str(fake.unique.email())
            phone = fake.phone_number()[:16]
            f.write(f"INSERT INTO guests (guest_id, guest_name, guest_email, phone_number) VALUES ({i}, '{name}', '{email}', '{phone}');\n")

        # 6. Sample data for Registrations (from pre-calculated data)
        f.write("\n-- Data for Registrations\n")
        reg_id = 1
        for e_id in range(1, NUM_EVENTS + 1):
            for g_id, att_status, fb_rating in event_reg_map[e_id]:
                reg_date = fake.date_time_this_year().strftime('%Y-%m-%d %H:%M:%S')
                att_str = '1' if att_status else '0'
                f.write(f"INSERT INTO registrations (registration_id, event_id, guest_id, registration_date, attendance_status, feedback_rating) VALUES ({reg_id}, {e_id}, {g_id}, '{reg_date}', {att_str}, {fb_rating});\n")
                reg_id += 1

        # ============================================================
        # 7. RBAC: ROLES & PERMISSIONS
        # ============================================================
        f.write("\n-- Data for Permissions (RBAC)\n")
        permissions = [
            (1, 'manage_event', 'Create, update, delete events'),
            (2, 'view_public_events', 'View public event listings'),
            (3, 'manage_finance', 'Manage event finances'),
            (4, 'register_guests', 'Register guests for events'),
            (5, 'view_analytics', 'View reports and statistics'),
            (6, 'manage_users', 'Manage user accounts'),
            (7, 'attendance_checkin', 'Perform guest check-ins'),
        ]
        for pid, pname, pdesc in permissions:
            f.write(f"INSERT INTO permissions (permission_id, permission_name, description) VALUES ({pid}, '{pname}', '{escape_str(pdesc)}');\n")

        f.write("\n-- Data for Roles (RBAC)\n")
        roles = [
            (1, 'Admin'),
            (2, 'Staff'),
            (3, 'Guest'),
            (4, 'Organizer'),
        ]
        for rid, rname in roles:
            f.write(f"INSERT INTO roles (role_id, role_name) VALUES ({rid}, '{rname}');\n")

        f.write("\n-- Data for Role_Permissions (RBAC N-N)\n")
        role_perms = [
            # Admin: full access
            (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
            # Staff: event ops + check-in + view + register
            (2, 2), (2, 4), (2, 5), (2, 7),
            # Guest: view only
            (3, 2),
            # Organizer: manage_event, view_public_events, register_guests, view_analytics
            (4, 1), (4, 2), (4, 4),
        ]
        for rid, pid in role_perms:
            f.write(f"INSERT INTO role_permissions (role_id, permission_id) VALUES ({rid}, {pid});\n")

        # 8. RBAC: Users with bcrypt hashed passwords
        f.write("\n-- Data for Users (RBAC)\n")
        users = [
            (1, 'admin', 'admin123', 1, 'NULL'),
            (2, 'staff01', 'staff123', 2, 'NULL'),
            (3, 'organizer01', 'org123', 4, 'NULL'),
        ]
        # Add 5 Guest users
        for i in range(1, 6):
            users.append((3 + i, f'guest{i:02d}', 'guest123', 3, i))
            
        for uid, uname, raw_pw, rid, gid in users:
            hashed = bcrypt.hashpw(raw_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            f.write(f"INSERT INTO users (user_id, username, password_hash, role_id, guest_id) VALUES ({uid}, '{uname}', '{hashed}', {rid}, {gid});\n")

        # Re-enable foreign key checks
        f.write("\nSET FOREIGN_KEY_CHECKS = 1;\n")

    print(f"Successfully generated {NUM_EVENTS} events and {NUM_GUESTS} guests sample data in 'sql/seed.sql'.")

# ============================================================
# INSERTION SCRIPT
# ============================================================

def insert_seed_data(session):
    """Reads seed.sql and executes the statements in batches"""
    with open('sql/seed.sql', 'r', encoding='utf-8') as f:
        sql_commands = f.read().split(';')
    
    batch = []
    batch_size = 100
    for command in sql_commands:
        cmd = command.strip()
        if cmd:
            batch.append(cmd)
            if len(batch) >= batch_size:
                try:
                    for c in batch:
                        session.execute(text(c))
                    session.commit()
                except Exception as e:
                    session.rollback()
                    print(f"Error executing batch: {e}")
                batch = []
    
    # Commit remaining commands
    if batch:
        try:
            for c in batch:
                session.execute(text(c))
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error executing final batch: {e}")
    
    print("Seed data inserted into the database successfully.")