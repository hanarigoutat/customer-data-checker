import streamlit as st
import pandas as pd
import zipfile
from collections import Counter

st.set_page_config(
    page_title="Customer Data Checker",
    layout="wide"
)

st.title("Customer Data Checker")

st.warning(
    "Les exports volumineux peuvent nécessiter plusieurs minutes de traitement."
)

uploaded_file = st.file_uploader(
    "Déposez votre export Klaviyo compressé (.zip)",
    type=["zip"]
)

if uploaded_file:

    progress = st.progress(0)
    status = st.empty()

    consent_counts = Counter()
    email_counts = Counter()

    status.info("Étape 1 sur 4 : Fichier reçu")
    progress.progress(10)

    with zipfile.ZipFile(uploaded_file) as z:

        status.info("Étape 2 sur 4 : Ouverture du fichier")
        progress.progress(25)

        csv_file = [
            f for f in z.namelist()
            if f.lower().endswith(".csv")
            and "__macosx" not in f.lower()
        ][0]

        status.info("Étape 3 sur 4 : Analyse des données")
        progress.progress(40)

        with z.open(csv_file) as f:

            chunks = pd.read_csv(
                f,
                usecols=["Email", "Email Marketing Consent"],
                chunksize=500_000,
                dtype=str
            )

            nb_chunks = 0
            total_rows = 0

            for chunk in chunks:

                nb_chunks += 1

                chunk["Email"] = (
                    chunk["Email"]
                    .fillna("")
                    .str.strip()
                    .str.lower()
                )

                chunk["Email Marketing Consent"] = (
                    chunk["Email Marketing Consent"]
                    .fillna("EMPTY")
                    .replace("", "EMPTY")
                )

                consent_counts.update(
                    chunk["Email Marketing Consent"]
                )

                email_counts.update(
                    chunk["Email"]
                )

                total_rows += len(chunk)

                progression = min(
                    40 + (nb_chunks * 2),
                    85
                )

                progress.progress(progression)

    status.info("Étape 4 sur 4 : Vérification des doublons")
    progress.progress(90)

    duplicate_emails = sum(
        1
        for count in email_counts.values()
        if count > 1
    )

    total = sum(consent_counts.values())

    results = []

    for status_name, count in sorted(
        consent_counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        results.append({
            "Email Marketing Consent": status_name,
            "Nb lignes": f"{count:,}".replace(",", " "),
            "%": round((count / total) * 100, 1)
        })

    results.append({
        "Email Marketing Consent": "Total",
        "Nb lignes": f"{total:,}".replace(",", " "),
        "%": 100.0
    })

    progress.progress(100)

    status.success("Analyse terminée")

    st.write(
        f"Nombre total de lignes analysées : "
        f"{total_rows:,}".replace(",", " ")
    )

    st.subheader("Résultats")

    st.dataframe(
        pd.DataFrame(results),
        use_container_width=True,
        hide_index=True
    )

    st.metric(
        "Emails en doublon",
        f"{duplicate_emails:,}".replace(",", " ")
    )
