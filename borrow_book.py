import streamlit as st
import mysql.connector
from datetime import datetime, timedelta

def get_borrow_count(book_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Faith0644",
        database="library_db"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM borrow_records WHERE id = %s", (book_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_user_position_in_line(book_id, user_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Faith0644",
        database="library_db"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id FROM borrow_records 
        WHERE id = %s 
        ORDER BY borrow_date ASC
    """, (book_id,))
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    if user_id in user_ids:
        return user_ids.index(user_id) + 1
    return len(user_ids) + 1

def get_user_borrowed_books_count(user_id):
    # Get the number of books a user has currently borrowed
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Faith0644",
        database="library_db"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM borrow_records WHERE user_id = %s AND return_status = FALSE", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def borrow_page():
    st.title("📖 Borrow Book")

    if 'user' not in st.session_state:
        st.warning("Please log in to borrow a book.")
        st.session_state.page = "login"
        st.rerun()
        return

    if 'selected_book_id' not in st.session_state:
        st.warning("No book selected.")
        st.session_state.page = "dashboard"
        st.rerun()
        return

    user_id = st.session_state.user["id"]
    book_id = st.session_state.selected_book_id

    # Fetch the number of books the user has already borrowed
    user_borrowed_count = get_user_borrowed_books_count(user_id)

    # Enforce the borrow limit (4 books)
    if user_borrowed_count >= 4:
        st.warning("You cannot borrow more than 4 books at a time.")
        if 'selected_book_id' in st.session_state:
            del st.session_state.selected_book_id  # <-- prevent re-rerunning into borrow_page
        st.session_state.page = "dashboard"
        st.rerun()
        return


    # Fetch book details
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Faith0644",
        database="library_db"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT title, author, bookshelf, link FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    conn.close()

    if not book:
        st.error("The selected book does not exist.")
        st.session_state.page = "dashboard"
        st.rerun()
        return

    title, author, genre, link = book
    st.write(f"**Title**: {title}")
    st.write(f"**Author**: {author}")
    st.write(f"**Genre**: {genre}")

    with st.form("borrow_form"):
        st.write("Please confirm to borrow the book.")
        st.text_input("Borrower's Name", value=st.session_state.user["name"], disabled=True)
        due_date = datetime.today() + timedelta(days=14)
        st.write(f"**Due Date:** {due_date.strftime('%B %d, %Y')}")
        confirm = st.form_submit_button("Confirm Borrow")

        if confirm:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Faith0644",
                database="library_db"
            )
            cursor = conn.cursor()

            # Insert borrow record
            cursor.execute("""
                INSERT INTO borrow_records (user_id, book_id, borrow_date, due_date) 
                VALUES (%s, %s, %s, %s)
            """, (user_id, book_id, datetime.now(), due_date))

            # Mark book as unavailable (optional logic, you can update based on borrow count)
            cursor.execute("""
                UPDATE books 
                SET available = FALSE
                WHERE id = %s
            """, (book_id,))

            conn.commit()
            conn.close()

            st.success(f"You've successfully borrowed **{title}** by {author}!")
            st.markdown(
    f'<a href="{link}" target="_blank">📘 Click here to open the book</a>',
    unsafe_allow_html=True 
)

    st.markdown("---")
    if st.button("🔙 Back to Dashboard"):
        st.session_state.page = "dashboard"
        del st.session_state.selected_book_id
        st.rerun()
