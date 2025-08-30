import re #Regular Expressions
import streamlit as st #Biblio Streamlit
import pandas as pd #tabelas 
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP #decimal para arredondamento
import statistics
import math

def arredondar(valor: float, casas: int = 2) -> float:
    return float(Decimal(str(valor)).quantize(Decimal("1." + "0"*casas), rounding=ROUND_HALF_UP))

def parse_numeros(s: str):
    tokens = re.findall(r'[-+]?\d+(?:[.,]\d+)?', s)
    return [float(t.replace(",", ".")) for t in tokens]

def media_ponderada_df(df: pd.DataFrame) -> float:
    df = df.dropna()
    if df.empty or df["fi"].sum() == 0:
        raise ValueError("Inclua ao menos uma linha válida e frequências > 0.")
    return (df["xi"]*df["fi"]).sum() / df["fi"].sum()

def mediana_df(df: pd.DataFrame) -> float:
    df = df.dropna()
    if df.empty or df["fi"].sum() == 0:
        raise ValueError("Inclua ao menos uma linha válida e frequências > 0.")
    serie_numeros_df = df["xi"].repeat(df["fi"])
    lista_numeros_df = serie_numeros_df.tolist()
    return statistics.median(lista_numeros_df)

def moda_df(df: pd.DataFrame):
    df = df.dropna()
    if df.empty or df["fi"].sum() == 0:
        raise ValueError("Inclua ao menos uma linha válida e frequências > 0.")
    
    serie_numeros_df = df["xi"].repeat(df["fi"])
    lista_numeros_df = serie_numeros_df.tolist()
    
    contagem = Counter(lista_numeros_df)
    freqmax = max(contagem.values())
    
    if all(f == freqmax for f in contagem.values()):
        return [], "amodal"
    
    lista_modais = [valor for valor, f in contagem.items() if f == freqmax]
    
    qtd_modais = len(lista_modais)
    tipos = {
        1: "unimodal",
        2: "bimodal",
        3: "trimodal",
        4: "tetramodal",
        5: "pentamodal",
        6: "hexamodal",
        7: "heptamodal",
        8: "octamodal",
    }
    
    tipo_moda = tipos.get(qtd_modais, "multimodal")
    
    return lista_modais, tipo_moda

def variancia_df(df: pd.DataFrame) -> float:
    df = df.dropna()
    if df.empty or df["fi"].sum() == 0:
        raise ValueError("Inclua ao menos uma linha válida e frequências > 0.")
    serie_numeros_df = df["xi"].repeat(df["fi"])
    lista_numeros_df = serie_numeros_df.tolist()
    return statistics.variance(lista_numeros_df)

    
st.set_page_config(page_title = "Estatística", page_icon = "heavy_plus_sign", layout="centered")
st.title(":red[Bem vindo ao site de Estatística]",anchor = None)
st.markdown(":gray[_Criado por Andriy Tam, Henrique Sabino e Paulo Santos_]")
st.divider()
st.caption("## Calcule por meio de:")
tab1, tab2 = st.tabs(["Tabela (xᵢ, fᵢ)", "Lista de valores"])

# --- Injeção de CSS para aumentar o tamanho da fonte das abas --- 
#Streamlit não apresenta parâmetros de tamanho de fonte nativamente
st.markdown("""
<style>
/* Seletor CSS para as abas */
button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
    font-size: 25px;
}
</style>
""", unsafe_allow_html=True)

with tab1:
    st.markdown("""
    <style>
    /* Estiliza os cabeçalhos das colunas (xᵢ, fᵢ) */
    .st-emotion-cache-1215rkt .st-emotion-cache-12j0h0g {
        font-size: 30px !important; 
    }
    
    /* Estiliza o texto dentro das células */
    .st-emotion-cache-1215rkt .st-emotion-cache-g81adp input {
        font-size: 30px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    base = pd.DataFrame({"xi":[None], "fi":[None]})
    with st.form("form_tabela"):
        edited = st.data_editor(
            base, num_rows="dynamic", use_container_width=True,
            column_config={
                "xi": st.column_config.NumberColumn("xᵢ"),
                "fi": st.column_config.NumberColumn("fᵢ", min_value=0, step=1),
            }
        )
        sub = st.form_submit_button("Calcular")
    if sub:
        try:
            edited = edited.astype(float)
            m = arredondar(media_ponderada_df(edited), 2)
            st.success(f"### Média: {m:.2f}")
            
            me = arredondar(mediana_df(edited),2)
            st.success(f"### Mediana: {me:.2f}")
            
            modais, tipo = moda_df(edited)
            st.success(f"### Moda: {', '.join(f"{x:.2f}" for x in modais)} - Amostra {tipo}")
            
            variance = arredondar(variancia_df(edited), 2)
            st.success(f"### Variância: {variance:.2f}")   
            
            desvio_padrao = arredondar(math.sqrt(variance), 2)
            st.success(f"### Desvio Padrão: {desvio_padrao:.2f}") 
            
            cv = (100 * desvio_padrao)/m
            coeficiente_variacao = arredondar(cv, 2)
            st.success(f"### Coeficiente de Variação: {coeficiente_variacao:.2f}%")
                     
            
        except Exception as e:
            st.warning(str(e))

with tab2:
    with st.form("form_texto"):
        st.markdown("""
    <style>
    [data-testid="stTextArea"] textarea {
        font-size: 22px !important;   /* aumenta o texto digitado */
        height: 150px;                /* aumenta a altura */
    }
    </style>
    """, unsafe_allow_html=True)
        st.subheader("Digite os números a serem calculados separados por espaço ou vírgula")
        s = st.text_area(label=' ', key='text_area1')
        st.caption(f"### Números a serem calculados: {s}")
        
        sub2 = st.form_submit_button("Calcular")
    if sub2:
        try:
            nums = parse_numeros(s)
            if not nums:
                raise ValueError("Nenhum número encontrado.")
            freq = Counter(nums)
            df_freq = pd.DataFrame(sorted(freq.items()), columns=["xi","fi"])
            
            #Chama a função da média
            m = arredondar(media_ponderada_df(df_freq), 2)
            st.success(f"### Média: {m:.2f}")
            
            #Chama a função da mediana
            me = arredondar(mediana_df(df_freq), 2)
            st.success(f"### Mediana: {me:.2f}")
            
            #Chama a função da moda
            modais, tipo = moda_df(df_freq)
            st.success(f"### Moda: {', '.join(f"{x:.2f}" for x in modais)}. Amostra {tipo}.")
            
            variance = arredondar(variancia_df(df_freq), 2)
            st.success(f"### Variância: {variance:.2f}")   
            
            desvio_padrao = arredondar(math.sqrt(variance), 2)
            st.success(f"### Desvio Padrão: {desvio_padrao:.2f}") 
            
            cv = (100 * desvio_padrao)/m
            coeficiente_variacao = arredondar(cv, 2)
            st.success(f"### Coeficiente de Variação: {coeficiente_variacao:.2f}%")
            
        except Exception as e:
            st.error(f"Entrada inválida: {e}")
