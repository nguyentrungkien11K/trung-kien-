import streamlit as st
import sqlite3
import bcrypt
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 🔑 Cấu hình Email SMTP của bạn
EMAIL_SENDER = "trungkien08033@gmail.com"  # Thay bằng email của bạn
EMAIL_PASSWORD = "zrxgxxmjgtlixgfp"  # Thay bằng mật khẩu ứng dụng Gmail

# 🎨 CSS để làm đẹp giao diện
st.markdown(
    """
    <style>
        .login-box {
            background: rgba(0, 0, 0, 0.6);
            padding: 40px;
            border-radius: 10px;
            width: 400px;
            margin: auto;
            text-align: center;
            color: white;
        }
        .stTextInput>div>div>input {
            background-color: rgba(255, 255, 255, 0.9);
            border: 2px solid #ffd700;
            padding: 12px;
            color: black;
            font-weight: bold;
            font-size: 18px;
        }
        .stButton>button {
            background: linear-gradient(to right, #ff416c, #ff4b2b);
            color: white;
            font-size: 18px;
            padding: 12px;
            border-radius: 5px;
            width: 100%;
            border: none;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)

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
        hashed_pw = hash_password(password)  # Mã hóa mật khẩu trước khi lưu
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

# 📩 Gửi mã OTP qua email và lưu vào session
def send_otp(email):
    otp = str(random.randint(100000, 999999))  # Tạo mã OTP ngẫu nhiên
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)

        # Tạo email với UTF-8
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = email
        msg["Subject"] = "Mã OTP đặt lại mật khẩu"
        
        # Nội dung email
        body = f"Mã OTP của bạn là: {otp}"
        msg.attach(MIMEText(body, "plain", "utf-8"))  # Mã hóa nội dung email UTF-8

        # Gửi email
        server.sendmail(EMAIL_SENDER, email, msg.as_string())
        server.quit()

        # Lưu OTP vào session để kiểm tra sau này
        st.session_state["otp"] = otp
        st.session_state["reset_email"] = email
        
        return True
    except Exception as e:
        st.error(f"Lỗi gửi email: {e}")
        return False

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
        if send_otp(email):
            st.success("✅ Mã OTP đã được gửi! Kiểm tra email của bạn.")

    if "otp" in st.session_state:
        user_otp = st.text_input("Nhập mã OTP", key="otp_input")
        new_password = st.text_input("Nhập mật khẩu mới", type="password", key="new_password_reset")

        if st.button("Đặt lại mật khẩu"):
            if user_otp == st.session_state["otp"]:
                reset_password(st.session_state["reset_email"], new_password)
                st.success("🔄 Mật khẩu đã được cập nhật! Hãy đăng nhập lại.")
                del st.session_state["otp"]
                del st.session_state["reset_email"]
            else:
                st.error("🚫 Mã OTP không đúng!")

st.markdown("</div>", unsafe_allow_html=True)

init_db()
