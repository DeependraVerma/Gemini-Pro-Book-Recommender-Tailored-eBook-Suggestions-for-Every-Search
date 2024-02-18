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

date_input = st.date_input("Select Date:", key="date_input")
submit = st.button("Search")

if submit:
    date_bracket_query = f'''SELECT date_type FROM exam_dates WHERE '{date_input}' BETWEEN start_date AND end_date;'''
    date_type = execute_sql_query(date_bracket_query)
    
    if date_type:
        date_type = date_type[0][0]
        
        ebook_query = '''SELECT title, description FROM ebooks WHERE YEAR(STR_TO_DATE(updated, '%d-%m-%Y %H:%i')) > 2022 AND status = "published";'''
        ebook_results = execute_sql_query(ebook_query)
        
        ebook_titles = [row[0] for row in ebook_results]
        ebook_descriptions = [row[1] for row in ebook_results]
        
        model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        
        date_embedding = model.encode(date_type, convert_to_tensor=True)
        ebook_embeddings = model.encode(ebook_descriptions, convert_to_tensor=True)
        
        similarity_scores = util.pytorch_cos_sim(date_embedding, ebook_embeddings)
        
        similarity_scores = similarity_scores.cpu().numpy()
        
        top_indices = similarity_scores.argsort()[0][-5:][::-1]
        top_ebook_titles = [ebook_titles[i] for i in top_indices]
        
        st.subheader(f"Top 5 eBooks with Highest BERT Similarity to Date Type '{date_type}':")
        st.table(top_ebook_titles)
    else:
        st.write("No matching date type found for the selected date.")
