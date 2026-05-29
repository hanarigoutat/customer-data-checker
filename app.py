import streamlit as st
import zipfile
import time

st.title("Test lecture ZIP")

uploaded_file = st.file_uploader(
    "Dépose ton ZIP",
    type=["zip"]
)

if uploaded_file:

    progress = st.progress(0)
    status = st.empty()

    t0 = time.time()

    status.write("📥 Fichier reçu")
    progress.progress(10)

    status.write("📦 Ouverture du ZIP...")
    with zipfile.ZipFile(uploaded_file) as z:

        progress.progress(40)

        files = z.namelist()

        status.write(f"📄 {len(files)} fichier(s) trouvé(s)")
        progress.progress(70)

        st.write(files)

    progress.progress(100)

    status.write(
        f"✅ Terminé en {time.time() - t0:.1f} secondes"
    )
