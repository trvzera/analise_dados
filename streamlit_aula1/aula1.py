import streamlit as st
import pandas as pd

st.write("Hello, world!")

nome = "Giovanni"
idade = 18

st.write(nome, idade)

df = pd.DataFrame({
'Português': [1, 2, 3, 4],
'Matemática': [10, 20, 30, 40],
'Python': [5, 9, 7, 10],
'Frame': [10, 7, 9, 5]
})

st.title("Meu primeiro dash")
st.subheader("Giovanni")

st.write(df)