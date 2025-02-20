import sqlite3
import bcrypt
import smtplib
import random
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 🔑 Cấu hình Email SMTP của bạn
EMAIL_SENDER = "trungkien08033@gmail.com"  # Thay bằng email của bạn
EMAIL_PASSWORD = "zrxgxxmjgtlixgfp"  # Thay bằng mật khẩu ứng dụng Gmail

# 🔑 Kết nối Database
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE,
                 email TEXT UNIQUE,
                 password TEXT)''')
    conn.commit()
    conn.close()

# 🔑 Hash mật khẩu
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# 🔓 Kiểm tra mật khẩu
def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# 📌 Đăng ký tài khoản
def register_user(username, email, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        hashed_pw = hash_password(password)
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_pw))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# 🚪 Đăng nhập tài khoản
def login_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT email, password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user:
        email, stored_hashed_password = user
        if check_password(password, stored_hashed_password):
            return email  # Trả về email nếu mật khẩu đúng
    return None  # Sai mật khẩu hoặc tài khoản không tồn tại

# 📌 Giao diện chọn chức năng
menu = ["Đăng nhập", "Đăng ký", "Quên mật khẩu"]
choice = st.sidebar.selectbox("Chọn chức năng", menu)

st.markdown("<div class='login-box'>", unsafe_allow_html=True)

# ✅ **Đăng ký tài khoản**
if choice == "Đăng ký":
    st.markdown("<h2>📌 <strong>Đăng ký tài khoản</strong></h2>", unsafe_allow_html=True)
    new_user = st.text_input("Tên đăng nhập")
    email = st.text_input("Email")
    new_password = st.text_input("Mật khẩu", type="password")
    
    if st.button("Đăng ký"):
        if new_user and email and new_password:
            if register_user(new_user, email, new_password):
                st.success("🎉 Đăng ký thành công! Hãy đăng nhập.")
            else:
                st.error("⚠️ Tên đăng nhập hoặc email đã tồn tại! Hãy thử lại.")
        else:
            st.warning("⚠️ Vui lòng nhập đầy đủ thông tin.")

# ✅ **Đăng nhập**
elif choice == "Đăng nhập":
    st.markdown("<h2>🔓 <strong>Đăng nhập</strong></h2>", unsafe_allow_html=True)
    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")
    
    if st.button("Đăng nhập"):
        email = login_user(username, password)
        if email:
            st.success(f"✅ Đăng nhập thành công! Chào mừng {username}.")
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
        else:
            st.error("🚫 Sai tên đăng nhập hoặc mật khẩu.")

st.markdown("</div>", unsafe_allow_html=True)

init_db()
