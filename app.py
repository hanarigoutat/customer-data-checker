import streamlit as st
import polars as pl
import zipfile

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

    with st.spinner("Analyse en cours..."):

        # Ouverture du ZIP
        with zipfile.ZipFile(uploaded_file) as z:

            csv_files = [
                f for f in z.namelist()
                if f.lower().endswith(".csv")
            ]

            if len(csv_files) == 0:
                st.error("Aucun fichier CSV trouvé dans le ZIP.")
                st.stop()

            csv_file = csv_files[0]

            with z.open(csv_file) as f:

                df = pl.read_csv(
                    f,
                    columns=[
                        "Email",
                        "Email Marketing Consent"
                    ],
                    ignore_errors=True
                )

        consent_col = "Email Marketing Consent"
        email_col = "Email"

        # Remplacement des valeurs vides
        df = df.with_columns(
            pl.when(
                pl.col(consent_col).is_null()
                | (pl.col(consent_col) == "")
            )
            .then(pl.lit("EMPTY"))
            .otherwise(pl.col(consent_col))
            .alias(consent_col)
        )

        # Comptage consentements
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
            "Nb lignes": [total],
            "%": [100.0]
        })

        result = pl.concat([result, total_row])

        # Emails en doublon
        duplicate_emails = (
            df
            .group_by(email_col)
            .len()
            .filter(pl.col("len") > 1)
            .height
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
