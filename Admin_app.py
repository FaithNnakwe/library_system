import streamlit as st
from dbs_management import add_book, edit_book, search_books_by_title, search_books_by_bookshelf, search_books_by_author, delete_book, get_borrowed_books, get_book_by_id
from user_app import search_books_menu,display_search_results
import pandas as pd
import mysql.connector

def dashboard():
    st.title("📚 Library Book Catalog System")
    st.write("Welcome, Admin!")

    # Log out button
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    # Sidebar Navigation
    menu = st.sidebar.selectbox("Menu", ["Add Book", "Search Books", "Edit Book", "Delete Book", "Borrowed Books","User Borrow History"])

    # Add a Book
    if menu == "Add Book":
        st.subheader("Add a New Book")
        title = st.text_input("Title")
        author = st.text_input("Author")
        bookshelf = st.text_input("Genre")

        if st.button("Add Book"):
            if title and author and bookshelf:
                add_book(title, author, bookshelf)
                st.success("Book added successfully!")
            else:
                st.error("Please fill in all fields.")

    # Search Books
    elif menu == "Search Books":
        search_books_menu()

    # Edit a Book
    elif menu == "Edit Book":
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
    elif menu == "Delete Book":
        st.subheader("Delete a Book")
        book_id = st.number_input("Enter Book ID to Delete", min_value=1, step=1)

        if st.button("Delete"):
            delete_book(book_id)
            st.success("Book deleted successfully!")
    
    elif menu == "Borrowed Books":
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
    elif menu == "User Borrow History":
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


    
    conn.close()

