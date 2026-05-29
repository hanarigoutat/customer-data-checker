import streamlit as st
import zipfile
import time
import polars as pl

st.set_page_config(
    page_title="Customer Data Checker",
    layout="wide"
)

st.title("Customer Data Checker")

st.warning(
    "⚠️ Les exports Klaviyo sont volumineux. "
    "L'envoi du fichier peut prendre plusieurs minutes avant le démarrage de l'analyse. "
    "Merci de patienter jusqu'à l'apparition des étapes de traitement."
)

uploaded_file = st.file_uploader(
    "Déposez votre export Klaviyo compressé (.zip)",
    type=["zip"]
)

if uploaded_file:

    start_total = time.time()

    progress = st.progress(0)
    status = st.empty()

    status.info("Étape 1/4 : Fichier reçu")
    progress.progress(25)

    with zipfile.ZipFile(uploaded_file) as z:

        status.info("Étape 2/4 : Ouverture du ZIP")
        progress.progress(50)

        csv_file = [
            f for f in z.namelist()
            if f.lower().endswith(".csv")
            and "__macosx" not in f.lower()
        ][0]

        st.write(f"📄 Fichier détecté : {csv_file}")

        status.info("Étape 3/4 : Lecture du CSV")
        progress.progress(75)

        with z.open(csv_file) as f:

            start = time.time()

            df = pl.read_csv(
                f,
                columns=[
                    "Email",
                    "Email Marketing Consent"
                ],
                n_rows=1000
            )

            st.success(
                f"1000 lignes lues en {time.time() - start:.1f} secondes"
            )

            st.write(
                f"Lignes chargées : {len(df):,}".replace(",", " ")
            )

        status.info("Étape 4/4 : Affichage des résultats")
        progress.progress(100)

        st.dataframe(df.head(20))

    status.success(
        f"✅ Analyse terminée en {time.time() - start_total:.1f} secondes"
    )
