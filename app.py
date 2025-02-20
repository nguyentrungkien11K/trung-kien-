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

# 🚪 Đăng nhập tài khoản (Bước 1: Kiểm tra mật khẩu)
def login_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT email, password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user:
        email, stored_hashed_password = user
        if check_password(password, stored_hashed_password):
            return email  # Trả về email nếu mật khẩu đúng (Tiếp tục bước 2: Gửi OTP)
    
    return None  # Sai mật khẩu hoặc tài khoản không tồn tại

# 📩 Gửi mã OTP qua email
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
        msg["Subject"] = "Mã OTP đăng nhập"
        
        # Nội dung email
        body = f"Mã OTP của bạn là: {otp}"
        msg.attach(MIMEText(body, "plain", "utf-8"))  # Mã hóa nội dung email UTF-8

        # Gửi email
        server.sendmail(EMAIL_SENDER, email, msg.as_string())
        server.quit()

        # Lưu OTP vào session
        st.session_state["otp"] = otp
        st.session_state["login_email"] = email
        
        return True
    except Exception as e:
        st.error(f"Lỗi gửi email: {e}")
        return False

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
        email = login_user(username, password)
        if email:
            if send_otp(email):
                st.success("✅ Mã OTP đã được gửi! Vui lòng kiểm tra email.")
                st.session_state["username"] = username  # Lưu username vào session
        else:
            st.error("🚫 Sai tên đăng nhập hoặc mật khẩu.")

    if "otp" in st.session_state:
        user_otp = st.text_input("Nhập mã OTP", key="otp_login")

        if st.button("Xác nhận OTP"):
            if user_otp == st.session_state["otp"]:
                st.success(f"🎉 Đăng nhập thành công! Chào mừng {st.session_state['username']}.")

                # Xóa OTP sau khi đăng nhập thành công
                del st.session_state["otp"]
                del st.session_state["login_email"]
                del st.session_state["username"]
            else:
                st.error("🚫 Mã OTP không đúng!")

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
                reset_password(st.session_state["login_email"], new_password)
                st.success("🔄 Mật khẩu đã được cập nhật! Hãy đăng nhập lại.")
                del st.session_state["otp"]
                del st.session_state["login_email"]
            else:
                st.error("🚫 Mã OTP không đúng!")

st.markdown("</div>", unsafe_allow_html=True)

init_db()
