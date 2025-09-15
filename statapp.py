# -------------------------------
# Import das bibliotecas
# -------------------------------
import re
import streamlit as st  # Framework web
import pandas as pd
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
import statistics
import math


# -------------------------------
# Funções utilitárias / estatística
# -------------------------------

def arredondar(valor: float, casas: int = 2) -> float:
    """
    Arredonda 'valor' para 'casas' decimais usando HALF_UP (5 arredonda para cima).
    Evita erros de binário do float usando Decimal.
    """
    return float(Decimal(str(valor)).quantize(Decimal("1." + "0"*casas), rounding=ROUND_HALF_UP))


def parse_numeros(s: str):
    """
    Extrai números de um texto aceitando vírgula OU ponto como decimal.
    Ex.: "10,5 7 2.3" -> [10.5, 7.0, 2.3]

    Observação: não trata milhares do tipo "1.234,56". Para isso,
    seria necessário um parser um pouco mais elaborado.
    """
    tokens = re.findall(r'[-+]?\d+(?:[.,]\d+)?', s)
    return [float(t.replace(",", ".")) for t in tokens]


def media_ponderada_df(df: pd.DataFrame) -> float:
    """
    Média ponderada para dados discretos: sum(xi*fi) / sum(fi).
    Exige ao menos uma linha válida e sum(fi) > 0.
    """
    df = df.dropna()
    if df.empty or df["fi"].sum() == 0:
        raise ValueError("Inclua ao menos uma linha válida e frequências > 0.")
    return (df["xi"]*df["fi"]).sum() / df["fi"].sum()


def mediana_df(df: pd.DataFrame) -> float:
    """
    Mediana para dados discretos: repete cada xi pela sua fi e aplica statistics.median.
    """
    df = df.dropna()
    if df.empty or df["fi"].sum() == 0:
        raise ValueError("Inclua ao menos uma linha válida e frequências > 0.")
    serie_numeros_df = df["xi"].repeat(df["fi"])
    lista_numeros_df = serie_numeros_df.tolist()
    return statistics.median(lista_numeros_df)


def moda_df(df: pd.DataFrame):
    """
    Moda para dados discretos:
    - Conta as ocorrências considerando as frequências;
    - Retorna a(s) moda(s) e o tipo (uni, bi, tri, ... multimodal);
    - Se todas as frequências empatam, considera amodal.
    """
    df = df.dropna()
    if df.empty or df["fi"].sum() == 0:
        raise ValueError("Inclua ao menos uma linha válida e frequências > 0.")
    
    serie_numeros_df = df["xi"].repeat(df["fi"])
    lista_numeros_df = serie_numeros_df.tolist()
    
    contagem = Counter(lista_numeros_df)
    freqmax = max(contagem.values())
    
    # Todos empatados no máximo => amodal
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
    """
    Variância amostral para dados discretos (statistics.variance já usa N-1).
    """
    df = df.dropna()
    if df.empty or df["fi"].sum() == 0:
        raise ValueError("Inclua ao menos uma linha válida e frequências > 0.")
    serie_numeros_df = df["xi"].repeat(df["fi"])
    lista_numeros_df = serie_numeros_df.tolist()
    return statistics.variance(lista_numeros_df)


def media_agrupada(df: pd.DataFrame) -> float:
    """
    Média para dados agrupados: usa ponto médio Pmi = (Li + Ls)/2 e soma ponderada por fi.
    """
    df["Pmi"] = (df["Li"] + df["Ls"]) / 2
    N = df["fi"].sum()
    if N == 0:
        raise ValueError("A soma das frequências (N) não pode ser zero.")
    media = (df["Pmi"] * df["fi"]).sum() / N
    return arredondar(media)


def mediana_agrupada(df: pd.DataFrame) -> float:
    """
    Mediana para dados agrupados:
    1) Calcula Fac (frequência acumulada);
    2) Encontra a classe onde Fac >= N/2;
    3) Aplica interpolação linear: Med = L + ((N/2 - F_anterior)/f_classe)*h.
    """
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
    """
    Moda para dados agrupados (bruta e Czuber):
    - 'modas_brutas' = ponto médio da(s) classe(s) com fi máxima;
    - 'modas_czuber' = interpolação de Czuber:
        Mo ≈ Li + (d1/(d1+d2)) * h, onde d1 = f_modal - f_prev e d2 = f_modal - f_next.
      Neste código, quando (d1+d2) <= 0 (ex.: planalto/empate), retorna None (N/A).
      Obs.: se quiser a REGRA RIGOROSA dos vizinhos (pico local estrito), troque a
      checagem por:
         if f_prev is not None and f_next is not None and (f_modal > f_prev) and (f_modal > f_next):
            ...
         else:
            modas_czuber.append(None)
    - 'tipo_moda' classifica uni/bi/tri/.../multimodal segundo o nº de classes modais.
    """
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
        # Moda bruta (ponto médio)
        modas_brutas.append((Li + Ls) / 2)
        
        f_modal = float(t.at[pos, "fi"])
        f_prev = float(t.at[pos - 1, "fi"]) if pos - 1 >= 0 else 0.0
        f_next = float(t.at[pos + 1, "fi"]) if pos + 1 < len(t) else 0.0
        
        d1, d2 = f_modal - f_prev, f_modal - f_next

        # Czuber definida somente se (d1 + d2) > 0 (evita divisão por zero/planaltos)
        # (Para a regra rigorosa de pico local, veja comentário no docstring acima.)
        if (d1 + d2) > 0:
            moda_cz = Li + (d1 / (d1 + d2)) * h_classe
            modas_czuber.append(arredondar(moda_cz))
        else:
            modas_czuber.append(None)
            
    return modas_brutas, modas_czuber, tipo_moda


def variancia_agrupada(df: pd.DataFrame, media: float) -> float:
    """
    Variância amostral para dados agrupados (dividindo por N-1).
    Usa Pmi como representante da classe.
    """
    N = df["fi"].sum()
    if N <= 1:
        raise ValueError("A amostra precisa ter mais de um elemento para calcular a variância.")
    
    if "Pmi" not in df.columns:
         df["Pmi"] = (df["Li"] + df["Ls"]) / 2
         
    variancia = (((df["Pmi"] - media)**2) * df["fi"]).sum() / (N - 1)
    return arredondar(variancia)


# -------------------------------
# Configuração e estilo da página
# -------------------------------
st.set_page_config(page_title="Estatística", page_icon="heavy_plus_sign", layout="wide")

# Seeds para recriar widgets ao limpar (evita mexer em keys já instanciadas)
if "text_area1_seed" not in st.session_state:
    st.session_state["text_area1_seed"] = 0
if "editor_discreto_seed" not in st.session_state:
    st.session_state["editor_discreto_seed"] = 0

# DF persistente para o editor do discreto (evita depender do estado interno do widget)
if "df_discreto" not in st.session_state:
    st.session_state.df_discreto = pd.DataFrame({"xi": [None], "fi": [None]})

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


# -------------------------------
# Cabeçalho
# -------------------------------
st.title(":red[Bem vindo ao site de Estatística]", anchor=None)
st.subheader("Esta aplicação é uma calculadora que utiliza agrupamentos discreto e por classes para calcular: ")
st.markdown("##### Cálculo de média - Mediana - Modas - Variância - Desvio Padrão - Coeficiente de Variação")
st.markdown(":gray[_Criado por Andriy Tam, Henrique Sabino, Paulo Santos e Luis Carlos Oliveira_]")
st.divider()


# -------------------------------
# Abas principais
# -------------------------------
aba_principal1, aba_principal2 = st.tabs(["Agrupamento Discreto", "Agrupamento por Classes"])


# =====================================================================================
# ABA 1: Agrupamento Discreto
# =====================================================================================
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
    tab1, tab2 = st.tabs(["Tabela (xᵢ, fᵢ)", "Lista de valores"])

    # CSS para o rótulo das subtabs (menor)
    st.markdown("""
    <style>
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------------------------
    # Tab 1: entrada por tabela
    # ---------------------------
    with tab1:
        base = pd.DataFrame({"xi": [None], "fi": [None]})
        clear_tab1 = False  # [Limpar] default
        with st.form("form_tabela"):
            st.markdown("#### Para adicionar mais linhas, **clique no `+` abaixo da tabela**.")
            edited = st.data_editor(
                st.session_state.df_discreto,
                num_rows="dynamic",          # permite adicionar/remover linhas
                use_container_width=True,
                column_config={
                    "xi": st.column_config.NumberColumn("xᵢ"),
                    "fi": st.column_config.NumberColumn("Frequência(fᵢ)", min_value=0, step=1),
                },
                key=f"editor_discreto_{st.session_state['editor_discreto_seed']}"  # seed na key
            )

            # [LIMPAR] botão logo abaixo da tabela
            clear_tab1 = st.form_submit_button("Limpar tabela", type="secondary", use_container_width=True)
            
            # Seleção de medidas a serem calculadas
            st.markdown("### Selecione o que deseja calcular: ")
            mediacbx = st.checkbox("Média") 
            medianacbx = st.checkbox("Mediana")
            modacbx = st.checkbox("Moda")
            varianciacbx = st.checkbox("Variância")
            desviopadraocbx = st.checkbox("Desvio Padrão")
            coeficientecbx = st.checkbox("Coeficiente de Variação")
            
            # Botão Calcular sozinho
            sub = st.form_submit_button("Calcular", use_container_width=True)

        # [Limpar] reset do editor após o form (recria o widget e zera o DF)
        if clear_tab1:
            st.session_state.df_discreto = base.copy()
            st.session_state["editor_discreto_seed"] += 1
            st.rerun()

        # Atualiza DF persistente com o que está na tela
        st.session_state.df_discreto = edited.copy()

        # Processamento ao clicar em "Calcular"
        if sub:
            try:
                # Limpa linhas vazias e força numérico
                edited_num = edited.dropna().astype(float)

                # Cálculos principais
                m = arredondar(media_ponderada_df(edited_num), 2)
                me = arredondar(mediana_df(edited_num), 2)
                modais, tipo = moda_df(edited_num)
                variance = arredondar(variancia_df(edited_num), 2)
                desvio_padrao = arredondar(math.sqrt(variance), 2)
                cv = (100 * desvio_padrao) / m
                coeficiente_variacao = arredondar(cv, 2)
                
                # Impressão em 2 colunas (usa st.success para não truncar texto)
                cards = []
                if mediacbx:        cards.append(("Média", f"{m:.2f}"))
                if medianacbx:      cards.append(("Mediana", f"{me:.2f}"))
                if varianciacbx:    cards.append(("Variância", f"{variance:.2f}"))
                if desviopadraocbx: cards.append(("Desvio Padrão", f"{desvio_padrao:.2f}"))
                if coeficientecbx:  cards.append(("Coeficiente de Variação", f"{coeficiente_variacao:.2f}%"))
                if modacbx:         cards.append((f"Moda ({tipo})", ", ".join(f"{x:.2f}" for x in modais)))

                cols = st.columns(2)
                for i, (titulo, valor) in enumerate(cards):
                    with cols[i % 2]:
                        st.success(f"**{titulo}:** {valor}")
                    
            except Exception as e:
                # Mostra aviso amigável (sem stacktrace)
                st.warning(str(e))
    

    # ---------------------------
    # Tab 2: entrada por texto
    # ---------------------------
    with tab2:
        clear_text = False  # [Limpar] default
        with st.form("form_texto"):
            # Aumenta a fonte/altura da área de texto
            st.markdown("""
            <style>
            [data-testid="stTextArea"] textarea {
                font-size: 22px !important;
                height: 150px;
            }
            </style>
            """, unsafe_allow_html=True)

            st.subheader("Digite os números a serem calculados separados por espaço")
            # Usa seed na key para recriar o widget ao limpar (evita modificar uma key já instanciada)
            s = st.text_area(label=' ', key=f'text_area1_{st.session_state["text_area1_seed"]}')
            st.caption(f"### Números a serem calculados: {s}")

            # [LIMPAR] botão logo abaixo da área de texto
            clear_text = st.form_submit_button("Limpar entrada", type="secondary", use_container_width=True)
            
            # Seleção de medidas
            st.markdown("### Selecione o que deseja calcular: ")
            mediacbx = st.checkbox("Média") 
            medianacbx = st.checkbox("Mediana")
            modacbx = st.checkbox("Moda")
            varianciacbx = st.checkbox("Variância")
            desviopadraocbx = st.checkbox("Desvio Padrão")
            coeficientecbx = st.checkbox("Coeficiente de Variação")
            
            # Botão Calcular sozinho
            sub2 = st.form_submit_button("Calcular", use_container_width=True)

        # [Limpar] recria o text_area com nova key (sem tocar na key já instanciada)
        if clear_text:
            st.session_state["text_area1_seed"] += 1
            st.rerun()

        if sub2:
            try:
                # Converte string para lista de floats (aceita vírgula/ponto)
                nums = parse_numeros(s)
                if not nums:
                    raise ValueError("Nenhum número encontrado.")

                # Constrói frequência e ordena (xi, fi)
                freq = Counter(nums)
                df_freq = pd.DataFrame(sorted(freq.items()), columns=["xi", "fi"])
                
                # Cálculos
                m = arredondar(media_ponderada_df(df_freq), 2)
                me = arredondar(mediana_df(df_freq), 2)
                modais, tipo = moda_df(df_freq)
                variance = arredondar(variancia_df(df_freq), 2)
                desvio_padrao = arredondar(math.sqrt(variance), 2)
                cv = (100 * desvio_padrao) / m
                coeficiente_variacao = arredondar(cv, 2)
                
                # Impressão em 2 colunas (sem truncar)
                cards = []
                if mediacbx:        cards.append(("Média", f"{m:.2f}"))
                if medianacbx:      cards.append(("Mediana", f"{me:.2f}"))
                if varianciacbx:    cards.append(("Variância", f"{variance:.2f}"))
                if desviopadraocbx: cards.append(("Desvio Padrão", f"{desvio_padrao:.2f}"))
                if coeficientecbx:  cards.append(("Coeficiente de Variação", f"{coeficiente_variacao:.2f}%"))
                if modacbx:         cards.append((f"Moda ({tipo})", ", ".join(f"{x:.2f}" for x in modais)))

                cols = st.columns(2)
                for i, (titulo, valor) in enumerate(cards):
                    with cols[i % 2]:
                        st.success(f"**{titulo}:** {valor}")
                
            except Exception as e:
                st.error(f"Entrada inválida: {e}")


# =====================================================================================
# ABA 2: Agrupamento por Classes
# =====================================================================================
with aba_principal2:
    st.subheader("Agrupamento por Classes")
    st.markdown(
        "Preencha `Li` e `Ls` na primeira linha. "
        "Clique em **Adicionar classe (+)** para criar a próxima com o mesmo `h = Ls − Li`."
    )

    # DataFrame da sessão para persistir a tabela entre reruns
    if 'df_classes' not in st.session_state:
        st.session_state.df_classes = pd.DataFrame([{"Li": None, "Ls": None, "fi": None}])

    clear_classes = False  # [Limpar] default

    # Um único form combina: editor + botão adicionar + checkboxes + calcular
    with st.form("form_classes_all", clear_on_submit=False):
        edited_df = st.data_editor(
            st.session_state.df_classes,
            num_rows="fixed",                # sem '+' nativo do editor (vamos controlar pelo botão)
            use_container_width=True,
            column_config={
                # Exibição como inteiros (format="%d"); step=1 para facilitar digitação
                "Li": st.column_config.NumberColumn("Limite Inferior (lᵢ)", format="%d", step=1),
                "Ls": st.column_config.NumberColumn("Limite Superior (lₛ)", format="%d", step=1),
                "fi": st.column_config.NumberColumn("Frequência (fi)", min_value=0, step=1, format="%d"),
            },
            key="editor_classes"
        )

        # Botões logo abaixo da tabela
        add_clicked = st.form_submit_button("Adicionar classe (+)", use_container_width=True)
        clear_classes = st.form_submit_button("Limpar tabela", type="secondary", use_container_width=True)

        # Checkboxes para escolher o que calcular
        st.markdown("### Selecione o que deseja calcular: ")
        mediacbx        = st.checkbox("Média")
        medianacbx      = st.checkbox("Mediana")
        modabrutacbx    = st.checkbox("Moda Bruta")
        modaczubercbx   = st.checkbox("Moda de Czuber")
        varianciacbx    = st.checkbox("Variância")
        desviopadraocbx = st.checkbox("Desvio Padrão")
        coeficientecbx  = st.checkbox("Coeficiente de Variação")

        # Botão Calcular sozinho
        calc_clicked = st.form_submit_button("Calcular", use_container_width=True)

    # ---------------------------
    # [Limpar] reset da tabela de classes
    # ---------------------------
    if clear_classes:
        st.session_state.df_classes = pd.DataFrame([{"Li": None, "Ls": None, "fi": None}])
        if "editor_classes" in st.session_state:
            del st.session_state["editor_classes"]  # limpa estado do widget
        st.rerun()

    # ---------------------------
    # Lógica do botão (+)
    # ---------------------------
    if add_clicked:
        # 'edited_df' já traz o que está na tela (confirmado ao enviar o form)
        base_cls = edited_df.copy()

        # Converte colunas para numérico, ignorando erros
        tmp = base_cls.copy()
        tmp["Li"] = pd.to_numeric(tmp["Li"], errors="coerce")
        tmp["Ls"] = pd.to_numeric(tmp["Ls"], errors="coerce")

        # Considera apenas linhas com Li e Ls válidos para calcular h
        comp = tmp.dropna(subset=["Li", "Ls"])
        if not comp.empty:
            last_idx = comp.index.max()              # última linha completa
            prev_Li  = int(round(tmp.loc[last_idx, "Li"]))
            prev_Ls  = int(round(tmp.loc[last_idx, "Ls"]))
            h_int    = int(round(prev_Ls - prev_Li)) # largura de classe como inteiro

            # Se h > 0, cria próxima classe [prev_Ls, prev_Ls + h]
            if h_int > 0:
                new_row = {"Li": prev_Ls, "Ls": prev_Ls + h_int, "fi": None}
            else:
                # Se não houver h válido, adiciona linha vazia
                new_row = {"Li": None, "Ls": None, "fi": None}
        else:
            # Se não houver nenhuma linha completa, adiciona linha vazia
            new_row = {"Li": None, "Ls": None, "fi": None}

        # Persiste a nova linha no session_state e força rerun para atualizar a UI
        st.session_state.df_classes = pd.concat([base_cls, pd.DataFrame([new_row])], ignore_index=True)
        st.rerun()

    # ---------------------------
    # Lógica do botão "Calcular"
    # ---------------------------
    if calc_clicked:
        try:
            # Copia os dados do editor e força para numérico
            tabela_classes = edited_df.copy()
            tabela_classes["Li"] = pd.to_numeric(tabela_classes["Li"], errors="coerce")
            tabela_classes["Ls"] = pd.to_numeric(tabela_classes["Ls"], errors="coerce")
            tabela_classes["fi"] = pd.to_numeric(tabela_classes["fi"], errors="coerce")

            # Mantém apenas linhas com Li, Ls e fi preenchidos
            tabela_classes = tabela_classes.dropna(subset=["Li", "Ls", "fi"]).astype(float)

            if tabela_classes.empty:
                raise ValueError("A tabela está vazia ou contém dados inválidos.")

            # Cálculos principais
            media = media_agrupada(tabela_classes)
            mediana = mediana_agrupada(tabela_classes)
            modas_brutas, modas_czuber, tipo_moda = moda_agrupada(tabela_classes)
            variancia = variancia_agrupada(tabela_classes, media)
            desvio_padrao = arredondar(math.sqrt(variancia))
            coeficiente_variacao = arredondar((100 * desvio_padrao) / media, 2) if media != 0 else None

            # Impressão em 2 colunas (st.success evita truncar)
            cards = []
            if mediacbx:        cards.append(("Média", f"{media:.2f}"))
            if medianacbx:      cards.append(("Mediana", f"{mediana:.2f}"))
            if varianciacbx:    cards.append(("Variância", f"{variancia:.2f}"))
            if desviopadraocbx: cards.append(("Desvio Padrão", f"{desvio_padrao:.2f}"))
            if coeficientecbx:  cards.append(("Coeficiente de Variação", f"{coeficiente_variacao:.2f}%" if coeficiente_variacao is not None else "Indefinido"))
            if modabrutacbx:    cards.append((f"Moda Bruta ({tipo_moda})", ", ".join(f"{m:.2f}" for m in modas_brutas)))
            # Para Czuber, valores None aparecem como "N/A"
            if modaczubercbx:   cards.append(("Moda de Czuber", ", ".join("N/A" if m is None else f"{m:.2f}" for m in modas_czuber)))

            cols = st.columns(2)
            for i, (titulo, valor) in enumerate(cards):
                with cols[i % 2]:
                    st.success(f"**{titulo}:** {valor}")

        except Exception as e:
            st.error(f"Erro: {e}")
