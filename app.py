import streamlit as st
import polars as pl

st.title("Test Polars")

df = pl.DataFrame({
    "a": [1, 2, 3]
})

st.write(df)
