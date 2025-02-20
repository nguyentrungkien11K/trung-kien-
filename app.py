import streamlit as st
import sqlite3
import bcrypt
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# 🔑 Email SMTP Configuration
EMAIL_SENDER = "trungkien08033@gmail.com"
EMAIL_PASSWORD = "zrxgxxmjgtlixgfp"

# 🔑 Database Connection
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

# 🔑 Hash Password
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# 🔓 Verify Password
def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# 🔄 Reset Password
def reset_password(email, new_password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    hashed_pw = hash_password(new_password)
    c.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_pw, email))
    conn.commit()
    conn.close()

# 📌 Register User
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

# 🚪 Login User
def login_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT email, password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user:
        email, stored_hashed_password = user
        if check_password(password, stored_hashed_password):
            return email
    return None

# 📩 Send OTP via Email
def send_otp(email):
    otp = str(random.randint(100000, 999999))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)

        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = email
        msg["Subject"] = "Login OTP Code"

        body = f"Your OTP code is: {otp}"
        msg.attach(MIMEText(body, "plain", "utf-8"))

        server.sendmail(EMAIL_SENDER, email, msg.as_string())
        server.quit()

        # Store OTP in session
        st.session_state["otp"] = otp
        st.session_state["login_email"] = email
        
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

# 📌 Navigation Menu
menu = ["Login", "Register", "Forgot Password"]
choice = st.sidebar.selectbox("Select Option", menu)

st.markdown("<div class='login-box'>", unsafe_allow_html=True)

# ✅ **Welcome Screen if Logged In**
if "logged_in" in st.session_state and st.session_state["logged_in"]:
    st.markdown(f"<h2>🎉 Welcome, {st.session_state['username']}!</h2>", unsafe_allow_html=True)
    st.write("You have successfully logged in. Have a great day! ☕😊")

    if st.button("🔓 Logout"):
        del st.session_state["logged_in"]
        del st.session_state["username"]
        st.rerun()

# ✅ **Register Form**
elif choice == "Register":
    st.markdown("<h2>📌 <strong>Register Account</strong></h2>", unsafe_allow_html=True)
    new_user = st.text_input("Username")
    email = st.text_input("Email")
    new_password = st.text_input("Password", type="password")
    
    if st.button("Register"):
        if new_user and email and new_password:
            if register_user(new_user, email, new_password):
                st.success("🎉 Registration successful! Please log in.")
            else:
                st.error("⚠️ Username or email already exists! Please try again.")
        else:
            st.warning("⚠️ Please fill in all fields.")

# ✅ **Login Form**
elif choice == "Login":
    st.markdown("<h2>🔓 <strong>Login</strong></h2>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        email = login_user(username, password)
        if email:
            if send_otp(email):
                st.success("✅ OTP has been sent! Please check your email.")
                st.session_state["pending_username"] = username
        else:
            st.error("🚫 Incorrect username or password.")

    if "otp" in st.session_state:
        user_otp = st.text_input("Enter OTP", key="otp_login")

        if st.button("Verify OTP"):
            if user_otp == st.session_state["otp"]:
                st.success(f"🎉 Login successful! Welcome, {st.session_state['pending_username']}.")

                st.session_state["logged_in"] = True
                st.session_state["username"] = st.session_state["pending_username"]

                del st.session_state["otp"]
                del st.session_state["login_email"]
                del st.session_state["pending_username"]
                
                st.rerun()
            else:
                st.error("🚫 Incorrect OTP!")

# ✅ **Forgot Password**
elif choice == "Forgot Password":
    st.markdown("<h2>🔄 <strong>Forgot Password</strong></h2>", unsafe_allow_html=True)
    email = st.text_input("Enter your email")
    
    if st.button("Send OTP"):
        if send_otp(email):
            st.success("✅ OTP has been sent! Please check your email.")

    if "otp" in st.session_state:
        user_otp = st.text_input("Enter OTP", key="otp_input")
        new_password = st.text_input("Enter new password", type="password", key="new_password_reset")

        if st.button("Reset Password"):
            if user_otp == st.session_state["otp"]:
                if "login_email" in st.session_state and st.session_state["login_email"]:
                    reset_password(st.session_state["login_email"], new_password)
                    st.success("🔄 Password updated successfully! Please log in again.")
                    del st.session_state["otp"]
                    del st.session_state["login_email"]
                else:
                    st.error("🚫 Email not found for password reset!")
            else:
                st.error("🚫 Incorrect OTP!")

st.markdown("</div>", unsafe_allow_html=True)

init_db()
