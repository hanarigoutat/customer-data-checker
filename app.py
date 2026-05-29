import streamlit as st

st.title("Test upload")

file = st.file_uploader("Dépose ton CSV")

if file:
    st.success(f"Fichier reçu : {file.size / 1024 / 1024:.1f} MB")
