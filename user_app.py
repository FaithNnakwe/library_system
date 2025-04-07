import streamlit as st
import mysql.connector
from dbs_management import borrow_book

# Connect to the MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",  # replace with your MySQL username
    password="Faith0644",  # replace with your MySQL password
    database="library_db"
)

# Create a cursor to execute SQL queries
cursor = conn.cursor()

def show_books():
    cursor.execute("SELECT * FROM books LIMIT 10")
    books = cursor.fetchall()
    for book in books:
        st.write(f"Title: {book[1]}, Author: {book[2]}, link: {book[3]}, Genre: {book[4]}")


def borrow_book_ui():
    user_id = st.number_input("User ID", min_value=1)
    book_id = st.number_input("Book ID", min_value=1)
    due_date = st.date_input("Due Date")
    
    if st.button("Borrow Book"):
        borrow_book(user_id, book_id, due_date)
        st.success("Book borrowed successfully!")

# Display
show_books()
borrow_book_ui()
