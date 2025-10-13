import streamlit as st
st.set_page_config(page_title="Regressão Linear", page_icon="📈", layout="wide")

st.title("📈 Regressão Linear")
st.sidebar.header("Navegação")
st.sidebar.write("Escolha uma página na barra lateral 👈")

# CSS para o título das subtabs
st.markdown("""
    <style>
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 50px;
        font-weight: bold; 
    }
    </style>
    """, unsafe_allow_html=True)

    
st.caption("## Selecione o tipo de equação:")
tab1, tab2 = st.tabs(["Equação da reta", "Equação do 2° grau"])

# CSS para o rótulo das subtabs (menor)
st.markdown("""
<style>
button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {font-size: 25px;}</style>""", unsafe_allow_html=True)
        