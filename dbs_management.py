import mysql.connector
import bcrypt
from datetime import datetime, timedelta

# Connect to the MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",  
    password="Faith0644",  
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
        user="root",
        password="Faith0644",  
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
        user="root",  
        password="Faith0644",  
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
        user="root",  
        password="Faith0644",  
        database="library_db"
    )
    cursor = conn.cursor()
    query = f"SELECT * FROM books WHERE bookshelf LIKE %s"
    cursor.execute(query, ('%' + bookshelf + '%',))  # Search for books in the bookshelf
    results = cursor.fetchall()
    conn.close()
    return results

# Search by Bookshelf
def search_books_by_id(book_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  
        password="Faith0644",  
        database="library_db"
    )
    cursor = conn.cursor()
    query = f"SELECT * FROM books WHERE id LIKE %s"
    cursor.execute(query, (book_id,))  # Search for books in the bookshelf
    results = cursor.fetchall()
    conn.close()
    return results

# Delete a Book
def delete_book(book_id):
    query = "DELETE FROM books WHERE id = %s"
    cursor.execute(query, (book_id,))
    conn.commit()

# Edit a Book
def edit_book(book_id, title, author, bookshelf):
    query = "UPDATE books SET title = %s, author = %s, bookshelf = %s WHERE id = %s"
    cursor.execute(query, (title, author, bookshelf, book_id))
    conn.commit()

def get_book_by_id(book_id):
    query = "SELECT title, author, bookshelf FROM books WHERE id = %s"
    cursor.execute(query, (book_id,))
    return cursor.fetchone()

def get_borrowed_books():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Faith0644",
        database="library_db"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.name, b.title, bb.due_date, bb.return_status
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
        SELECT b.id, b.title, b.link, b.author, bb.borrow_date, bb.due_date
        FROM borrow_records bb
        JOIN books b ON bb.book_id = b.id
        JOIN users u ON u.id = bb.user_id
        WHERE u.email = %s AND bb.return_status = FALSE
    """
    cursor.execute(query, (email,))
    results = cursor.fetchall()
    conn.close()
    return results


import mysql.connector

def extend_due_date(book_id, email):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Faith0644",
        database="library_db"
    )
    cursor = conn.cursor()

    update_query = """
        UPDATE borrow_records bb
        JOIN users u ON bb.user_id = u.id
        SET 
            bb.due_date = DATE_ADD(bb.due_date, INTERVAL 14 DAY),
            bb.extended = TRUE
        WHERE 
            bb.book_id = %s 
            AND u.email = %s 
            AND bb.return_status = FALSE 
            AND bb.extended = FALSE
    """

    cursor.execute(update_query, (book_id, email))
    conn.commit()
    
    success = cursor.rowcount > 0  # True if update happened, False if already extended or no matching record
    cursor.close()
    conn.close()
    return success

def close_connection():
    cursor.close()
    conn.close()


