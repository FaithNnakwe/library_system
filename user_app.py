import streamlit as st
import mysql.connector
from dbs_management import borrow_book, search_books, search_books_by_author, search_books_by_bookshelf, search_books_by_title
from PIL import Image, ImageDraw, ImageFont
import random
from textwrap import wrap

# Font settings (adjust based on your OS)
title_font = ImageFont.truetype("arial.ttf", 17)
author_font = ImageFont.truetype("arial.ttf", 13)

# Utility Functions
def random_pastel_color():
    """Generate a random pastel color."""
    return tuple(random.randint(150, 255) for _ in range(3))

def get_text_size(text, font):
    """Get the width and height of the text for wrapping."""
    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def wrap_text(text, font, max_width):
    """Wrap text to fit within the specified width."""
    lines = []
    words = text.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        width, _ = get_text_size(test_line, font)
        if width <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)
    return lines

# Dashboard Function
def dashboard():
    st.title("📚 User Dashboard")
    st.write("Welcome, Book Lover!")

    # Log Out Button
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    # Sidebar Menu
    menu = st.sidebar.selectbox("Menu", ["Search Books", "View Borrowed Books"])

    # Menu Actions
    if menu == "Search Books":
        search_books_menu()

    if menu == "View Borrowed Books":
        view_borrowed_books_menu()

    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  # replace with your MySQL username
        password="Faith0644",  # replace with your MySQL password
        database="library_db"
    )
    cursor = conn.cursor()

    # Available Books Section
    st.subheader("📖 Available Books")
    show_available_books(cursor)

    # Close connection
    conn.close()

# Search Books Function
def search_books_menu():
    st.subheader("Search for Books")

    # Create three different search inputs
    title_search = st.text_input("Enter Title")
    author_search = st.text_input("Enter Author")
    bookshelf_search = st.text_input("Enter Bookshelf")

    # Create a button to trigger the search
    if st.button("Search"):
        # Determine which search term is provided and call the appropriate search function
        if title_search:
            results = search_books_by_title(title_search)
            display_search_results(results)
        elif author_search:
            results = search_books_by_author(author_search)
            display_search_results(results)
        elif bookshelf_search:
            results = search_books_by_bookshelf(bookshelf_search)
            display_search_results(results)
        else:
            st.warning("Please enter at least one search term.")


def display_search_results(results):
    if results:
        cols = st.columns(5)  # Create columns layout for displaying books
        for idx, book in enumerate(results):
            if len(book) >= 5:
                title, author, genre = book[1], book[2], book[4]
                display_book_image(title, author, genre, idx, cols)
    else:
        st.warning("No books found.")

# View Borrowed Books Function
def view_borrowed_books_menu():
    st.subheader("View Borrowed Books")
    # This section would fetch and display borrowed books from the database
    pass

# Available Books Function
def show_available_books(cursor):
    st.subheader("Available Books")

    # Initialize the number of books to show
    if 'books_shown' not in st.session_state:
        st.session_state.books_shown = 10  # Show 5 books initially

    # Connect to the database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  # your MySQL username
        password="Faith0644",  # your MySQL password
        database="library_db"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE bookshelf IS NOT NULL ORDER BY RAND()")
    books = cursor.fetchall()
    conn.close()

    # Display books based on the current count
    cols = st.columns(5)
    for idx, book in enumerate(books[:st.session_state.books_shown]):
        title, author, genre, book_id = book[1], book[2], book[4], book[0]
        display_book_image(title, author, genre, idx,cols)

    # Add a "Load More" button if there are more books
    if st.session_state.books_shown < len(books):
        if st.button("Load More"):
            st.session_state.books_shown += 5  # Load 5 more books


# Book Display Function
def display_book_image(title, author, genre, idx, cols):
    bg_color = random_pastel_color()
    img = Image.new("RGB", (250, 250), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Wrap and draw title text with shadow
    title_lines = wrap_text(title, title_font, 210)
    y_text = 100
    for line in title_lines:
        draw.text((21, y_text + 1), line, font=title_font, fill="gray")  # shadow
        draw.text((20, y_text), line, font=title_font, fill="black")
        y_text += 25

    # Draw author with shadow
    author_lines = wrap_text(f"by {author}", author_font, 190)
    for line in author_lines:
        draw.text((21, y_text + 1), f"by {author}", font=author_font, fill="lightgray")
        draw.text((20, y_text), f"by {author}", font=author_font, fill="darkblue")
        y_text += 20

    # Use the correct column to display the image (side by side)
    col_idx = idx % 5  # Ensure images are placed correctly in a row
    with cols[col_idx]:
        st.image(img, caption=f"Genre: {genre}")
