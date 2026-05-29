import streamlit as st
import polars as pl
import zipfile
import time

st.set_page_config(
    page_title="Customer Data Checker",
    layout="wide"
)

st.title("Customer Data Checker")

uploaded_file = st.file_uploader(
    "Déposez votre export Klaviyo compressé (.zip)",
    type=["zip"]
)

if uploaded_file:

    start_total = time.time()

    st.write("✅ ZIP uploadé")
    st.write(f"Taille ZIP : {uploaded_file.size / 1024 / 1024:.1f} MB")

    try:

        with zipfile.ZipFile(uploaded_file) as z:

            st.write("✅ ZIP ouvert")

            csv_files = [
                f for f in z.namelist()
                if f.lower().endswith(".csv")
            ]

            st.write(f"✅ {len(csv_files)} CSV trouvé(s)")

            if not csv_files:
                st.error("Aucun CSV trouvé dans le ZIP")
                st.stop()

            csv_file = csv_files[0]

            st.write(f"📄 CSV sélectionné : {csv_file}")

            with z.open(csv_file) as f:

                st.write("⏳ Lecture du CSV...")

                start = time.time()

                df = pl.read_csv(
                    f,
                    columns=[
                        "Email",
                        "Email Marketing Consent"
                    ],
                    ignore_errors=True
                )

                st.write(
                    f"✅ CSV chargé en {time.time() - start:.1f}s"
                )

                st.write(
                    f"✅ Nombre de lignes : {len(df):,}".replace(",", " ")
                )

        consent_col = "Email Marketing Consent"
        email_col = "Email"

        st.write("⏳ Préparation des données...")

        df = df.with_columns(
            pl.when(
                pl.col(consent_col).is_null()
                | (pl.col(consent_col) == "")
            )
            .then(pl.lit("EMPTY"))
            .otherwise(pl.col(consent_col))
            .alias(consent_col)
        )

        st.write("⏳ Calcul des consentements...")

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

        # Ligne Total
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

        st.write("✅ Consentements calculés")

        st.write("⏳ Calcul des doublons...")

        duplicate_emails = (
            df
            .group_by(email_col)
            .len()
            .filter(pl.col("len") > 1)
            .height
        )

        st.write("✅ Doublons calculés")

        st.success(
            f"Analyse terminée en {time.time() - start_total:.1f}s"
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

    except Exception as e:
        st.error("Erreur")
        st.exception(e)
