import streamlit as st
import sqlite3
import bcrypt
import smtplib
import random

# 🔥 Cập nhật đường dẫn ảnh nền
BACKGROUND_IMAGE = "https://raw.githubusercontent.com/nguyentrungkien11K/trung-kien-/main/banner1.jpg"

# 🔑 Cấu hình email gửi mã OTP (sử dụng Gmail)
EMAIL_SENDER = "your-email@gmail.com"  # Thay bằng email của bạn
EMAIL_PASSWORD = "your-email-password"  # Thay bằng mật khẩu ứng dụng

# 🎨 CSS để cải thiện giao diện + làm chữ nhập liệu màu đen
st.markdown(
    f"""
    <style>
        body {{
            background-size: cover;
            background-position: center;
            font-family: Arial, sans-serif;
        }}
        .login-box {{
            background: rgba(0, 0, 0, 0.6);
            padding: 40px;
            border-radius: 10px;
            width: 400px;
            margin: auto;
            text-align: center;
            color: white;
        }}
        .stTextInput>div>div>input {{
            background-color: rgba(255, 255, 255, 0.9);
            border: 2px solid #ffd700;
            padding: 12px;
            color: black;  
            font-weight: bold;
            font-size: 18px;
        }}
        .stTextInput>div>div>input::placeholder {{
            color: rgba(0, 0, 0, 0.6); 
            font-weight: normal;
        }}
        .stButton>button {{
            background: linear-gradient(to right, #ff416c, #ff4b2b);
            color: white;
            font-size: 18px;
            padding: 12px;
            border-radius: 5px;
            width: 100%;
            border: none;
            font-weight: bold;
        }}
        h2 {{
            color: #ffd700;
            font-weight: bold !important;
            text-align: center;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# 🔑 Tiêu đề chính
st.markdown("<h1 style='text-align: center; color: white;'>🔐 Đăng nhập & Đăng ký</h1>", unsafe_allow_html=True)

# 🗄️ Kết nối CSDL SQLite
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
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if user and check_password(password, user[0]):
        return True
    return False

# 📩 Gửi mã OTP qua email
def send_otp(email):
    otp = str(random.randint(100000, 999999))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        message = f"Subject: Mã OTP đặt lại mật khẩu\n\nMã OTP của bạn là: {otp}"
        server.sendmail(EMAIL_SENDER, email, message)
        server.quit()
        return otp
    except Exception as e:
        st.error(f"Lỗi gửi email: {e}")
        return None

# 🔄 Đặt lại mật khẩu
def reset_password(email, new_password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    hashed_pw = hash_password(new_password)
    c.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_pw, email))
    conn.commit()
    conn.close()
    return True

# 📌 Giao diện chọn chức năng
menu = ["Đăng nhập", "Đăng ký", "Quên mật khẩu"]
choice = st.sidebar.selectbox("Chọn chức năng", menu)

# 🎨 Hộp đăng nhập
st.markdown("<div class='login-box'>", unsafe_allow_html=True)

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

elif choice == "Đăng nhập":
    st.markdown("<h2>🔓 <strong>Đăng nhập</strong></h2>", unsafe_allow_html=True)
    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")
    
    if st.button("Đăng nhập"):
        if login_user(username, password):
            st.success(f"✅ Đăng nhập thành công! Chào mừng {username}.")
        else:
            st.error("🚫 Sai tên đăng nhập hoặc mật khẩu.")

elif choice == "Quên mật khẩu":
    st.markdown("<h2>🔄 <strong>Quên mật khẩu</strong></h2>", unsafe_allow_html=True)
    email = st.text_input("Nhập email của bạn")
    
    if st.button("Gửi mã OTP"):
        otp = send_otp(email)
        if otp:
            user_otp = st.text_input("Nhập mã OTP")
            new_password = st.text_input("Nhập mật khẩu mới", type="password")

            if st.button("Đặt lại mật khẩu"):
                if user_otp == otp:
                    reset_password(email, new_password)
                    st.success("🔄 Mật khẩu đã được cập nhật! Hãy đăng nhập lại.")
                else:
                    st.error("🚫 Mã OTP không đúng!")

st.markdown("</div>", unsafe_allow_html=True)

init_db()
