"""
PICV - CEPAGRI / UNICAMP
Módulo: 01_padronizacao_fusao_ema.py
Descrição: Processamento, higienização temporal e fusão das séries de 10 minutos
           da Estação Meteorológica Automática (EMA) de 2013 a 2025.
"""

from datetime import datetime, timedelta
import numpy as np
import pandas as pd


def parse_campbell_horamin(hora_val) -> tuple[int, int]:
    """Converte o formato de hora inteiro da Campbell (ex: 10, 50, 1340, 2400)

    ou time em (horas, minutos, flag_virada_dia).
    """
    if pd.isna(hora_val):
        return (0, 0, 0)

    if isinstance(hora_val, str):
        # Caso venha como string "20:10:00"
        parts = hora_val.split(":")
        return (int(parts[0]), int(parts[1]), 0)

    if hasattr(hora_val, "hour"):  # datetime.time
        return (hora_val.hour, hora_val.minute, 0)

    # Caso seja inteiro Campbell (ex: 2400 -> 24h 00min)
    h_int = int(hora_val)
    if h_int == 2400:
        return (23, 59, 1)  # Marca para virada ou fechamento do dia civil

    horas = h_int // 100
    minutos = h_int % 100
    return (horas, minutos, 0)


def processar_serie_2013_2018(caminho_arquivo: str) -> pd.DataFrame:
    """Carrega e padroniza os dados subdiários de 2013 a 2018."""
    print("-> Carregando base 2013-2018 (Dados_10minutos)...")
    df = pd.read_excel(caminho_arquivo, sheet_name="Dados_10minutos")

    # Tratamento seguro da data e hora: reconstrói via Ano + Dia Juliano + HoraMin
    # para evitar os erros '#VALUE!' encontrados na coluna 'Data e hora'
    timestamps = []
    for _, row in df[["Ano", "Dia_Juliano", "HoraMin"]].iterrows():
        try:
            ano = int(row["Ano"])
            dia_jul = int(row["Dia_Juliano"])
            base_date = datetime(ano, 1, 1) + timedelta(days=dia_jul - 1)

            if hasattr(row["HoraMin"], "hour"):
                h, m = row["HoraMin"].hour, row["HoraMin"].minute
            elif isinstance(row["HoraMin"], str):
                parts = row["HoraMin"].split(":")
                h, m = int(parts[0]), int(parts[1])
            else:
                h_int = int(row["HoraMin"])
                h, m = h_int // 100, h_int % 100

            # Arredonda segundos/frações para a grade de 10 min exata
            m = round(m / 10) * 10
            if m == 60:
                h += 1
                m = 0
            ts = base_date.replace(hour=h % 24, minute=m, second=0)
            if h >= 24:
                ts += timedelta(days=1)
            timestamps.append(ts)
        except Exception:
            timestamps.append(pd.NaT)

    df["timestamp"] = timestamps

    # Seleção e renomeação uniforme de colunas (Padrão snake_case)
    col_map = {
        "T": "temperatura",
        "UR": "umidade_relativa",
        "Chuva": "precipitacao",
        "V5m": "vento_vel_5m",
        "V2m": "vento_vel_2m",
        "Dir": "vento_direcao",
    }

    df_clean = df[list(col_map.keys()) + ["timestamp"]].rename(columns=col_map)
    df_clean.dropna(subset=["timestamp"], inplace=True)
    return df_clean


def processar_serie_2019_2025(caminho_arquivo: str) -> pd.DataFrame:
    """Carrega e padroniza os dados subdiários de 2019 a 2025 (Tabela 111)."""
    print("-> Carregando base 2019-2025 (Dados_111)...")
    df = pd.read_excel(caminho_arquivo, sheet_name="Dados_111")

    # Reconstrói timestamps a partir de 'Data' e 'HoraMinuto' (formato Campbell)
    timestamps = []
    for _, row in df[["Data", "HoraMinuto"]].iterrows():
        try:
            d = pd.to_datetime(row["Data"])
            hm = int(row["HoraMinuto"])
            if hm == 2400:
                # 2400h do dia D é equivalente a 00:00 do dia D+1
                ts = d + timedelta(days=1)
            else:
                h = hm // 100
                m = hm % 100
                ts = d.replace(hour=h, minute=m, second=0)
            timestamps.append(ts)
        except Exception:
            timestamps.append(pd.NaT)

    df["timestamp"] = timestamps

    col_map = {
        "Temperatura (°C)": "temperatura",
        "Umidade relativa (%)": "umidade_relativa",
        "Precipitação (mm)": "precipitacao",
        "Velocidade do vento (m/s)": "vento_vel_5m",
        "Rajada (m/s)": "vento_rajada",
        "Direção do vento (°)": "vento_direcao",
        "Índice UV": "indice_uv",
    }

    cols_existentes = [c for c in col_map.keys() if c in df.columns]
    df_clean = df[cols_existentes + ["timestamp"]].rename(columns=col_map)
    df_clean.dropna(subset=["timestamp"], inplace=True)
    return df_clean


def fundir_series_meteorologicas(
    caminho_13_18: str, caminho_19_25: str, exportar_parquet: bool = True
) -> pd.DataFrame:
    """Unifica e indexa a série contínua com resolução de 10 minutos (2013-2025)."""
    df_13 = processar_serie_2013_2018(caminho_13_18)
    df_19 = processar_serie_2019_2025(caminho_19_25)

    print("-> Concatenando séries e eliminando duplicatas temporais...")
    df_merged = pd.concat([df_13, df_19], ignore_index=True)

    # Conversão de tipos numéricos forçada (elimina strings residuais)
    variaveis_numericas = [
        "temperatura",
        "umidade_relativa",
        "precipitacao",
        "vento_vel_5m",
        "vento_vel_2m",
        "vento_rajada",
        "vento_direcao",
        "indice_uv",
    ]
    for col in variaveis_numericas:
        if col in df_merged.columns:
            df_merged[col] = pd.to_numeric(df_merged[col], errors="coerce")

    # Ordenação cronológica e remoção de duplicatas exatas de timestamp
    df_merged.sort_values(by="timestamp", inplace=True)
    df_merged.drop_duplicates(subset=["timestamp"], keep="last", inplace=True)

    # Configuração do índice temporal formal
    df_merged.set_index("timestamp", inplace=True)

    # Criação do grid contínuo de 10 minutos para explicitar todas as falhas
    start_time = df_merged.index.min()
    end_time = df_merged.index.max()
    full_index = pd.date_range(
        start=start_time, end=end_time, freq="10min", name="timestamp"
    )
    df_completo = df_merged.reindex(full_index)

    print("\n" + "=" * 50)
    print("RELATÓRIO DE INTEGRAÇÃO DA SÉRIE BRUTA (10 MIN)")
    print("=" * 50)
    print(f"Período temporal: {start_time} até {end_time}")
    print(f"Total de registros esperados no grid contínuo: {len(full_index):,}")
    print(
        f"Total de registros presentes: {df_completo['temperatura'].count():,}"
    )
    print(
        f"Total de registros faltantes: {df_completo['temperatura'].isna().sum():,} "
        f"({(df_completo['temperatura'].isna().mean()*100):.2f}%)"
    )
    print("=" * 50)

    if exportar_parquet:
        # Recomenda-se formato Parquet para bases subdiárias grandes (mais leve e preserva tipos)
        df_completo.to_parquet(
            "ema_campinas_10min_2013_2025_bruta.parquet", compression="snappy"
        )
        print(
            "Arquivo salvo com sucesso: 'ema_campinas_10min_2013_2025_bruta.parquet'"
        )

    return df_completo


if __name__ == "__main__":
    arq_2013 = "dados_processados_EMA_2013a18.xlsx"
    arq_2019 = "Dados_Processados_EMA_2019a2025 .xlsx"

    df_serie_unificada = fundir_series_meteorologicas(arq_2013, arq_2019)