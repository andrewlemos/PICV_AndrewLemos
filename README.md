# Controle de Qualidade, Homogeneização e Análise de Séries Meteorológicas do CEPAGRI/UNICAMP

Repositório do projeto de **Iniciação Científica Voluntária (PICV)** vinculado ao **Centro de Pesquisas Meteorológicas e Climáticas Aplicadas à Agricultura (CEPAGRI)** da **Universidade Estadual de Campinas (UNICAMP)**.

---

##  Sobre o Projeto

Este trabalho tem como foco a **recuperação, o controle de qualidade e a análise de dados meteorológicos de superfície** da estação do CEPAGRI/UNICAMP.

O objetivo principal é consolidar uma base de dados meteorológicos tratada e consistente a partir dos registros originais, avaliando possíveis quebras na série temporal — como a mudança de sítio da estação em maio de 2013 — e permitindo estudos futuros sobre **tendências climáticas e eventos extremos em Campinas-SP**.

###  Equipe

* **Aluno:** Andrew Filipe Moreira Lemos
* **Orientadora:** Profª. Drª. Ana Maria H. de Avila
* **Coorientador:** Me. Bruno Kabke Bainy

---

##  Arquivos Disponíveis

| Arquivo                                                | Descrição                                                                                                               |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| `dados_processados_EMA_2013a18.xlsx`                   | Registros originais da Estação Meteorológica Automática (EMA) referentes ao período de maio de 2013 a dezembro de 2018. |
| `Dados_Processados_EMA_2019a2025 .xlsx`                | Registros originais da EMA referentes ao período de janeiro de 2019 a dezembro de 2025.                                 |
| `inventário_manutencoes_EMA (1).xlsx`                  | Histórico cronológico de intervenções, calibrações e substituições de sensores da estação.                              |
| `Gabriela_Trindade_Mensais1989a2023 (1).xlsx`          | Compilação histórica preliminar utilizada como referência externa comparativa.                                          |
| `PICV_Andrew_Lemos_CEPAGRI_UNICAMP_final_hist (1).pdf` | Documento formal contendo a proposta e o cronograma do projeto de pesquisa.                                             |

---

##  Etapa Concluída: Padronização e Fusão da Série Subdiária

Foi desenvolvido e executado um pipeline para a **ingestão e unificação dos dados brutos**, com resolução temporal de **10 minutos**, abrangendo o período de **2013 a 2025**.

###  Scripts

* **Padronização e fusão:** `Padronização e Fusão das Séries Temporais.py`
* **Arquivo gerado:** `ema_campinas_10min_2013_2025_bruta.parquet`
* **Inspeção estrutural:** `inspecionar_parquet.py`
* **Fatiador e exportador CLI:** `exportar_amostra.py` — extrai recortes temporais parametrizados via terminal em `.xlsx` ou `.csv`.

###  Principais Ações Realizadas

1. **Reconstrução dos carimbos de data e hora**

   Reconstrução dos registros temporais a partir do padrão utilizado pelos sistemas Campbell Scientific:

   `Ano + Dia Juliano + HoraMinuto`

   O processamento também trata as ocorrências de `2400h` e elimina inconsistências residuais provenientes das planilhas originais.

2. **Harmonização das variáveis**

   Padronização dos diferentes nomes utilizados para as mesmas variáveis meteorológicas, por exemplo:

   * `T` → `temperatura`
   * `Temperatura (°C)` → `temperatura`
   * `UR` → `umidade_relativa`
   * `Umidade relativa (%)` → `umidade_relativa`

   O resultado utiliza um **esquema canônico em `snake_case`**.

3. **Regularização da série temporal**

   As observações são alinhadas em um índice temporal contínuo com intervalo regular de **10 minutos**, utilizando `pd.date_range`.

   Dessa forma, os períodos sem observações ficam explicitamente representados como `NaN`, permitindo que as falhas da série sejam identificadas e posteriormente submetidas às etapas de controle de qualidade.

---

##  Como Executar

### 1. Requisitos

O projeto requer **Python 3.10+** e as seguintes bibliotecas para manipulação e serialização dos dados:

* `pandas`
* `openpyxl`
* `pyarrow`

Instale as dependências com:

```powershell
pip install pandas openpyxl pyarrow
```

### 2. Gerar a Base Parquet Unificada

Execute o pipeline principal de ingestão e limpeza temporal:

```powershell
python "Padronização e Fusão das Séries Temporais.py"
```

O processamento gera o arquivo colunar comprimido:

```text
ema_campinas_10min_2013_2025_bruta.parquet
```

### 3. Inspecionar a Integridade dos Dados

Para auditar rapidamente os tipos de dados, o total de registros faltantes (`NaN`) e estatísticas descritivas básicas no terminal:

```powershell
python inspecionar_parquet.py
```

### 4. Exportar Amostras e Séries Históricas

O script `exportar_amostra.py` permite **fatiar qualquer janela temporal da base bruta diretamente pela linha de comando**, sem necessidade de editar o código-fonte.

O resultado pode ser exportado em formato tabular para **validações externas, inspeções ou análises pontuais**.

#### Parâmetros Disponíveis

| Argumento        | Tipo        | Descrição                                              | Exemplo              |
| ---------------- | ----------- | ------------------------------------------------------ | -------------------- |
| `-i`, `--inicio` | Obrigatório | Data/hora inicial (`YYYY-MM-DD` ou `YYYY-MM-DD HH:MM`) | `2024-01-01`         |
| `-f`, `--fim`    | Obrigatório | Data/hora final (`YYYY-MM-DD` ou `YYYY-MM-DD HH:MM`)   | `2024-12-31`         |
| `--formato`      | Opcional    | Formato de saída: `xlsx` (padrão) ou `csv`             | `--formato csv`      |
| `-o`, `--saida`  | Opcional    | Nome personalizado do arquivo gerado                   | `-o serie_2024.xlsx` |

> **Nota:** Para recortes volumosos com mais de **1.048.576 linhas**, utilize obrigatoriamente `--formato csv`, respeitando o limite físico de linhas das planilhas do Excel.

Os arquivos CSV são gravados com:

* codificação `utf-8-sig`;
* delimitador `;`;
* vírgula como separador decimal.

Essa configuração proporciona compatibilidade direta com versões em português do **Microsoft Excel** e do **LibreOffice Calc**.

### Exemplos de Uso no PowerShell

#### Exportar um ano completo em Excel (`.xlsx`)

```powershell
python exportar_amostra.py -i 2024-01-01 -f 2024-12-31
```

#### Exportar um mês específico em CSV (`.csv`)

```powershell
python exportar_amostra.py -i 2023-10-01 -f 2023-10-31 --formato csv
```

#### Exportar um evento extremo com intervalo horário e nome personalizado

```powershell
python exportar_amostra.py -i "2024-01-15 00:00" -f "2024-01-15 23:50" -o tempestade_15jan.xlsx
```

#### Consultar o manual de ajuda integrado

```powershell
python exportar_amostra.py --help
```

---

##  Estrutura do Processamento

O fluxo atual do projeto pode ser representado da seguinte forma:

```text
Dados originais
      │
      ▼
┌─────────────────────────┐
│ Ingestão das planilhas  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Reconstrução temporal   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Padronização das        │
│ variáveis               │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Regularização em        │
│ intervalos de 10 min    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Base Parquet bruta      │
│ 2013–2025               │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Inspeção e auditoria    │
│ estrutural              │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Exportação de recortes  │
│ temporais via CLI       │
└─────────────────────────┘
```

---

##  Próximas Etapas

As próximas etapas do projeto incluem:

* Controle de qualidade dos dados meteorológicos;
* Identificação e tratamento de valores discrepantes;
* Avaliação de falhas e períodos sem observações;
* Investigação de alterações instrumentais e de sítio;
* Homogeneização das séries temporais;
* Análise estatística e climatológica;

---

##  Instituição

**Centro de Pesquisas Meteorológicas e Climáticas Aplicadas à Agricultura — CEPAGRI**

**Universidade Estadual de Campinas — UNICAMP**

Campinas — São Paulo — Brasil
