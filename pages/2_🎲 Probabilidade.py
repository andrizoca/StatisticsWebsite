import streamlit as st
st.set_page_config(page_title="Probabilidade", page_icon="🎲", layout="wide")

# CSS para aumentar fonte de células, cabeçalhos e checkboxes
st.markdown("""
<style>
div[data-testid="stDataFrame"] div[role="rowheader"] {
    font-size: 30px !important;
    font-weight: bold;
}
div[data-testid="stDataFrame"] div[role="gridcell"] input {
    font-size: 30px !important;
}
div[data-testid="stDataFrame"] .col-header-name {
    font-size: 22px !important;
}
div[data-testid="stCheckbox"] label {
    font-size: 20px !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🎲 Probabilidade")
st.sidebar.header("Navegação")
st.sidebar.write("Escolha uma página na barra lateral 👈")

st.markdown("## Selecione o tipo desejado:")
aba_principal1, aba_principal2 = st.tabs(["Variável aleatória contínua", "Variável aleatória discreta"])

with aba_principal1:
    # CSS para o título das subtabs
    st.markdown("""
    <style>
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 50px;
        font-weight: bold; 
    }
    </style>
    """, unsafe_allow_html=True)

    st.caption("## Selecione o método de entrada:")
    tab1, tab2, tab3 = st.tabs(["Distribuição uniforme", "Distribuição exponencial", "Distribuição normal para amostra"])

    # CSS para o rótulo das subtabs (menor)
    st.markdown("""
    <style>
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 25px;
    }
    </style>
    """, unsafe_allow_html=True)
    
with aba_principal2:
    st.caption("## Selecione o método de entrada:")
    tab1, tab2 = st.tabs(["Distribuição binomial", "Distribuição de Poisson"])
    
        