import bcrypt
from sqlalchemy import text
import streamlit as st

# ============================================================
# PASSWORD HASHING & VERIFICATION
# ============================================================

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# ============================================================
# USER AUTHENTICATION
# ============================================================

def authenticate_user(session, username, password):
    query = text("""
        SELECT u.user_id, u.password_hash, r.role_name, p.permission_name, u.guest_id
        FROM users u
        JOIN roles r ON u.role_id = r.role_id
        JOIN role_permissions rp ON r.role_id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.permission_id
        WHERE u.username = :username
    """)

    result = session.execute(query, {"username": username}).fetchall()

    if result:
        stored_hash = result[0][1]
        # Verify password
        if verify_password(password, stored_hash):
            user_data = {
                "user_id": result[0][0],
                "role": result[0][2],
                "guest_id": result[0][4],
                "permissions": [row[3] for row in result] # List of permission_names
            }
            return user_data
    return None

# ============================================================
# REGISTRATION
# ============================================================

def register_new_guest_user(session, username, password, name, email, phone):
    try:
        # Check if username exists
        check_query = text("SELECT COUNT(*) FROM users WHERE username = :username")
        if session.execute(check_query, {"username": username}).scalar() > 0:
            return False, "Username already exists!"
            
        # 1. Insert into guests
        insert_guest = text("""
            INSERT INTO guests (guest_name, guest_email, phone_number)
            VALUES (:name, :email, :phone)
        """)
        session.execute(insert_guest, {"name": name, "email": email, "phone": phone})
        
        # Get guest_id
        guest_id = session.execute(text("SELECT LAST_INSERT_ID()")).scalar()
        
        # 2. Insert into users
        hashed_pw = hash_password(password)
        insert_user = text("""
            INSERT INTO users (username, password_hash, role_id, guest_id)
            VALUES (:username, :password_hash, 3, :guest_id)
        """)
        session.execute(insert_user, {
            "username": username,
            "password_hash": hashed_pw,
            "guest_id": guest_id
        })
        
        session.commit()
        return True, "Registration successful! Please login."
    except Exception as e:
        session.rollback()
        return False, f"System error: {str(e)}"

# ============================================================
# AUTHORIZATION (RBAC)
# ============================================================

def has_permission(permission_name):
    if 'user_info' not in st.session_state or st.session_state.user_info is None:
        return False
    return permission_name in st.session_state.user_info['permissions']
