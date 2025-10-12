import streamlit as st

# -------------------------------
# Configuração da página
# -------------------------------
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

# -------------------------------
# Sidebar
# -------------------------------
st.sidebar.header("Navegação")
st.sidebar.write("Escolha uma seção na barra lateral 👈")
st.sidebar.info(
    "Dica: Você pode alternar entre as páginas sem perder os dados enquanto o app estiver aberto."
)

# -------------------------------
# Cabeçalho
# -------------------------------
st.title(":red[Bem-vindo ao Site de Estatística] 👋")
st.subheader("Uma ferramenta prática para **parâmetros estatísticos**, **regressão** e **probabilidade**.")

st.markdown(
    """
Este aplicativo foi pensado para **estudantes** e **profissionais** que precisam calcular medidas estatísticas,
ajustar **reta de regressão** e explorar **distribuições de probabilidade** de forma simples e visual.

Você pode **digitar os dados manualmente** ou **colar de uma planilha**. O app aceita números com **vírgula ou ponto**.
Os resultados são apresentados em cartões, com arredondamento amigável e mensagens de ajuda quando algo estiver faltando.
"""
)

st.divider()

# -------------------------------
# O que você encontra aqui
# -------------------------------
st.markdown("## 🧭 O que você encontra aqui")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        """
**📊 Parâmetros Estatísticos**  
Calcule **média**, **mediana**, **moda** (inclui tipo: uni/bi/tri...), **variância**, **desvio padrão** e **coeficiente de variação**.  
• Suporta dados **discretos** (xi, fi) e por **classes** (Li, Ls, fi).
"""
    )
with col2:
    st.markdown(
        """
**📈 Regressão Linear**  
Ajuste a **equação da reta** aos seus dados (y = a + bx), visualize relações e interprete coeficientes.
"""
    )
with col3:
    st.markdown(
        """
**🎲 Probabilidade**  
Distribuições **contínuas** (Uniforme, Exponencial, Normal) e **discretas** (Binomial, Poisson) com parâmetros e áreas/probabilidades.
"""
    )

st.divider()

# -------------------------------
# Acessos rápidos
# -------------------------------
st.markdown("## 🚀 Acessos rápidos")
st.page_link("pages/1_📊 Parâmetros Estatísticos.py", label="📊 Parâmetros Estatísticos")
st.page_link("pages/2_📈 Regressão Linear.py", label="📈 Regressão Linear")
st.page_link("pages/3_🎲 Probabilidade.py", label="🎲 Probabilidade")

st.divider()

# -------------------------------
# Rodapé
# -------------------------------
st.markdown(":gray[_Criado por Andriy Tam, Henrique Sabino, Paulo Santos e Luis Carlos Oliveira._]")
st.markdown(":gray[_Instruído por João Carlos Santos._]")
