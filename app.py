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

# 📩 Gửi mã OTP qua email
def send_otp(email):
    otp = str(random.randint(100000, 999999))  # Tạo mã OTP ngẫu nhiên
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)

        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = email
        msg["Subject"] = "Mã OTP đăng nhập"

        body = f"Mã OTP của bạn là: {otp}"
        msg.attach(MIMEText(body, "plain", "utf-8"))

        server.sendmail(EMAIL_SENDER, email, msg.as_string())
        server.quit()

        # Lưu OTP vào session
        st.session_state["otp"] = otp
        st.session_state["login_email"] = email
        
        return True
    except Exception as e:
        st.error(f"Lỗi gửi email: {e}")
        return False

# ✅ Đặt lại mật khẩu
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

# ✅ **Kiểm tra nếu đã đăng nhập thì hiển thị trang chào mừng**
if "logged_in" in st.session_state and st.session_state["logged_in"]:
    st.markdown(f"<h2>🎉 Chào mừng {st.session_state['username']}!</h2>", unsafe_allow_html=True)
    st.write("Bạn đã đăng nhập thành công. Chúc bạn một ngày tốt lành! ☕😊")

    # Nút đăng xuất
    if st.button("🔓 Đăng xuất"):
        del st.session_state["logged_in"]
        del st.session_state["username"]
        st.rerun()

# ✅ **Quên mật khẩu**
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
                if reset_password(st.session_state["login_email"], new_password):
                    st.success("🔄 Mật khẩu đã được cập nhật! Hãy đăng nhập lại.")
                    del st.session_state["otp"]
                    del st.session_state["login_email"]
                else:
                    st.error("❌ Lỗi khi cập nhật mật khẩu!")
            else:
                st.error("🚫 Mã OTP không đúng!")

st.markdown("</div>", unsafe_allow_html=True)

init_db()
