import streamlit as st
import zipfile
import time
import polars as pl

st.title("Test lecture CSV")

uploaded_file = st.file_uploader(
    "Dépose ton ZIP",
    type=["zip"]
)

if uploaded_file:

    with zipfile.ZipFile(uploaded_file) as z:

        csv_file = [
            f for f in z.namelist()
            if f.lower().endswith(".csv")
            and "__macosx" not in f.lower()
        ][0]

        st.write(f"CSV trouvé : {csv_file}")

        with z.open(csv_file) as f:

            start = time.time()

            df = pl.read_csv(
                f,
                columns=["Email", "Email Marketing Consent"],
                n_rows=100000
            )

            elapsed = time.time() - start

            st.success(
                f"100 000 lignes lues en {elapsed:.1f}s"
            )

            st.write(
                f"Lignes chargées : {len(df):,}".replace(",", " ")
            )

            st.dataframe(df.head(20))
