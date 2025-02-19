import sqlite3
import streamlit as st

conn = sqlite3.connect("users.db")
c = conn.cursor()

c.execute("SELECT * FROM users")
rows = c.fetchall()

st.write("📌 Dữ liệu trong bảng users:")
for row in rows:
    st.write(row)

conn.close()
