Script Utilitário: exportar_amostra.py
Exporta recortes temporais da série bruta da EMA via linha de comando.
"""

import argparse
import sys
import pandas as pd


def exportar_amostra(data_inicio: str, data_fim: str, formato: str, saida: str | None = None):
    caminho_parquet = "ema_campinas_10min_2013_2025_bruta.parquet"

    print(f"-> Carregando base: {caminho_parquet}...")
    try:
        df = pd.read_parquet(caminho_parquet)
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_parquet}' não foi encontrado na pasta atual.")
        sys.exit(1)

    print(f"-> Recortando intervalo de {data_inicio} até {data_fim}...")
    # Recorte temporal no DatetimeIndex
    df_recorte = df.loc[data_inicio:data_fim]

    total_linhas = len(df_recorte)
    if total_linhas == 0:
        print("Aviso: Nenhum registro foi encontrado para o intervalo informado.")
        sys.exit(0)

    # Define nome padrão do arquivo se não for fornecido
    if not saida:
        inicio_str = data_inicio.replace(":", "").replace(" ", "_")
        fim_str = data_fim.replace(":", "").replace(" ", "_")
        saida = f"amostra_ema_{inicio_str}_a_{fim_str}.{formato}"

    print(f"-> Exportando {total_linhas:,} linhas para '{saida}'...")

    if formato == "xlsx":
        # Limite máximo de linhas de uma planilha Excel
        if total_linhas > 1_048_576:
            print(
                "Erro: O intervalo contém mais de 1.048.576 linhas, excedendo o limite do Excel. "
                "Use o formato 'csv' para esse volume."
            )
            sys.exit(1)
        df_recorte.to_excel(saida)
    elif formato == "csv":
        df_recorte.to_csv(saida, sep=";", decimal=",", encoding="utf-8-sig")

    print(f"Sucesso! Arquivo '{saida}' gerado com êxito.")


def main():
    parser = argparse.ArgumentParser(
        description="Fatiador e exportador de amostras da série temporal da EMA (CEPAGRI/UNICAMP)."
    )

    parser.add_argument(
        "-i", "--inicio",
        required=True,
        help="Data inicial no formato YYYY-MM-DD ou YYYY-MM-DD HH:MM (ex: 2024-01-01)"
    )
    parser.add_argument(
        "-f", "--fim",
        required=True,
        help="Data final no formato YYYY-MM-DD ou YYYY-MM-DD HH:MM (ex: 2024-12-31)"
    )
    parser.add_argument(
        "--formato",
        choices=["xlsx", "csv"],
        default="xlsx",
        help="Formato do arquivo exportado (padrão: xlsx)"
    )
    parser.add_argument(
        "-o", "--saida",
        default=None,
        help="Nome personalizado para o arquivo de saída (opcional)"
    )

    args = parser.parse_args()
    exportar_amostra(args.inicio, args.fim, args.formato, args.saida)


if __name__ == "__main__":
    main()