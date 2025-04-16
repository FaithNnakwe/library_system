import streamlit as st
import mysql.connector
from dbs_management import search_books_by_author, search_books_by_bookshelf, search_books_by_title
from dbs_management import get_user_borrowed_books, extend_due_date, search_books_by_id
from PIL import Image, ImageDraw, ImageFont
import borrow_book
import random
from textwrap import wrap
from login import log_in
import recommendations


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

def set_gradient_background():
    st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #1a1a2e, #16213e);  
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
    if 'user' not in st.session_state or not st.session_state.get('logged_in', False):
        st.warning("🚫 Please log in to access the dashboard.")
        st.session_state.page = "login"
        st.rerun()
        return

   
    if st.session_state.page == "borrow" and st.session_state.get("selected_book_id"):
        print("✅ Navigating to borrow_page with book ID:", st.session_state.selected_book_id)
        borrow_book.borrow_page()
        return
    
    
    if st.session_state.page == "my_account":
        borrow_book.user_account_page()
        return

    if 'current_menu' not in st.session_state:
        st.session_state.current_menu = "Search Books"  # default view

    set_gradient_background()
    st.title("📚 User Dashboard")

    # Navigation Buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🔍 Search Books", key="Search1"):
            st.session_state.current_menu = "Search Books"
            st.rerun()
    with col2:
        if st.button("📖 View Borrowed"):
            st.session_state.current_menu = "View Borrowed Books"
            st.rerun()
    with col3:
        if st.button("✨ Recommendations"):
            st.session_state.current_menu = "Recommendations"
            st.rerun()
    with col4:
        if st.button("👤 My Account"):
            st.session_state.page = "my_account"
            st.rerun()


    st.write(f"Welcome, {st.session_state.user['name']}!")

    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.page = "login"
        st.rerun()

    

    if st.session_state.current_menu == "Search Books":
        search_books_menu()
        st.subheader("📖 Available Books")
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Faith0644",
            database="library_db"
        )
        cursor = conn.cursor()
        show_available_books()
        conn.close()

    elif st.session_state.current_menu == "View Borrowed Books":
        view_borrowed_books_menu()
        if st.button("🔙 Return to Dashboard"):
            st.session_state.current_menu = "Search Books"
            st.rerun()

    elif st.session_state.current_menu == "Recommendations":
        recommendations.show_recommendations()
        if st.button("🔙 Return to Dashboard"):
            st.session_state.current_menu = "Search Books"
            st.rerun()

    st.markdown("""
    <style>
    .streamlit-expander {
        background-color: black !important;
        color: white !important;
        border-radius: 10px;
        padding: 10px;
    }
    .streamlit-expanderHeader {
        background-color: #111 !important;
        color: white !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)



# Search Books Function
def search_books_menu():
    st.subheader("Search for Books")

    # Create four different search inputs
    title_search = st.text_input("Enter Title")
    author_search = st.text_input("Enter Author")
    bookshelf_search = st.text_input("Enter Bookshelf")
    Bookid_search = st.text_input("Enter Book ID")

    # Create a button to trigger the search
    if st.button("Search", key="Search2"):
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
        elif Bookid_search:
            results = search_books_by_id(Bookid_search)
            display_search_results(results)
        else:
            st.warning("Please enter at least one search term.")
            return
        
        st.session_state.search_results = results  
        st.session_state.search_triggered = True   
        st.rerun()  # Trigger rerun to display results outside the button context

      # Show previous search results after rerun
    if st.session_state.get("search_triggered", False):
        results = st.session_state.get("search_results", [])
        display_search_results(results)


def display_search_results(results):
    if results:
        cols = st.columns(5)  # Create columns layout for displaying books
        for idx, book in enumerate(results):
            if len(book) >= 5:
                title, author, genre, book_id = book[1], book[2], book[4], book[0]
                display_book_image(title, author, genre, book_id, idx, cols)
    else:
        st.warning("No books found.")

def view_borrowed_books_menu():
    borrow_email = st.session_state.user['email']
    borrowed_books = get_user_borrowed_books(borrow_email)

    st.subheader("📚 Your Borrowed Books")
    st.markdown("#### Users are allowed 4 books at a time.")
    if 'feedback' in st.session_state:
        st.success(st.session_state.feedback)
        del st.session_state.feedback

    if not borrowed_books:
        st.info("You have no borrowed books.")
        return

    for book in borrowed_books:
        with st.expander(f"{book['title']} by {book['author']}"):
            st.write(f"**Link:** {book['link']}")
            st.write(f"**Borrowed On:** {book['borrow_date']}")
            st.write(f"**Due Date:** {book['due_date']}")
            st.write(f"**Book ID:** {book['id']}")

            # Return book button
            if st.button(f"Return '{book['title']}'", key=book['id']):
                return_borrowed_book(book['id'], borrow_email)
                st.session_state.feedback = f"You returned '{book['title']}' successfully."
                st.rerun()

            # Extend due date logic
            if book.get('extended'):
                st.warning("📅 Due date already extended.")
            else:
                if st.button(f"Extend Due Date for '{book['title']}'", key=f"extend_{book['id']}"):
                    success = extend_due_date(book['id'], borrow_email)
                    if success:
                        st.session_state.feedback = f"Due date for '{book['title']}' has been extended by 14 days."
                    else:
                        st.session_state.feedback = f"Due date extension for '{book['title']}' failed. Extension already used."
                    st.rerun()



@st.cache_data
def get_random_books():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Faith0644",
        database="library_db"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE bookshelf IS NOT NULL ORDER BY RAND()")
    books = cursor.fetchall()
    conn.close()
    return books

def return_borrowed_book(book_id, email):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Faith0644",
        database="library_db"
    )
    cursor = conn.cursor()

    # 1. Mark borrow record as returned
    update_query = """
        UPDATE borrow_records bb
        JOIN users u ON bb.user_id = u.id
        SET bb.return_status = TRUE
        WHERE bb.book_id = %s AND u.email = %s AND bb.return_status = FALSE
    """
    cursor.execute(update_query, (book_id, email))

    # 2. Check active borrow count
    cursor.execute("""
        SELECT COUNT(*) FROM borrow_records
        WHERE book_id = %s AND return_status = FALSE
    """, (book_id,))
    active_borrow_count = cursor.fetchone()[0]

    # 3. If less than 2, update availability
    if active_borrow_count < 2:
        cursor.execute("UPDATE books SET available = TRUE WHERE id = %s", (book_id,))

        # 4. Mark first person in hold queue as notified
        cursor.execute("""
            SELECT id FROM holds
            WHERE book_id = %s AND notified = FALSE
            ORDER BY hold_date ASC
            LIMIT 1
        """, (book_id,))
        first_hold = cursor.fetchone()
        if first_hold:
            hold_id = first_hold[0]
            cursor.execute("UPDATE holds SET notified = TRUE WHERE id = %s", (hold_id,))
            st.success("✅ First user in the hold queue marked as notified.")

    conn.commit()
    conn.close()




# Available Books Function
def show_available_books():
    st.subheader("Available Books")

    # Initialize the number of books to show
    if 'books_shown' not in st.session_state:
        st.session_state.books_shown = 10  # Show 5 books initially
    books = get_random_books()

    # Display books based on the current count
    cols = st.columns(5)
    for idx, book in enumerate(books[:st.session_state.books_shown]):
        title, author, genre, book_id = book[1], book[2], book[4], book[0]
        display_book_image(title, author, genre, book_id, idx,cols)

    # Add a "Load More" button if there are more books
    if st.session_state.books_shown < len(books):
        if st.button("Load More"):
            st.session_state.books_shown += 5  


# Book Display Function
def display_book_image(title, author, genre, book_id, idx, cols):
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
        st.image(img, caption=f"Genre: {genre} Book ID: {book_id}")
         # Show Borrow button only if the user is NOT an admin
        if st.session_state.get("user") and st.session_state.user.get("role") != "admin":
            if st.button(f"Borrow", key=f"borrow_{book_id}"):
                st.session_state.selected_book_id = book_id
                st.session_state.page = "borrow"
                print(f"Page state changed to: {st.session_state.page}")  # Debugging output
                st.rerun()

def main():
    # Ensure that a page is set in session state
    if 'page' not in st.session_state:
        st.session_state.page = 'login'  # Default to login page

    if st.session_state.page == 'dashboard':
        dashboard()
    elif st.session_state.page == 'borrow':
        borrow_book.borrow_page()
    elif st.session_state.page == 'login':
        log_in

main()