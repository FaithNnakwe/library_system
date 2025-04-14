import streamlit as st
import mysql.connector
import hashlib
import Admin_app
import user_app

# MySQL connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Faith0644",
        database="library_db"
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Sign up
def sign_up():
    st.title("Sign Up")
    name = st.text_input("Name")
    sign_up_email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["user", "admin"])

    if st.button("Register"):
        if not name or not sign_up_email or not password or not role:
            st.error("Please fill in all fields.")
        else:
            hashed_pw = hash_password(password)

            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)", 
                           (name, sign_up_email, hashed_pw, role))
                conn.commit()
                conn.close()
                st.success("Registration successful. Please login.")
            except mysql.connector.errors.IntegrityError:
                st.error("Email already exists.")

# Login
def login(role="main"):
    st.title("Login")
    login_email = st.text_input("Email", key=f"login_email_{role}")
    password = st.text_input("Password", type="password", key=f"login_password_{role}")

    if st.button("Login", key=f"login_button_{role}"):
        if not login_email or not password:
            st.error("Please fill in all fields.")
        else: 
            hashed_pw = hash_password(password)
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (login_email, hashed_pw))
            user_data = cursor.fetchone()
            conn.close()

            if user_data:
                st.session_state.logged_in = True
                st.session_state.user = user_data
                st.success(f"Welcome {user_data['name']} ({user_data['role']})")
                st.rerun()  # Trigger a rerun to update the app flow
            else:
                st.error("Invalid email or password.")

# Route after login
def main_app():
    role = st.session_state.user["role"]
    if role == "admin":
        Admin_app.dashboard()  # call admin function
    else:
        user_app.dashboard()   # call user function

# App flow
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

st.sidebar.title("Navigation")
if st.session_state.logged_in:
    main_app()
else:
    page = st.sidebar.radio("Go to", ["Login", "Sign Up"])
    if page == "Login":
        login()
    else:
        sign_up()
