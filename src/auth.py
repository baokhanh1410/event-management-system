import bcrypt
from sqlalchemy import text
import streamlit as st

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def authenticate_user(session, username, password):
    query = text("""
        SELECT u.user_id, u.password_hash, r.role_name, p.permission_name
        FROM users u
        JOIN roles r ON u.role_id = r.role_id
        JOIN role_permission rp ON r.role_id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.permission_id
        WHERE u.username = :username
    """)

    result = session.execute(query, {"username": username}).fetchall()

    if result:
        stored_hash = result[0][1]
        # Kiểm tra mật khẩu
        if verify_password(password, stored_hash):
            user_data = {
                "user_id": result[0][0],
                "role": result[0][2],
                "permissions": [row[3] for row in result] # Danh sách các permission_name
            }
            return user_data
    return None

def has_permission(permission_name):
    if 'user_info' not in st.session_state or st.session_state.user_info is None:
        return False
    return permission_name in st.session_state.user_info['permissions']
