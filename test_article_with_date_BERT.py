from dotenv import load_dotenv
import streamlit as st
import os
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer, util


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

question = st.text_input("Article Title:", key="article_input")
date_input = st.date_input("Select Date:", key="date_input")
submit = st.button("Search")

if submit:
    article_title = question
    article_query = f'''SELECT article_keywords FROM article WHERE title = "{article_title}";'''
    article_keywords = execute_sql_query(article_query)
    
    if article_keywords:
        article_keywords = article_keywords[0][0]  
        date_bracket_query = f'''SELECT date_type FROM exam_dates WHERE '{date_input}' BETWEEN start_date AND end_date;'''
        date_type = execute_sql_query(date_bracket_query)
        
        if date_type:
            date_type = date_type[0][0]
            
            query_text = f"{article_keywords} {date_type}"

            ebook_query = '''SELECT title, description FROM ebooks WHERE YEAR(STR_TO_DATE(updated, '%d-%m-%Y %H:%i')) > 2022 AND status = "published";'''
            ebook_results = execute_sql_query(ebook_query)
            
            ebook_titles = [row[0] for row in ebook_results]
            ebook_descriptions = [row[1] for row in ebook_results]

            model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

            query_embedding = model.encode(query_text, convert_to_tensor=True)
            ebook_embeddings = model.encode(ebook_descriptions, convert_to_tensor=True)

            similarity_scores = util.pytorch_cos_sim(query_embedding, ebook_embeddings)

            similarity_scores = similarity_scores.cpu().numpy()

            top_indices = similarity_scores.argsort()[0][-5:][::-1]
            top_ebook_titles = [ebook_titles[i] for i in top_indices]
            
            st.subheader(f"Top 5 eBooks with Highest BERT Similarity to Article Keywords and Date Type '{date_type}':")
            st.table(top_ebook_titles)
        else:
            st.write("No matching date type found for the selected date.")
    else:
        st.write("Article not found. Please enter a valid article title.")
