# Borrow Book Details Page
import streamlit as st
import mysql.connector
from user_app import show_available_books

def borrow_book_page(book_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Faith0644",
        database="library_db"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    book = cursor.fetchone()
    conn.close()

    if book:
        title = book[1]
        author = book[2]
        genre = book[4]
        availability = "Available" if book[5] else "Not Available"

        st.subheader(f"📚 {title}")
        st.write(f"Author: {author}")
        st.write(f"Genre: {genre}")
        st.write(f"Availability: {availability}")

        if availability == "Available":
            user_id = st.number_input("Your User ID", min_value=1)
            due_date = st.date_input("Due Date")
            if st.button("Borrow Book"):
                # Update the database or session as needed (e.g., change availability)
                st.success("Book borrowed successfully!")
        else:
            st.warning("This book is currently not available for borrowing.")

# Main display function
def main():
    if "selected_book" in st.session_state and st.session_state.selected_book is not None:
        borrow_book_page(st.session_state.selected_book)
    else:
        show_available_books()

# Run the app
main()
