import streamlit as st
import requests

st.title("Test fichier SharePoint")

url = st.text_input("Lien du fichier")

if st.button("Tester"):

    try:
        r = requests.get(url, allow_redirects=True, timeout=30)

        st.write("Status :", r.status_code)
        st.write("URL finale :", r.url)

    except Exception as e:
        st.error(str(e))
