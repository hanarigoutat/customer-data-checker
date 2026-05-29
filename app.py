import streamlit as st
import polars as pl

st.set_page_config(page_title="Customer Data Checker")

st.title("Customer Data Checker")

uploaded_file = st.file_uploader(
    "Sélectionnez votre export Klaviyo",
    type=["csv"]
)

if uploaded_file:

    consent_col = "Email Marketing Consent"
    email_col = "Email"

    with st.spinner("Analyse en cours..."):

        df = pl.read_csv(
            uploaded_file,
            columns=[email_col, consent_col],
            ignore_errors=True
        )

        result = (
            df
            .with_columns(
                pl.when(
                    pl.col(consent_col).is_null() |
                    (pl.col(consent_col) == "")
                )
                .then(pl.lit("EMPTY"))
                .otherwise(pl.col(consent_col))
                .alias(consent_col)
            )
            .group_by(consent_col)
            .len()
        )

        total = result["len"].sum()

        result = (
            result
            .with_columns(
                (pl.col("len") * 100 / total)
                .round(1)
                .alias("%")
            )
            .rename({"len": "Nb lignes"})
            .sort("Nb lignes", descending=True)
        )

        total_row = pl.DataFrame({
            consent_col: ["Total"],
            "Nb lignes": [total],
            "%": [100.0]
        })

        result = pl.concat([result, total_row])

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
