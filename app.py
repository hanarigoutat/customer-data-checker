import streamlit as st
import requests

st.title("Test SharePoint")

url = st.text_input(
    "URL du fichier SharePoint",
    value="https://hyteck.sharepoint.com"
)

if st.button("Tester l'accès"):
    try:
        r = requests.get(url, timeout=20)

        st.write("Status code :", r.status_code)
        st.write("Headers :", dict(r.headers))

    except Exception as e:
        st.error(str(e))
