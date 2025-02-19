import os
import streamlit as st
import sqlite3
import bcrypt
import smtplib
import random
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 📨 Thông tin SMTP (Cập nhật đúng tài khoản Gmail)
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "your_email@gmail.com")  # Lấy từ biến môi trường
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_email_password")  # Không lưu plaintext
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# 🔥 Link ảnh nền
BACKGROUND_IMAGE = "https://raw.githubusercontent.com/nguyentrungkien11K/trung-kien-/main/banner1.jpg"

# 🎨 CSS giao diện
st.markdown(
    f"""
    <style>
        body {{
            background-image: url('{BACKGROUND_IMAGE}');
            background-size: cover;
            background-position: center;
        }}
        .login-box {{
            background: rgba(0, 0, 0, 0.8);
            padding: 40px;
            border-radius: 10px;
            width: 400px;
            margin: auto;
            text-align: center;
            color: white;
        }}
        .stTextInput>div>div>input {{
            background-color: rgba(255, 255, 255, 0.2);
            border: 2px solid #ffd700;
            padding: 10px;
            color: white;
        }}
        .stButton>button {{
            background: linear-gradient(to right, #ff416c, #ff4b2b);
            color: white;
            font-size: 18px;
            padding: 12px;
            border-radius: 5px;
            width: 100%;
            border: none;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# 🔑 Kết nối SQLite
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             username TEXT UNIQUE,
             password TEXT,
             email TEXT UNIQUE,
             otp TEXT,
             otp_time REAL)''')
conn.commit()

# 🔑 Hash mật khẩu
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# 🔓 Kiểm tra mật khẩu
def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# 📧 Gửi OTP qua email
def send_otp(to_email, username, otp):
    subject = "Mã xác nhận OTP đăng nhập"
    body = f"Xin chào {username},\n\nMã OTP của bạn là: {otp}\nMã này có hiệu lực trong 5 phút.\n\nTrân trọng,\nĐội ngũ phát triển."
    
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Lỗi gửi OTP:", e)
        return False

# 📌 Đăng ký tài khoản
def register_user(username, password, email):
    try:
        hashed_pw = hash_password(password)
        c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, hashed_pw, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# 🚪 Đăng nhập & tạo OTP
def login_user(username, password):
    c.execute("SELECT password, email FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    
    if user and check_password(password, user[0]):
        otp = str(random.randint(100000, 999999))
        otp_time = time.time()
        
        c.execute("UPDATE users SET otp = ?, otp_time = ? WHERE username = ?", (otp, otp_time, username))
        conn.commit()
        
        if send_otp(user[1], username, otp):
            return True
    return False

# 🕒 Xác thực OTP
def verify_otp(username, entered_otp):
    c.execute("SELECT otp, otp_time FROM users WHERE username = ?", (username,))
    data = c.fetchone()
    
    if data:
        stored_otp, otp_time = data
        if stored_otp == entered_otp and time.time() - otp_time <= 300:
            return True
    return False

# 📌 Giao diện chọn chức năng
menu = ["Đăng nhập", "Đăng ký"]
choice = st.sidebar.selectbox("Chọn chức năng", menu)

st.markdown("<div class='login-box'>", unsafe_allow_html=True)

if choice == "Đăng ký":
    st.markdown("<h2 style='color: #ffd700;'>📌 Đăng ký tài khoản</h2>", unsafe_allow_html=True)
    new_user = st.text_input("Tên đăng nhập")
    new_email = st.text_input("Email")
    new_password = st.text_input("Mật khẩu", type="password")
    
    if st.button("Đăng ký"):
        if new_user and new_email and new_password:
            if register_user(new_user, new_password, new_email):
                st.success("🎉 Đăng ký thành công! Hãy đăng nhập.")
            else:
                st.error("⚠️ Tên đăng nhập hoặc email đã tồn tại!")
        else:
            st.warning("⚠️ Vui lòng nhập đầy đủ thông tin.")

elif choice == "Đăng nhập":
    st.markdown("<h2 style='color: #ffd700;'>🔓 Đăng nhập</h2>", unsafe_allow_html=True)
    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")
    
    if st.button("Gửi mã OTP"):
        if login_user(username, password):
            st.session_state["otp_username"] = username
            st.session_state["otp_step"] = True
            st.success("📩 Mã OTP đã gửi đến email của bạn.")
        else:
            st.error("🚫 Sai tên đăng nhập hoặc mật khẩu.")
    
    if "otp_step" in st.session_state:
        otp_code = st.text_input("Nhập mã OTP")
        if st.button("Xác nhận OTP"):
            if verify_otp(st.session_state["otp_username"], otp_code):
                st.success(f"✅ Đăng nhập thành công! Chào mừng {st.session_state['otp_username']}.")
            else:
                st.error("🚫 Mã OTP không hợp lệ hoặc đã hết hạn!")

st.markdown("</div>", unsafe_allow_html=True)
