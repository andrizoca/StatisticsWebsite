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
st.markdown("""
<style>
/* Aumenta fonte do índice da tabela */
div[data-testid="stDataFrame"] div[role="rowheader"] {
    font-size: 22px !important;
    font-weight: bold;
}

/* Aumenta fonte do conteúdo das células */
div[data-testid="stDataFrame"] div[role="gridcell"] input {
    font-size: 22px !important;
}
</style>
""", unsafe_allow_html=True)


st.title(":red[Bem vindo ao site de Estatística]",anchor = None)
st.subheader("Esta aplicação é uma calculadora que utiliza agrupamentos discreto e por classes para calcular: ")
st.markdown("##### Cálculo de média - Mediana - Modas - Variância - Desvio Padrão - Coeficiente de Variação")
st.markdown(":gray[_Criado por Andriy Tam, Henrique Sabino e Paulo Santos_]")
st.divider()


# Abas principais
aba_principal1, aba_principal2 = st.tabs(["Agrupamento Discreto", "Agrupamento por Classes"])

# --- Agrupamento Discreto ---
with aba_principal1:
    st.markdown("""
<style>
/* Altera o tamanho da fonte das abas principais */
button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
    font-size: 50px;
    font-weight: bold; /* opcional, deixa em negrito */
}
</style>
""", unsafe_allow_html=True)
    st.caption("## Selecione o método de entrada:")
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
                me = arredondar(mediana_df(edited),2)
                modais, tipo = moda_df(edited)
                variance = arredondar(variancia_df(edited), 2)                
                desvio_padrao = arredondar(math.sqrt(variance), 2)
                cv = (100 * desvio_padrao)/m
                coeficiente_variacao = arredondar(cv, 2)
                
                st.success(f"### Média: {m:.2f}")
                st.success(f"### Mediana: {me:.2f}")
                st.success(f"### Moda ({tipo}) : {', '.join(f"{x:.2f}" for x in modais)} ")
                st.success(f"### Variância: {variance:.2f}")
                st.success(f"### Desvio Padrão: {desvio_padrao:.2f}")
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
                
                #Chama a função da mediana
                me = arredondar(mediana_df(df_freq), 2)
                
                #Chama a função da moda
                modais, tipo = moda_df(df_freq)
                
                variance = arredondar(variancia_df(df_freq), 2)
                
                desvio_padrao = arredondar(math.sqrt(variance), 2)
                
                cv = (100 * desvio_padrao)/m
                coeficiente_variacao = arredondar(cv, 2)
                
                st.success(f"### Média: {m:.2f}")
                st.success(f"### Mediana: {me:.2f}")
                st.success(f"### Moda ({tipo}) : {', '.join(f"{x:.2f}" for x in modais)} ")
                st.success(f"### Variância: {variance:.2f}")
                st.success(f"### Desvio Padrão: {desvio_padrao:.2f}")
                st.success(f"### Coeficiente de Variação: {coeficiente_variacao:.2f}%")
                
            except Exception as e:
                st.error(f"Entrada inválida: {e}")
                
                
with aba_principal2:
    st.subheader("Agrupamento por Classes")

    base_classes = pd.DataFrame({
        "Li": [None],
        "Ls": [None],
        "fi": [None]
    })

    with st.form("form_classes"):
        tabela_classes = st.data_editor(
            base_classes, num_rows="dynamic", use_container_width=True,
            column_config={
                "Li": st.column_config.NumberColumn("Limite Inferior (lᵢ)"),
                "Ls": st.column_config.NumberColumn("Limite Superior (lₛ)"),
                "fi": st.column_config.NumberColumn("Frequência (fi)", min_value=0, step=1),
            }
        )
        sub_classes = st.form_submit_button("Calcular")

        if sub_classes:
            try:
                tabela_classes = tabela_classes.dropna().astype(float)

                # calcula ponto médio
                tabela_classes["Pmi"] = (tabela_classes["Li"] + tabela_classes["Ls"]) / 2
                N = tabela_classes["fi"].sum()

                # Frequência acumulada
                tabela_classes["Fac"] = tabela_classes["fi"].cumsum()

                # Média
                media = arredondar((tabela_classes["Pmi"] * tabela_classes["fi"]).sum() / N)

                # Mediana
                N2 = N/2
                linha_mediana = tabela_classes[tabela_classes["Fac"] >= N2].iloc[0]
                idx_mediana = tabela_classes.index[tabela_classes["Fac"] >= N2][0]
                L = linha_mediana["Li"]
                h = linha_mediana["Ls"] - linha_mediana["Li"]
                f = linha_mediana["fi"]
                F_anterior = tabela_classes.loc[idx_mediana-1, "Fac"] if idx_mediana > 0 else 0
                mediana = arredondar(L + ((N2 - F_anterior) / f) * h)

                # --- Moda (2 versões) ---
                # Implementação robusta para multimodalidade:
                t = tabela_classes.reset_index(drop=True).copy()  # trabalho em cópia com índice contínuo

                # detectar classes modais (pode ser multimodal)
                freqmax = t["fi"].max()
                modal_pos = t.index[t["fi"] == freqmax].tolist()

                tipos = {
                    1: "unimodal", 2: "bimodal", 3: "trimodal", 4: "tetramodal",
                    5: "pentamodal", 6: "hexamodal", 7: "heptamodal", 8: "octamodal"
                }
                tipo_moda = tipos.get(len(modal_pos), "multimodal")

                modas_brutas = []
                modas_czuber = []

                for pos in modal_pos:
                    Li = float(t.at[pos, "Li"])
                    Ls = float(t.at[pos, "Ls"])
                    h_classe = Ls - Li
                    Pmi = (Li + Ls) / 2
                    modas_brutas.append(Pmi)

                    f_modal = float(t.at[pos, "fi"])
                    f_prev = float(t.at[pos - 1, "fi"]) if pos - 1 >= 0 else 0.0
                    f_next = float(t.at[pos + 1, "fi"]) if pos + 1 < len(t) else 0.0

                    d1 = f_modal - f_prev
                    d2 = f_modal - f_next

                    if (d1 + d2) > 0:
                        moda_cz = Li + (d1 / (d1 + d2)) * h_classe
                        moda_cz = arredondar(moda_cz, 2)
                        modas_czuber.append(moda_cz)
                    else:
                        modas_czuber.append(None)

                # Impressão formatada
                st.success(f"### Média: {media:.2f}")
                st.success(f"### Mediana: {mediana:.2f}")
                st.success(f"### Moda Bruta ({tipo_moda}): " +
                           ", ".join(f"{m:.2f}" for m in modas_brutas))
                cz_strs = [f"{arredondar(m):.2f}" if m is not None else "N/A" for m in modas_czuber]
                st.success(f"### Moda de Czuber ({tipo_moda}): " + ", ".join(cz_strs))

                # Variância
                variancia = arredondar((( (tabela_classes["Pmi"] - media)**2 ) * tabela_classes["fi"]).sum() / (N - 1))

                # Desvio Padrão
                desvio_padrao = arredondar(math.sqrt(variancia))
                
                #Coeficiente de variação
                cv = (100 * desvio_padrao)/media
                coeficiente_variacao = arredondar(cv, 2)

                st.success(f"### Variância: {variancia:.2f}")
                st.success(f"### Desvio Padrão: {desvio_padrao:.2f}")
                st.success(f"### Coeficiente de variação: {coeficiente_variacao:.2f}%")
                

            except Exception as e:
                st.error(f"Erro: {e}")