# funcoes.py
import re
import math
import statistics
import pandas as pd
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP

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