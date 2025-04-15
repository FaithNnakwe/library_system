import streamlit as st
from dbs_management import add_book, edit_book, search_books_by_title, search_books_by_bookshelf, search_books_by_author, delete_book, get_borrowed_books, get_book_by_id
from user_app import search_books_menu,display_search_results
import pandas as pd
import mysql.connector

def set_gradient_background():
    st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #1a1a2e, #16213e);  /* dark academic vibe */
    }

    /* Times New Roman for all text */
    html, body, [class*="css"] {
        font-family: 'Times New Roman', Times, serif;
    }

    /* Library-themed button style */
    .stButton>button {
        border: none;
        background-color: #6b4226;  /* warm brown like leather-bound books */
        color: #fffbe6;             /* soft parchment-like white */
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



def dashboard():
    set_gradient_background() 
    st.title("📚 Library Book Catalog System")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        if st.button("Add Book", key="Add_button1"):
            st.session_state.current_menu = "Add Book"
            st.rerun()

    with col2:
        if st.button("Search Books"):
            st.session_state.current_menu = "Search Books"
            st.rerun()

    with col3:
        if st.button("Edit Book"):
            st.session_state.current_menu = "Edit Book"
            st.rerun()
        
    with col4:
        if st.button("Delete Book"):
            st.session_state.current_menu = "Delete Book"
            st.rerun()

    with col5:
        if st.button("Borrowed Books"):
            st.session_state.current_menu = "Borrowed Books"
            st.rerun()

    with col6:
        if st.button("User Borrow History"):
            st.session_state.current_menu = "User Borrow History"
            st.rerun()



    st.write("Welcome, Admin!")

    # Log out button
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    
    if "current_menu" not in st.session_state:
        st.session_state.current_menu = "Add Book" 

    # Add a Book
    if st.session_state.current_menu == "Add Book":
        st.subheader("Add a New Book")
        title = st.text_input("Title")
        author = st.text_input("Author")
        bookshelf = st.text_input("Genre")

        if st.button("Add Book",key="Add_button2"):
            if title and author and bookshelf:
                add_book(title, author, bookshelf)
                st.success("Book added successfully!")
            else:
                st.error("Please fill in all fields.")

    # Search Books
    elif st.session_state.current_menu == "Search Books":
        search_books_menu()

    # Edit a Book
    elif st.session_state.current_menu == "Edit Book":
        st.subheader("Edit Book Details")
        book_id = st.number_input("Enter Book ID", min_value=1, step=1)

        if st.button("Fetch Book"):
            book = get_book_by_id(book_id)
            if book:
                current_title, current_author, current_genre = book
                st.session_state['edit_book_loaded'] = True
                st.session_state['book_details'] = {
                'title': current_title,
                'author': current_author,
                'genre': current_genre
            }
            else:
                st.warning("Book not found.")

        if st.session_state.get('edit_book_loaded', False):
            st.text("Leave blank to keep current value")
            new_title = st.text_input("New Title", value=st.session_state['book_details']['title'])
            new_author = st.text_input("New Author", value=st.session_state['book_details']['author'])
            new_genre = st.text_input("New Genre", value=st.session_state['book_details']['genre'])

            if st.button("Update Book"):
            # Keep original values if fields are left empty
                final_title = new_title if new_title.strip() else st.session_state['book_details']['title']
                final_author = new_author if new_author.strip() else st.session_state['book_details']['author']
                final_genre = new_genre if new_genre.strip() else st.session_state['book_details']['genre']

                edit_book(book_id, final_title, final_author, final_genre)
                st.success("Book updated successfully!")
                st.session_state['edit_book_loaded'] = False

    # Delete a Book
    elif st.session_state.current_menu == "Delete Book":
        st.subheader("Delete a Book")
        book_id = st.number_input("Enter Book ID to Delete", min_value=1, step=1)

        if st.button("Delete"):
            delete_book(book_id)
            st.success("Book deleted successfully!")
    
    elif st.session_state.current_menu == "Borrowed Books":
        st.subheader("Borrowed Book Records")
        borrowed = get_borrowed_books()

        if borrowed:
    # Create a DataFrame for cleaner formatting
            df = pd.DataFrame(borrowed, columns=["User", "Book Title", "Due Date", "Returned"])
            # Optional: Map return status for clearer display
            df["Returned"] = df["Returned"].map({
            0: "📕 Borrowed",
            1: "✅ Returned"
            })
            st.table(df)
        else:
            st.info("No books currently borrowed.")

    elif st.session_state.current_menu == "User Borrow History":
        admin_user_search()

def admin_user_search():
    st.title("🔍 Search User Borrow History")

    # Admin check
    if 'user' not in st.session_state or st.session_state.user.get("role") != "admin":
        st.warning("Admin access only.")
        st.session_state.page = "login"
        st.rerun()
        return

    # Search method
    search_option = st.selectbox("Search by", ["Email", "User ID", "Name"])

    conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Faith0644",
                database="library_db"
            )
    cursor = conn.cursor(dictionary=True)

    # User lookup logic
    user = None
    if search_option == "Email":
        search_email = st.text_input("Enter User Email", key='borrow_email')
        if search_email:
            cursor.execute("SELECT id, name FROM users WHERE email = %s", (search_email,))
            user = cursor.fetchone()

    elif search_option == "User ID":
        user_id = st.text_input("Enter User ID", type="number")
        if user_id:
            cursor.execute("SELECT id, name FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()

    elif search_option == "Name":
        name = st.text_input("Enter Full or Partial Name")
        if name:
            cursor.execute("SELECT id, name FROM users WHERE name LIKE %s", (f"%{name}%",))
            users = cursor.fetchall()

            if users:
                selected_user = st.selectbox("Select a user", [f"{u['id']} - {u['name']}" for u in users])
                selected_id = int(selected_user.split(" - ")[0])
                cursor.execute("SELECT id, name FROM users WHERE id = %s", (selected_id,))
                user = cursor.fetchone()
            else:
                st.error("No users found with that name.")

    # If a user was found, fetch their borrowing history
    if user:
        st.write(f"**User found:** {user['name']} (ID: {user['id']})")

        cursor.execute("""
            SELECT b.title, br.borrow_date, br.due_date, br.return_status
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            WHERE br.user_id = %s
        """, (user['id'],))

        borrow_history = cursor.fetchall()

        if borrow_history:
            st.write("**Borrowing History:**")
            for record in borrow_history:
                return_status = "Returned" if record['return_status'] else "Not Returned"
                st.write(f"**Title**: {record['title']}")
                st.write(f"**Borrowed On**: {record['borrow_date']}")
                st.write(f"**Due Date**: {record['due_date']}")
                st.write(f"**Return Status**: {return_status}")
                st.markdown("---")
        else:
            st.info("This user has no borrowing history.")



