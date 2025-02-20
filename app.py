import streamlit as st
import sqlite3
import bcrypt

# 🔥 Cập nhật đường dẫn ảnh nền
BACKGROUND_IMAGE = "https://raw.githubusercontent.com/nguyentrungkien11K/trung-kien-/main/banner1.jpg"

# 🎨 CSS để cải thiện giao diện + làm đậm chữ trong ô nhập liệu
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
            background-color: rgba(255, 255, 255, 0.2);
            border: 2px solid #ffd700;
            padding: 12px;
            color: white;
            font-weight: bold;  /* 🔥 Làm đậm chữ nhập vào */
            font-size: 18px;  /* 📌 Tăng kích thước chữ */
        }}
        .stTextInput>div>div>input::placeholder {{
            color: rgba(255, 255, 255, 0.6); /* 🌟 Làm chữ gợi ý mờ */
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

# 📌 Giao diện chọn chức năng
menu = ["Đăng nhập", "Đăng ký"]
choice = st.sidebar.selectbox("Chọn chức năng", menu)

# 🎨 Hộp đăng nhập
st.markdown("<div class='login-box'>", unsafe_allow_html=True)

if choice == "Đăng ký":
    st.markdown("<h2>📌 <strong>Đăng ký tài khoản</strong></h2>", unsafe_allow_html=True)
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
    st.markdown("<h2>🔓 <strong>Đăng nhập</strong></h2>", unsafe_allow_html=True)
    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")
    
    if st.button("Đăng nhập"):
        if login_user(username, password):
            st.success(f"✅ Đăng nhập thành công! Chào mừng {username}.")
        else:
            st.error("🚫 Sai tên đăng nhập hoặc mật khẩu.")

st.markdown("</div>", unsafe_allow_html=True)

init_db()
