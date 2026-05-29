import streamlit as st

st.title("Test upload")

uploaded_file = st.file_uploader(
    "Dépose ton ZIP",
    type=["zip"]
)

if uploaded_file:
    st.success("Fichier reçu")
    st.write(f"Taille : {uploaded_file.size / 1024 / 1024:.1f} MB")
