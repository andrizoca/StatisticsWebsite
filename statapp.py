import re
import streamlit as st
import pandas as pd
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
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
        1: "unimodal", 2: "bimodal", 3: "trimodal", 4: "tetramodal",
        5: "pentamodal", 6: "hexamodal", 7: "heptamodal", 8: "octamodal",
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

def media_agrupada(df: pd.DataFrame) -> float:
    df["Pmi"] = (df["Li"] + df["Ls"]) / 2
    N = df["fi"].sum()
    if N == 0:
        raise ValueError("A soma das frequências (N) não pode ser zero.")
    media = (df["Pmi"] * df["fi"]).sum() / N
    return arredondar(media)

def mediana_agrupada(df: pd.DataFrame) -> float:
    N = df["fi"].sum()
    df["Fac"] = df["fi"].cumsum()
    
    N2 = N / 2
    try:
        linha_mediana = df[df["Fac"] >= N2].iloc[0]
        idx_mediana = linha_mediana.name
    except IndexError:
        raise ValueError("Não foi possível encontrar a classe da mediana.")

    L = linha_mediana["Li"]
    h = linha_mediana["Ls"] - linha_mediana["Li"]
    f = linha_mediana["fi"]
    
    idx_pos = df.index.get_loc(idx_mediana)
    F_anterior = df.iloc[idx_pos - 1]["Fac"] if idx_pos > 0 else 0

    mediana = L + ((N2 - F_anterior) / f) * h
    return arredondar(mediana)

def moda_agrupada(df: pd.DataFrame):
    t = df.reset_index(drop=True)
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
        Li, Ls = float(t.at[pos, "Li"]), float(t.at[pos, "Ls"])
        h_classe = Ls - Li
        modas_brutas.append((Li + Ls) / 2)
        
        f_modal = float(t.at[pos, "fi"])
        f_prev = float(t.at[pos - 1, "fi"]) if pos - 1 >= 0 else 0.0
        f_next = float(t.at[pos + 1, "fi"]) if pos + 1 < len(t) else 0.0
        
        d1, d2 = f_modal - f_prev, f_modal - f_next
        if (d1 + d2) > 0:
            moda_cz = Li + (d1 / (d1 + d2)) * h_classe
            modas_czuber.append(arredondar(moda_cz))
        else:
            modas_czuber.append(None)
            
    return modas_brutas, modas_czuber, tipo_moda

def variancia_agrupada(df: pd.DataFrame, media: float) -> float:
    N = df["fi"].sum()
    if N <= 1:
        raise ValueError("A amostra precisa ter mais de um elemento para calcular a variância.")
    
    if "Pmi" not in df.columns:
         df["Pmi"] = (df["Li"] + df["Ls"]) / 2
         
    variancia = (((df["Pmi"] - media)**2) * df["fi"]).sum() / (N - 1)
    return arredondar(variancia)
    
st.set_page_config(page_title = "Estatística", page_icon = "heavy_plus_sign", layout="centered")
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


st.title(":red[Bem vindo ao site de Estatística]",anchor = None)
st.subheader("Esta aplicação é uma calculadora que utiliza agrupamentos discreto e por classes para calcular: ")
st.markdown("##### Cálculo de média - Mediana - Modas - Variância - Desvio Padrão - Coeficiente de Variação")
st.markdown(":gray[_Criado por Andriy Tam, Henrique Sabino, Paulo Santos e Luis Carlos Oliveira_]")
st.divider()


aba_principal1, aba_principal2 = st.tabs(["Agrupamento Discreto", "Agrupamento por Classes"])

with aba_principal1:
    st.markdown("""
<style>
button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
    font-size: 50px;
    font-weight: bold; 
}
</style>
""", unsafe_allow_html=True)
    st.caption("## Selecione o método de entrada:")
    tab1, tab2 = st.tabs(["Tabela (xᵢ, fᵢ)", "Lista de valores"])

    st.markdown("""
    <style>
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

    with tab1:
        base = pd.DataFrame({"xi":[None], "fi":[None]})
        with st.form("form_tabela"):
            st.markdown("#### Para adicionar mais linhas, **clique no `+` abaixo da tabela**.")
            edited = st.data_editor(
                base, num_rows="dynamic", use_container_width=True,
                column_config={
                    "xi": st.column_config.NumberColumn("xᵢ"),
                    "fi": st.column_config.NumberColumn("fᵢ", min_value=0, step=1),
                }
            )
            
            st.markdown("### Selecione o que deseja calcular: ")
            mediacbx = st.checkbox("Média") 
            medianacbx = st.checkbox("Mediana")
            modacbx = st.checkbox("Moda")
            varianciacbx = st.checkbox("Variância")
            desviopadraocbx = st.checkbox("Desvio Padrão")
            coeficientecbx = st.checkbox("Coeficiente de Variação")
            
            sub = st.form_submit_button("Calcular")
        if sub:
            try:
                edited = edited.dropna().astype(float)
                m = arredondar(media_ponderada_df(edited), 2)
                me = arredondar(mediana_df(edited),2)
                modais, tipo = moda_df(edited)
                variance = arredondar(variancia_df(edited), 2)
                desvio_padrao = arredondar(math.sqrt(variance), 2)
                cv = (100 * desvio_padrao)/m
                coeficiente_variacao = arredondar(cv, 2)
                
                if mediacbx: 
                    st.success(f"### Média: {m:.2f}")
                if medianacbx:
                    st.success(f"### Mediana: {me:.2f}")
                if modacbx:
                    st.success(f"### Moda ({tipo}) : {', '.join(f'{x:.2f}' for x in modais)} ")
                if varianciacbx: 
                    st.success(f"### Variância: {variance:.2f}")
                if desviopadraocbx: 
                    st.success(f"### Desvio Padrão: {desvio_padrao:.2f}")
                if coeficientecbx: 
                    st.success(f"### Coeficiente de Variação: {coeficiente_variacao:.2f}%")
                    
            except Exception as e:
                st.warning(str(e))
    

    with tab2:
        with st.form("form_texto"):
            st.markdown("""
        <style>
        [data-testid="stTextArea"] textarea {
            font-size: 22px !important;
            height: 150px;
        }
        </style>
        """, unsafe_allow_html=True)
            st.subheader("Digite os números a serem calculados separados por espaço ou vírgula")
            s = st.text_area(label=' ', key='text_area1')
            st.caption(f"### Números a serem calculados: {s}")
            
            st.markdown("### Selecione o que deseja calcular: ")
            mediacbx = st.checkbox("Média") 
            medianacbx = st.checkbox("Mediana")
            modacbx = st.checkbox("Moda")
            varianciacbx = st.checkbox("Variância")
            desviopadraocbx = st.checkbox("Desvio Padrão")
            coeficientecbx = st.checkbox("Coeficiente de Variação")
            
            sub2 = st.form_submit_button("Calcular")
        if sub2:
            try:
                nums = parse_numeros(s)
                if not nums:
                    raise ValueError("Nenhum número encontrado.")
                freq = Counter(nums)
                df_freq = pd.DataFrame(sorted(freq.items()), columns=["xi","fi"])
                
                m = arredondar(media_ponderada_df(df_freq), 2)
                me = arredondar(mediana_df(df_freq), 2)
                modais, tipo = moda_df(df_freq)
                variance = arredondar(variancia_df(df_freq), 2)
                desvio_padrao = arredondar(math.sqrt(variance), 2)
                cv = (100 * desvio_padrao)/m
                coeficiente_variacao = arredondar(cv, 2)
                
                if mediacbx: 
                    st.success(f"### Média: {m:.2f}")
                if medianacbx:
                    st.success(f"### Mediana: {me:.2f}")
                if modacbx:
                    st.success(f"### Moda ({tipo}) : {', '.join(f'{x:.2f}' for x in modais)} ")
                if varianciacbx: 
                    st.success(f"### Variância: {variance:.2f}")
                if desviopadraocbx: 
                    st.success(f"### Desvio Padrão: {desvio_padrao:.2f}")
                if coeficientecbx: 
                    st.success(f"### Coeficiente de Variação: {coeficiente_variacao:.2f}%")
                
            except Exception as e:
                st.error(f"Entrada inválida: {e}")
                
                
with aba_principal2:
    st.subheader("Agrupamento por Classes")
    st.markdown(
        "Preencha `Li` e `Ls` na primeira linha. "
        "Clique em **Adicionar classe (+)** para criar a próxima com o mesmo `h = Ls − Li`."
    )

    if 'df_classes' not in st.session_state:
        st.session_state.df_classes = pd.DataFrame([{"Li": None, "Ls": None, "fi": None}])

    # ===== UM ÚNICO FORM (editor -> botão + -> checkboxes -> Calcular) =====
    with st.form("form_classes_all", clear_on_submit=False):
        edited_df = st.data_editor(
            st.session_state.df_classes,
            num_rows="fixed",                # sem '+' nativo
            use_container_width=True,
            column_config={
                "Li": st.column_config.NumberColumn("Limite Inferior (lᵢ)", format="%d", step=1),
                "Ls": st.column_config.NumberColumn("Limite Superior (lₛ)", format="%d", step=1),
                "fi": st.column_config.NumberColumn("Frequência (fi)", min_value=0, step=1, format="%d"),
            },
            key="editor_classes"
        )

        # Botão + ANTES dos checkboxes
        add_clicked = st.form_submit_button("Adicionar classe (+)", use_container_width=True)

        st.markdown("### Selecione o que deseja calcular: ")
        mediacbx        = st.checkbox("Média")
        medianacbx      = st.checkbox("Mediana")
        modabrutacbx    = st.checkbox("Moda Bruta")
        modaczubercbx   = st.checkbox("Moda de Czuber")
        varianciacbx    = st.checkbox("Variância")
        desviopadraocbx = st.checkbox("Desvio Padrão")
        coeficientecbx  = st.checkbox("Coeficiente de Variação")

        calc_clicked = st.form_submit_button("Calcular", use_container_width=True)

    # ===== (+): usa exatamente o que está NA TELA (edited_df) =====
    if add_clicked:
        base = edited_df.copy()

        tmp = base.copy()
        tmp["Li"] = pd.to_numeric(tmp["Li"], errors="coerce")
        tmp["Ls"] = pd.to_numeric(tmp["Ls"], errors="coerce")

        comp = tmp.dropna(subset=["Li", "Ls"])
        if not comp.empty:
            last_idx = comp.index.max()
            prev_Li  = int(round(tmp.loc[last_idx, "Li"]))
            prev_Ls  = int(round(tmp.loc[last_idx, "Ls"]))
            h_int    = int(round(prev_Ls - prev_Li))
            if h_int > 0:
                new_row = {"Li": prev_Ls, "Ls": prev_Ls + h_int, "fi": None}
            else:
                new_row = {"Li": None, "Ls": None, "fi": None}
        else:
            new_row = {"Li": None, "Ls": None, "fi": None}

        st.session_state.df_classes = pd.concat(
            [base, pd.DataFrame([new_row])], ignore_index=True
        )
        st.rerun()

    # ===== Calcular: usa o edited_df confirmado pelo form =====
    if calc_clicked:
        try:
            tabela_classes = edited_df.copy()
            tabela_classes["Li"] = pd.to_numeric(tabela_classes["Li"], errors="coerce")
            tabela_classes["Ls"] = pd.to_numeric(tabela_classes["Ls"], errors="coerce")
            tabela_classes["fi"] = pd.to_numeric(tabela_classes["fi"], errors="coerce")
            tabela_classes = tabela_classes.dropna(subset=["Li", "Ls", "fi"]).astype(float)

            if tabela_classes.empty:
                raise ValueError("A tabela está vazia ou contém dados inválidos.")

            media = media_agrupada(tabela_classes)
            mediana = mediana_agrupada(tabela_classes)
            modas_brutas, modas_czuber, tipo_moda = moda_agrupada(tabela_classes)
            variancia = variancia_agrupada(tabela_classes, media)
            desvio_padrao = arredondar(math.sqrt(variancia))
            coeficiente_variacao = arredondar((100 * desvio_padrao) / media, 2) if media != 0 else None

            cards = []
            if mediacbx:        cards.append(("Média", f"{media:.2f}"))
            if medianacbx:      cards.append(("Mediana", f"{mediana:.2f}"))
            if modabrutacbx:    cards.append(("Moda Bruta", ", ".join(f"{m:.2f}" for m in modas_brutas)))
            if modaczubercbx:   cards.append(("Moda de Czuber", ", ".join("N/A" if m is None else f"{m:.2f}" for m in modas_czuber)))
            if varianciacbx:    cards.append(("Variância", f"{variancia:.2f}"))
            if desviopadraocbx: cards.append(("Desvio Padrão", f"{desvio_padrao:.2f}"))
            if coeficientecbx:
                cards.append(("Coeficiente de Variação", f"{coeficiente_variacao:.2f}%" if coeficiente_variacao is not None else "Indefinido"))

            # imprime em 3 colunas (quebra em novas linhas automaticamente)
            cols = st.columns(2)
            for i, (titulo, valor) in enumerate(cards):
                with cols[i % 2]:
                    st.metric(titulo, valor)
        except Exception as e:
            st.error(f"Erro: {e}")



