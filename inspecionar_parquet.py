import pandas as pd

# 1. Carregar o arquivo Parquet
df = pd.read_parquet("ema_campinas_10min_2013_2025_bruta.parquet")

# 2. Informações estruturais (tipos de dados, memória, colunas)
print("=== INFORMAÇÕES ESTRUTURAIS ===")
print(df.info())

# 3. Primeiras e últimas linhas
print("\n=== PRIMEIROS REGISTROS ===")
print(df.head())

print("\n=== ÚLTIMOS REGISTROS ===")
print(df.tail())

# 4. Resumo estatístico descritivo das variáveis meteorológicas
print("\n=== ESTATÍSTICA DESCRITIVA ===")
print(df.describe().T[['count', 'mean', 'std', 'min', '50%', 'max']])