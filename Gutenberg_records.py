import pandas as pd
import mysql.connector

df = pd.read_csv('gutenberg_metadata.csv')
df['ID'] = df.index + 1  # Adding an ID column based on the index (starting from 1)
print(df.head())

import pandas as pd

# Replace NaN values with None for MySQL compatibility
df['Author'] = df['Author'].apply(lambda x: None if pd.isna(x) else x)
df['Bookshelf'] = df['Bookshelf'].apply(lambda x: None if pd.isna(x) else x)
df['Title'] = df['Title'].apply(lambda x: None if pd.isna(x) else x)

# Check if the NaN values are replaced with None
print(df.head())


# Load your DataFrame (you may already have it in the previous step)
# df = pd.read_csv("gutenberg_data.csv")

# MySQL connection details
conn = mysql.connector.connect(
    host="localhost",  # Update with your MySQL host
    user="root",  # Update with your MySQL username
    password="Faith0644",  # Update with your MySQL password
    database="library_db"  # The name of your database
)

cursor = conn.cursor()

# Create table if it doesn't exist already (run only once)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INT PRIMARY KEY,
        title VARCHAR(255),
        author VARCHAR(255),
        link TEXT,
        bookshelf VARCHAR(255)
    )
""")

# Insert data from DataFrame into MySQL
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO books (id, title, author, link, bookshelf)
        VALUES (%s, %s, %s, %s, %s)
    """, (row["ID"], row["Title"], row["Author"], row["Link"], row["Bookshelf"]))

# Commit and close connection
conn.commit()
cursor.close()
conn.close()

print("Data inserted successfully!")

