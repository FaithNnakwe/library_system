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


def register_user(name, email, password):
    # Hash the password before storing
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
    cursor.execute(query, (name, email, hashed_password))
    conn.commit()

def login_user(email, password):
    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
        print("Login successful!")
        return user
    else:
        print("Invalid credentials!")
        return None


def add_book(title, author, bookshelf):
    query = "INSERT INTO books (title, author, bookshelf) VALUES (%s, %s, %s)"
    cursor.execute(query, (title, author, bookshelf))
    conn.commit()

def borrow_book(user_id, book_id, due_date):
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    user_exists = cursor.fetchone()

    # Check if book exists
    cursor.execute("SELECT id FROM books WHERE id = %s", (book_id,))
    book_exists = cursor.fetchone()

    if user_exists and book_exists:
        query = "INSERT INTO borrow_records (user_id, book_id, due_date) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_id, book_id, due_date))
        conn.commit()
    else:
        print("User or Book does not exist.")


def return_book(record_id):
    query = "UPDATE borrow_records SET return_status = TRUE WHERE id = %s"
    cursor.execute(query, (record_id,))
    conn.commit()

def get_borrow_history(user_id):
    query = "SELECT * FROM borrow_records WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    borrow_history = cursor.fetchall()
    return borrow_history

def search_books(search_term):
    # SQL query to search for books based on title, author, or bookshelf
    query = """
    SELECT id, title, author, link, bookshelf 
    FROM books 
    WHERE title LIKE %s OR author LIKE %s OR bookshelf LIKE %s
    """
    
    # Apply the LIKE pattern to the search term (case-insensitive)
    like_pattern = f"%{search_term}%"
    
    # Execute the query with the search term applied to all fields (title, author, bookshelf)
    cursor.execute(query, (like_pattern, like_pattern, like_pattern))
    
    # Fetch all matching results
    results = cursor.fetchall()
    
    # If results are found, return them; otherwise, return an empty list
    if results:
        return results
    else:
        return []  # Return an empty list if no books match the search

    

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


def close_connection():
    cursor.close()
    conn.close()


