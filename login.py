import streamlit as st
import mysql.connector
import hashlib
import Admin_app
import user_app
from streamlit.errors import StreamlitAPIException

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

def set_gradient_background():
    st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
    }

     /* Apply Times New Roman to everything */
    html, body, [class*="css"] {
        font-family: 'Times New Roman', Times, serif;
    }

    .stButton>button {
        border: none
        background-color: #6b4226;  /* warm brown like leather-bound books */
        color: #fffbe6; 
        font-family: 'Times New Roman', Times, serif;
        padding: 0.6em 1.2em;
        border-radius: 8px;
        font-weight: bold;
        transition: background-color 0.3s ease, transform 0.2s;

    }

    .stButton>button:hover {
        background-color: #8b5e3c;  /* slightly lighter brown */
        transform: scale(1.03);
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sign up
def sign_up():
    set_gradient_background()  # or set_background_color(), etc
    st.title("Sign Up")
    
    name = st.text_input("Name")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password")
    
    # Hidden admin code input for advanced users
    admin_code_input = st.text_input("Admin Code (leave blank if you're signing up as a user)", type="password")
    
    # Set role based on admin code
    ADMIN_SECRET_CODE = "my_super_secret_code_123"  # Change this to your own secret
    role = "admin" if admin_code_input == ADMIN_SECRET_CODE else "user"

    if st.button("Register"):
        if not name or not email or not password:
            st.error("Please fill in all fields.")
        else:
            hashed_pw = hash_password(password)

            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)", 
                               (name, email, hashed_pw, role))
                conn.commit()
                conn.close()
                st.success(f"Registration successful as a {role}. Please login.")
            except mysql.connector.errors.IntegrityError:
                st.error("Email already exists.")


# Login
def log_in():
    set_gradient_background()  # or set_background_color(), etc
    st.title("Login")
    email = st.text_input("Email", key=f"login_email2")
    password = st.text_input("Password", type="password", key=f"login_password2")

    if st.button("Login", key=f"login_button1"):
        if not email or not password:
            st.error("Please fill in all fields.")
        else: 
            hashed_pw = hash_password(password)
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, hashed_pw))
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
    try:
        page = st.sidebar.radio("Go to", ["Login", "Sign Up"], key="login_signup_radio_unique")
        
        if page == "Login":
            log_in()
        else:
            sign_up()
    except  StreamlitAPIException as e:
        pass
