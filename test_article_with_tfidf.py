from dotenv import load_dotenv
import streamlit as st
import os
from sqlalchemy import create_engine, text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


load_dotenv()

db_user = "root"
db_password = "root"
db_host = "localhost"
db_name = "book_recommender"

connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
engine = create_engine(connection_string)

def execute_sql_query(sql):
    with engine.connect() as connection:
        result = connection.execute(text(sql))
        rows = result.fetchall()
        return rows

st.set_page_config(page_title="Book Recommender")
st.header("Book Recommender")

question = st.text_input("Input Query:", key="input")
submit = st.button("Search")

if submit:
    article_title = question  
    article_query = f'''SELECT article_keywords FROM article WHERE title = "{article_title}";'''
    article_keywords = execute_sql_query(article_query)
    
    if article_keywords:
        article_keywords = article_keywords[0][0]  
        

        ebook_query = '''SELECT title, description FROM ebooks WHERE status = "published";'''
        ebook_results = execute_sql_query(ebook_query)
        
        ebook_titles = [row[0] for row in ebook_results]
        ebook_descriptions = [row[1] for row in ebook_results]
        
  
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix_articles = tfidf_vectorizer.fit_transform([article_keywords])
        tfidf_matrix_ebooks = tfidf_vectorizer.transform(ebook_descriptions)

        similarity_scores = cosine_similarity(tfidf_matrix_articles, tfidf_matrix_ebooks)

        top_indices = similarity_scores.argsort()[0][-5:][::-1]
        top_ebook_titles = [ebook_titles[i] for i in top_indices]
        
        st.subheader("Top 5 eBooks with Highest Cosine Similarity to Article Keywords:")
        st.table(top_ebook_titles)
    else:
        st.write("Article not found. Please enter a valid article title.")
