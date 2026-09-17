import pandas as pd

df = pd.read_parquet("ema_campinas_10min_2013_2025_bruta.parquet")

# Exemplo: Exportar apenas o ano de 2024 para conferência rápida no Excel
df_2024 = df.loc['2024-01-01':'2024-12-31']
df_2024.to_excel("amostra_ema_2024.xlsx")
print("Amostra de 2024 salva em Excel!")