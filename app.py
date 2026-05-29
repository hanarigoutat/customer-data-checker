import streamlit as st
import pandas as pd
import zipfile
import time
from collections import Counter

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    password = st.text_input(
        "Code d'accès",
        type="password"
    )

    if password == "":
        st.stop()

    if password == "CRM2026":
        st.session_state.authenticated = True
        st.rerun()

    st.error("Code d'accès incorrect")
    st.stop()

st.markdown("""
<style>
.block-container {
    max-width: 1000px;
    padding-top: 2rem;
}

h1 {
    text-align: center;
}

[data-testid="stMetricValue"] {
    font-size: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.title("Contrôle Base Clients")

st.warning(
    "Les exports volumineux peuvent nécessiter plusieurs minutes de traitement."
)

st.info(
    """
    Temps observés sur un export de référence (~12 millions de lignes)

    • Transfert du fichier : environ 4 minutes

    • Analyse des données : environ 1 minute

    • Temps total : environ 5 minutes

    L'analyse démarre automatiquement dès la fin du transfert du fichier.
    """
)

uploaded_file = st.file_uploader(
    "Déposez votre export Klaviyo compressé (.zip)",
    type=["zip"]
)

if uploaded_file:

    start_total = time.time()

    progress = st.progress(0)
    status = st.empty()

    consent_counts = Counter()
    email_counts = Counter()

    with zipfile.ZipFile(uploaded_file) as z:

        status.info("Analyse des données en cours...")
        progress.progress(40)

        csv_file = [
            f for f in z.namelist()
            if f.lower().endswith(".csv")
            and "__macosx" not in f.lower()
        ][0]

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

                progress.progress(
                    min(40 + nb_chunks * 2, 85)
                )

    duplicate_emails = sum(
        1
        for count in email_counts.values()
        if count > 1
    )

    expected_statuses = [
        "SUBSCRIBED",
        "NEVER_SUBSCRIBED",
        "UNSUBSCRIBED",
        "EMPTY"
    ]

    total = sum(consent_counts.values())

    results = []

    for status_name in expected_statuses:

        count = consent_counts.get(status_name, 0)

        pct = (
            round((count / total) * 100, 1)
            if total > 0
            else 0
        )

        results.append({
            "Email Marketing Consent": status_name,
            "Nb lignes": f"{count:,}".replace(",", " "),
            "%": f"{pct:.1f}%".replace(".", ",")
        })

    results.append({
        "Email Marketing Consent": "Total",
        "Nb lignes": f"{total:,}".replace(",", " "),
        "%": "100,0%"
    })

    result_df = pd.DataFrame(results)

    progress.progress(100)
    progress.empty()

    duration = round(time.time() - start_total)

    # Ajout de 3 min 45 sec correspondant au temps moyen de transfert
    duration += 225

    minutes = duration // 60
    seconds = duration % 60

    status.success("Analyse terminée")

    st.caption(
        f"{total_rows:,} lignes analysées"
        .replace(",", " ")
    )

    st.caption(
        f"Temps total estimé (transfert + analyse) : {minutes} min {seconds} sec"
    )

    st.subheader("Résultats")

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Contrôles")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Emails en doublon",
            f"{duplicate_emails:,}".replace(",", " ")
        )

    with col2:
        st.metric(
            "Nombre total de lignes",
            f"{total:,}".replace(",", " ")
        )
