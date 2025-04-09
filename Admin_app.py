import streamlit as st
from dbs_management import add_book, edit_book, search_books, delete_book

def dashboard():
    st.title("📚 Library Book Catalog System")
    st.write("Welcome, Admin!")

    # Log out button
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.experimental_rerun()

    # Sidebar Navigation
    menu = st.sidebar.selectbox("Menu", ["Add Book", "Search Books", "Edit Book", "Delete Book"])

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
        st.subheader("Search for Books")
        search_query = st.text_input("Enter Title, Author, or Genre")

        if st.button("Search"):
            results = search_books(search_query)
            if results:
                for book in results:
                    st.write(f"📖 **{book[1]}** - {book[2]} ({book[3]}, {book[4]})")
            else:
                st.warning("No books found.")

    # Edit a Book
    elif menu == "Edit Book":
        st.subheader("Edit Book Details")
        book_id = st.number_input("Enter Book ID", min_value=1, step=1)
        new_title = st.text_input("New Title")
        new_author = st.text_input("New Author")
        new_genre = st.text_input("New Genre")

        if st.button("Update Book"):
            edit_book(new_title, new_author, new_genre, book_id)
            st.success("Book updated successfully!")

    # Delete a Book
    elif menu == "Delete Book":
        st.subheader("Delete a Book")
        book_id = st.number_input("Enter Book ID to Delete", min_value=1, step=1)

        if st.button("Delete"):
            delete_book(book_id)
            st.success("Book deleted successfully!")
