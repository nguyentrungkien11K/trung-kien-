import streamlit as st
import sqlite3
import bcrypt

# Kết nối SQLite
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE,
                 password TEXT)''')
    conn.commit()
    conn.close()

# Hàm tạo mật khẩu hash
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Hàm kiểm tra mật khẩu
def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# Hàm đăng ký tài khoản
def register_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        hashed_pw = hash_password(password)
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# Hàm kiểm tra thông tin đăng nhập
def login_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if user and check_password(password, user[0]):
        return True
    return False

# Giao diện Streamlit
st.title("🔐 Đăng nhập & Đăng ký với Streamlit")

menu = ["Đăng nhập", "Đăng ký"]
choice = st.sidebar.selectbox("Chọn chức năng", menu)

if choice == "Đăng ký":
    st.subheader("🔑 Đăng ký tài khoản")
    new_user = st.text_input("Tên đăng nhập")
    new_password = st.text_input("Mật khẩu", type="password")
    
    if st.button("Đăng ký"):
        if new_user and new_password:
            if register_user(new_user, new_password):
                st.success("🎉 Đăng ký thành công! Hãy đăng nhập.")
            else:
                st.error("⚠️ Tên đăng nhập đã tồn tại! Hãy thử tên khác.")
        else:
            st.warning("⚠️ Vui lòng nhập đầy đủ thông tin.")

elif choice == "Đăng nhập":
    st.subheader("🔓 Đăng nhập")
    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")
    
    if st.button("Đăng nhập"):
        if login_user(username, password):
            st.success(f"✅ Đăng nhập thành công! Chào mừng {username}.")
        else:
            st.error("🚫 Sai tên đăng nhập hoặc mật khẩu.")

# Khởi tạo database khi chạy ứng dụng
init_db()
