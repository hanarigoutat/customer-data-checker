import streamlit as st
import zipfile
import time

st.title("Test lecture ZIP")

uploaded_file = st.file_uploader(
    "Dépose ton ZIP",
    type=["zip"]
)

if uploaded_file:

    start = time.time()

    st.success("ZIP reçu")

    with zipfile.ZipFile(uploaded_file) as z:

        st.success("ZIP ouvert")

        files = z.namelist()

        st.write("Fichiers trouvés :")
        st.write(files)

    st.success(
        f"Terminé en {time.time() - start:.1f} secondes"
    )
