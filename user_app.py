import streamlit as st
import mysql.connector
from dbs_management import borrow_book

# Dashboard function to call from main.py
def dashboard():
    st.title("📚 User Dashboard")
    st.write("Welcome, Book Lover!")

    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.experimental_rerun()

    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  # replace with your MySQL username
        password="Faith0644",  # replace with your MySQL password
        database="library_db"
    )
    cursor = conn.cursor()

    # Show available books
    st.subheader("📖 Available Books")
    cursor.execute("SELECT * FROM books LIMIT 10")
    books = cursor.fetchall()
    for book in books:
        st.write(f"**Title:** {book[1]} | **Author:** {book[2]} | **Genre:** {book[4]}")

    # Borrow Book Form
    st.subheader("📚 Borrow a Book")
    user_id = st.number_input("Your User ID", min_value=1)
    book_id = st.number_input("Book ID to Borrow", min_value=1)
    due_date = st.date_input("Due Date")

    if st.button("Borrow Book"):
        borrow_book(user_id, book_id, due_date)
        st.success("Book borrowed successfully!")

    conn.close()
