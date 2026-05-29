import streamlit as st
import zipfile

st.title("Test ZIP")

uploaded_file = st.file_uploader(
    "Dépose un ZIP",
    type=["zip"]
)

if uploaded_file:

    st.success("ZIP uploadé")

    with zipfile.ZipFile(uploaded_file) as z:

        csv_files = [
            f for f in z.namelist()
            if f.lower().endswith(".csv")
        ]

        st.write("CSV trouvés :")
        st.write(csv_files)
