import streamlit as st
import mysql.connector
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import borrow_book
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Faith0644",
        database="library_db"
    )

def get_user_borrowed_book_ids(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT book_id FROM borrow_records 
        WHERE user_id = %s AND return_status = FALSE
    """, (user_id,))
    book_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return book_ids

def get_books_dataframe():
    conn = get_connection()
    query = "SELECT id, title, author, bookshelf AS genre FROM books"
    books_df = pd.read_sql(query, conn)
    conn.close()
    return books_df

def generate_recommendations(user_id, top_n=10):
    borrowed_ids = get_user_borrowed_book_ids(user_id)
    if not borrowed_ids:
        return pd.DataFrame()  # No recommendations if user hasn't borrowed

    books_df = get_books_dataframe()
    books_df["description"] = (
        books_df["title"].fillna("") + " " +
        books_df["author"].fillna("") + " " +
        books_df["genre"].fillna("")
    )

    # Vectorize descriptions
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(books_df["description"])

    # Aggregate similarities across all borrowed books
    indices = books_df[books_df["id"].isin(borrowed_ids)].index
    user_profile_vector = tfidf_matrix[indices].mean(axis=0).A
    cosine_similarities = cosine_similarity(user_profile_vector, tfidf_matrix).flatten()

    # Sort and filter out already borrowed books
    books_df["similarity"] = cosine_similarities
    filtered_books = books_df[~books_df["id"].isin(borrowed_ids)]
    unique_recommendations = ( filtered_books
    .sort_values(by="similarity", ascending=False)
    .drop_duplicates(subset=["title"])
    .head(top_n)
      )
    return unique_recommendations

def show_recommendations():
    st.subheader("🔮 Book Recommendations for You")

    if "user" not in st.session_state:
        st.info("Please log in to see recommendations.")
        return

    user_id = st.session_state.user["id"]
    recs = generate_recommendations(user_id)

    if recs.empty:
        st.info("Borrow some books to start getting recommendations!")
    else:
        for _, row in recs.iterrows():
            with st.container():
                st.markdown(f"### 📘 {row['title']}")
                st.markdown(f"**Author:** *{row['author']}*  \n**Genre:** {row['genre']}")
                if st.button(f"📥 Borrow this Book", key=f"borrow_{row['id']}"):
                    st.session_state.selected_book_id = row["id"]
                    st.session_state.page = "borrow"
                    st.rerun()
                st.markdown("---")
