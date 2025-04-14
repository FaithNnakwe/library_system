use library_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Auto-incrementing ID
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255)
    role VARCHAR(100),
);

CREATE TABLE borrow_records (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Auto-incrementing ID
    user_id INT,  -- Foreign key referencing users(id)
    book_id INT,  -- Foreign key referencing books(id)
    borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp of when the book is borrowed
    due_date TIMESTAMP,  -- Due date for return
    return_status BOOLEAN DEFAULT FALSE,  -- Status of the book (whether it's returned or not)
    FOREIGN KEY (user_id) REFERENCES users(id),  -- Foreign key constraint for user_id
    FOREIGN KEY (book_id) REFERENCES books(id)   -- Foreign key constraint for book_id
);
