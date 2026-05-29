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
    "L'envoi du fichier peut prendre plusieurs minutes avant le démarrage de l'analyse."
)

uploaded_file = st.file_uploader(
    "Déposez votre export Klaviyo compressé (.zip)",
    type=["zip"]
)

if uploaded_file:

    start_total = time.time()

    progress = st.progress(0)

    current_step = st.empty()
    timer = st.empty()

    current_step.info("📥 Étape 1/4 : Fichier reçu")
    progress.progress(25)

    with zipfile.ZipFile(uploaded_file) as z:

        current_step.info("📦 Étape 2/4 : Ouverture du ZIP")
        progress.progress(50)

        csv_file = [
            f for f in z.namelist()
            if f.lower().endswith(".csv")
            and "__macosx" not in f.lower()
        ][0]

        st.success(f"📄 Fichier détecté : {csv_file}")

        current_step.info("📊 Étape 3/4 : Lecture du fichier complet")

        with z.open(csv_file) as f:

            start = time.time()

            df = pl.read_csv(
                f,
                columns=[
                    "Email",
                    "Email Marketing Consent"
                ],
                ignore_errors=True
            )

            progress.progress(75)

            st.success(
                f"✅ Fichier chargé en {time.time() - start:.1f} secondes"
            )

            st.write(
                f"📈 Nombre de lignes : {len(df):,}".replace(",", " ")
            )

        current_step.info("🔎 Étape 4/4 : Calcul des indicateurs")

        consent_col = "Email Marketing Consent"
        email_col = "Email"

        df = df.with_columns(
            pl.when(
                pl.col(consent_col).is_null()
                | (pl.col(consent_col) == "")
            )
            .then(pl.lit("EMPTY"))
            .otherwise(pl.col(consent_col))
            .alias(consent_col)
        )

        result = (
            df
            .group_by(consent_col)
            .len()
            .rename({"len": "Nb lignes"})
            .sort("Nb lignes", descending=True)
        )

        total = result["Nb lignes"].sum()

        result = result.with_columns(
            (
                pl.col("Nb lignes") * 100 / total
            )
            .round(1)
            .alias("%")
        )

        total_row = pl.DataFrame({
            consent_col: ["Total"],
            "Nb lignes": [int(total)],
            "%": [100.0]
        })

        result = pl.concat([
            result.cast({
                consent_col: pl.Utf8,
                "Nb lignes": pl.Int64,
                "%": pl.Float64
            }),
            total_row
        ])

        duplicate_emails = (
            df
            .group_by(email_col)
            .len()
            .filter(pl.col("len") > 1)
            .height
        )

        progress.progress(100)

        current_step.success("✅ Analyse terminée")

        timer.success(
            f"Temps total : {time.time() - start_total:.1f} secondes"
        )

        st.subheader("Résultats")

        st.dataframe(
            result.to_pandas(),
            use_container_width=True,
            hide_index=True
        )

        st.metric(
            "Emails en doublon",
            f"{duplicate_emails:,}".replace(",", " ")
        )
