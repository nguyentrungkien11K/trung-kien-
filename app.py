import streamlit as st
import sqlite3
import bcrypt

# Link ảnh nền trên GitHub (sau khi tải lên, thay đường dẫn đúng vào đây)
BACKGROUND_IMAGE = "https://raw.githubusercontent.com/tên_tài_khoản/trung-kien-/main/background.jpg"

# CSS để tạo giao diện giống mẫu
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
            padding: 30px;
            border-radius: 10px;
            width: 350px;
            margin: auto;
            color: white;
            text-align: center;
        }}
        .stTextInput>div>div>input {{
            background-color: #fff;
            border: 2px solid #ffcc00;
            padding: 10px;
        }}
        .stButton>button {{
            background-color: #ffcc00;
            color: black;
            font-size: 18px;
            padding: 10px 20px;
            border-radius: 5px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Tiêu đề chính
st.markdown("<h1 style='text-align: center; color: white;'>🔐 Đăng nhập & Đăng ký</h1>", unsafe_allow_html=True)

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

# Hàm đăng ký & đăng nhập
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

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

def login_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if user and check_password(password, user[0]):
        return True
    return False

menu = ["Đăng nhập", "Đăng ký"]
choice = st.sidebar.selectbox("Chọn chức năng", menu)

st.markdown("<div class='login-box'>", unsafe_allow_html=True)

if choice == "Đăng ký":
    st.markdown("<h2 style='color: #ffcc00;'>📌 Đăng ký tài khoản</h2>", unsafe_allow_html=True)
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
    st.markdown("<h2 style='color: #ffcc00;'>🔓 Đăng nhập</h2>", unsafe_allow_html=True)
    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")
    
    if st.button("Đăng nhập"):
        if login_user(username, password):
            st.success(f"✅ Đăng nhập thành công! Chào mừng {username}.")
        else:
            st.error("🚫 Sai tên đăng nhập hoặc mật khẩu.")

st.markdown("</div>", unsafe_allow_html=True)

init_db()

