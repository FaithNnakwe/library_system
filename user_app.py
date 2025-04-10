import streamlit as st
import mysql.connector
from dbs_management import borrow_book
from PIL import Image, ImageDraw, ImageFont
import random
from textwrap import wrap


# Font settings (optional: adjust based on your OS)
title_font = ImageFont.truetype("arial.ttf", 17)
author_font = ImageFont.truetype("arial.ttf", 13)

# Random pastel color generator
def random_pastel_color():
    return tuple(random.randint(150, 255) for _ in range(3))


genre_icons = {
    "Drama": "🎭",
    "Sci-Fi": "🚀",
    "Historical": "🏰",
    "Fantasy": "🐉",
    "Mystery": "🕵️",
    "Romance": "❤️",
    "Non-Fiction": "📘"
}
def get_text_size(text, font):
    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height

def wrap_text(text, font, max_width):
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


# Dashboard function to call from main.py
def dashboard():
    st.title("📚 User Dashboard")
    st.write("Welcome, Book Lover!")

    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

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
    cursor.execute("SELECT * FROM books WHERE bookshelf != 'None' ORDER BY RAND() LIMIT 10;")
    books = cursor.fetchall()

    cols = st.columns(5)  # Adjust the number '3' for how many books to show in each row
    for  idx, book in enumerate(books):
        title = book[1]
        author = book[2]
        genre = book[4]
        icon = genre_icons.get(genre, "📚")

    # Create book cover image
        bg_color = random_pastel_color()
        img = Image.new("RGB", (250, 250), color=bg_color)
        draw = ImageDraw.Draw(img)

    # Draw genre icon
        draw.text((200, 20), icon, font=author_font, fill="black")

    # Wrap and draw title text with shadow
        title_lines = wrap_text(title, title_font, 210)  # wrap to fit width
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
        col_idx = idx % 5  # Make sure images are assigned to columns in a row
        with cols[col_idx]:
    # Display the generated image in Streamlit
            st.image(img, caption=f"Genre: {genre}")
        if (idx + 1) % 5 == 0 and idx != len(books) - 1:
            cols = st.columns(5)


    # Borrow Book Form
    st.subheader("📚 Borrow a Book")
    user_id = st.number_input("Your User ID", min_value=1)
    book_id = st.number_input("Book ID to Borrow", min_value=1)
    due_date = st.date_input("Due Date")

    if st.button("Borrow Book"):
        borrow_book(user_id, book_id, due_date)
        st.success("Book borrowed successfully!")

    conn.close()

