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
    cursor.execute("SELECT COUNT(*) FROM borrow_records WHERE book_id = %s AND return_status = FALSE", (book_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_user_borrowed_books_count(user_id):
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

def get_hold_position(user_id, book_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Faith0644",
        database="library_db"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id FROM holds 
        WHERE book_id = %s ORDER BY hold_date ASC
    """, (book_id,))
    queue = cursor.fetchall()
    conn.close()
    return [u[0] for u in queue].index(user_id) + 1 if (user_id,) in queue else None

def set_gradient_background():
    st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #1a1a2e, #16213e);;
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
    
def borrow_page():
    set_gradient_background()
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

    user_borrowed_count = get_user_borrowed_books_count(user_id)

    if user_borrowed_count >= 4:
        st.warning("You cannot borrow more than 4 books at a time.")
        del st.session_state.selected_book_id 
        st.session_state.page = "dashboard"
        st.rerun()
        return

    borrow_count = get_borrow_count(book_id)

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

    if borrow_count < 2:
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
                cursor.execute("""
                    INSERT INTO borrow_records (user_id, book_id, borrow_date, due_date, return_status) 
                    VALUES (%s, %s, %s, %s, FALSE)
                """, (user_id, book_id, datetime.now(), due_date))

                cursor.execute("SELECT COUNT(*) FROM borrow_records WHERE book_id = %s AND return_status = FALSE", (book_id,))
                new_borrow_count = cursor.fetchone()[0]
                if new_borrow_count >= 2:
                    cursor.execute("UPDATE books SET available = FALSE WHERE id = %s", (book_id,))
                conn.commit()
                conn.close()

                st.success(f"You've successfully borrowed **{title}** by {author}!")
                st.markdown(f'<a href="{link}" target="_blank">📘 Click here to open the book</a>', unsafe_allow_html=True)

    else:
        st.warning("This book is not availably right now.")

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Faith0644",
            database="library_db"
        )
        cursor = conn.cursor()
        # Check if user already has a hold
        cursor.execute("SELECT COUNT(*) FROM holds WHERE user_id = %s AND book_id = %s", (user_id, book_id))
        already_held = cursor.fetchone()[0] > 0

        if not already_held:
            if st.button("📌 Place Hold"):
                cursor.execute("INSERT INTO holds (user_id, book_id, hold_date) VALUES (%s, %s, %s)", (user_id, book_id, datetime.now()))
                 # Update availability since borrow count already >= 2
                cursor.execute("""
                UPDATE books SET available = FALSE WHERE id = %s
            """, (book_id,))
                
                conn.commit()
                st.success("Hold placed successfully!")
        else:
            position = get_hold_position(user_id, book_id)
            st.info(f"You already have a hold on this book. Your position in line is: **{position}**")

        conn.close()

    st.markdown("---")
    if st.button("🔙 Back to Dashboard"):
        del st.session_state.selected_book_id
        st.session_state.page = "dashboard"
        st.rerun()

def user_account_page():
    set_gradient_background()
    st.title("📚 My Library Activity")

    if 'user' not in st.session_state:
        st.warning("Please log in to view your account.")
        st.session_state.page = "login"
        st.rerun()
        return

    user_id = st.session_state.user["id"]

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Faith0644",
        database="library_db"
    )
    cursor = conn.cursor()

    # --- Borrowing History ---
    st.subheader("📖 Borrowing History")
    cursor.execute("""
        SELECT b.title, b.author, br.borrow_date, br.due_date, br.return_status
        FROM borrow_records br
        JOIN books b ON br.book_id = b.id
        WHERE br.user_id = %s
        ORDER BY br.borrow_date DESC
    """, (user_id,))
    records = cursor.fetchall()

    if records:
        for title, author, borrow_date, due_date, returned in records:
            st.subheader(f"**Title**: {title} ")
            st.write(f"**Author**: {author}")
            st.write(f"**Borrowed on**: {borrow_date.strftime('%B %d, %Y')}")
            st.write(f"**Due**: {due_date.strftime('%B %d, %Y')} ")
            st.write(f"**Returned**: {"✅ Yes" if returned else "❌ No"}")
    else:
        st.info("You haven't borrowed any books yet.")

    # --- Holds List ---
    st.subheader("📌 Books on Hold")
    cursor.execute("""
        SELECT h.book_id, b.title, b.author, h.hold_date, h.notified
        FROM holds h
        JOIN books b ON h.book_id = b.id
        WHERE h.user_id = %s
        ORDER BY h.hold_date ASC
    """, (user_id,))
    holds = cursor.fetchall()

    if holds:
        for book_id, title, author, hold_date, notified in holds:
            # Fetch position in queue
            cursor.execute("""
                SELECT user_id FROM holds
                WHERE book_id = %s
                ORDER BY hold_date ASC
            """, (book_id,))
            queue = cursor.fetchall()
            position = [u[0] for u in queue].index(user_id) + 1

            position_display = "📬 Book Available" if notified else f"#{position}"

            st.markdown(f"**Title**: {title} ")
            st.write(f"**Author**: {author}")
            st.write(f"**Placed on**: {hold_date.strftime('%B %d, %Y')}")
            st.write(f"**Your position in queue**: **#{position_display}** ---")
    else:
        st.info("You haven't placed any holds yet.")

    conn.close()

    if st.button("🔙 Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
