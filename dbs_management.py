import mysql.connector
import bcrypt

# Connect to the MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",  # replace with your MySQL username
    password="Faith0644",  # replace with your MySQL password
    database="library_db"
)

# Create a cursor to execute SQL queries
cursor = conn.cursor()


def add_book(title, author, bookshelf):
    query = "INSERT INTO books (title, author, bookshelf) VALUES (%s, %s, %s)"
    cursor.execute(query, (title, author, bookshelf))
    conn.commit()

def return_book(record_id):
    query = "UPDATE borrow_records SET return_status = TRUE WHERE id = %s"
    cursor.execute(query, (record_id,))
    conn.commit()

def get_borrow_history(user_id):
    query = "SELECT * FROM borrow_records WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    borrow_history = cursor.fetchall()
    return borrow_history

# Search by Title
def search_books_by_title(title):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  # replace with your MySQL username
        password="Faith0644",  # replace with your MySQL password
        database="library_db"
    )
    cursor = conn.cursor()
    query = f"SELECT * FROM books WHERE title LIKE %s"
    cursor.execute(query, ('%' + title + '%',))  # Search for books with the title
    results = cursor.fetchall()
    conn.close()
    return results

# Search by Author
def search_books_by_author(author):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  # replace with your MySQL username
        password="Faith0644",  # replace with your MySQL password
        database="library_db"
    )
    cursor = conn.cursor()
    query = f"SELECT * FROM books WHERE author LIKE %s"
    cursor.execute(query, ('%' + author + '%',))  # Search for books by the author
    results = cursor.fetchall()
    conn.close()
    return results

# Search by Bookshelf
def search_books_by_bookshelf(bookshelf):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  # replace with your MySQL username
        password="Faith0644",  # replace with your MySQL password
        database="library_db"
    )
    cursor = conn.cursor()
    query = f"SELECT * FROM books WHERE bookshelf LIKE %s"
    cursor.execute(query, ('%' + bookshelf + '%',))  # Search for books in the bookshelf
    results = cursor.fetchall()
    conn.close()
    return results
   

# Delete a Book
def delete_book(book_id):
    query = "DELETE FROM books WHERE id = %s"
    cursor.execute(query, (book_id,))
    conn.commit()

# Edit a Book
def edit_book(book_id, title, author, bookshelf,):
    query = "UPDATE books SET title = %s, author = %s, bookshelf = %s  WHERE id = %s"
    cursor.execute(query, (title, author, bookshelf, book_id))
    conn.commit()

def get_borrowed_books():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Faith0644",
        database="library_db"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.name, b.title, bb.due_date
        FROM borrow_records bb
        JOIN users u ON bb.user_id = u.id
        JOIN books b ON bb.book_id = b.id
    """)
    results = cursor.fetchall()
    conn.close()
    return results

def get_user_borrowed_books(email):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Faith0644",
        database="library_db"
    )
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT b.id, b.title, b.author, bb.borrow_date, bb.due_date
        FROM borrowed_books bb
        JOIN books b ON bb.book_id = b.id
        JOIN users u ON u.id = bb.user_id
        WHERE u.email = %s AND bb.returned = FALSE
    """
    cursor.execute(query, (email,))
    results = cursor.fetchall()
    conn.close()
    return results

def return_borrowed_book(book_id, email):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Faith0644",
        database="library_db"
    )
    cursor = conn.cursor()
    update_query = """
        UPDATE borrowed_books bb
        JOIN users u ON bb.user_id = u.id
        SET bb.return_status = TRUE
        WHERE bb.book_id = %s AND u.email = %s
    """
    cursor.execute(update_query, (book_id, email))
    conn.commit()
    conn.close()


def close_connection():
    cursor.close()
    conn.close()


