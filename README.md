# Controle de Qualidade, Homogeneização e Análise de Séries Meteorológicas do CEPAGRI/UNICAMP

Repositório do projeto de **Iniciação Científica Voluntária (PICV)** vinculado ao **Centro de Pesquisas Meteorológicas e Climáticas Aplicadas à Agricultura (CEPAGRI)** da **Universidade Estadual de Campinas (UNICAMP)**.

---

## 📌 Sobre o Projeto

Este trabalho tem como foco a **recuperação, o controle de qualidade e a análise de dados meteorológicos de superfície** da estação do CEPAGRI/UNICAMP.

O objetivo principal é consolidar uma base de dados meteorológicos tratada e consistente a partir dos registros originais, avaliando possíveis quebras na série temporal — como a mudança de sítio da estação em maio de 2013 — e permitindo estudos futuros sobre **tendências climáticas e eventos extremos em Campinas-SP**.

### 👨‍🔬 Equipe

* **Aluno:** Andrew Filipe Moreira Lemos
* **Orientadora:** Profª. Drª. Ana Maria H. de Avila
* **Coorientador:** Me. Bruno Kabke Bainy

---

## 📂 Arquivos Disponíveis

| Arquivo                                                | Descrição                                                                                                               |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| `dados_processados_EMA_2013a18.xlsx`                   | Registros originais da Estação Meteorológica Automática (EMA) referentes ao período de maio de 2013 a dezembro de 2018. |
| `Dados_Processados_EMA_2019a2025 .xlsx`                | Registros originais da EMA referentes ao período de janeiro de 2019 a dezembro de 2025.                                 |
| `inventário_manutencoes_EMA (1).xlsx`                  | Histórico cronológico de intervenções, calibrações e substituições de sensores da estação.                              |
| `Gabriela_Trindade_Mensais1989a2023 (1).xlsx`          | Compilação histórica preliminar utilizada como referência externa comparativa.                                          |
| `PICV_Andrew_Lemos_CEPAGRI_UNICAMP_final_hist (1).pdf` | Documento formal contendo a proposta e o cronograma do projeto de pesquisa.                                             |

---

## ⚙️ Etapa Concluída: Padronização e Fusão da Série Subdiária

Foi desenvolvido e executado um script para a **ingestão e unificação dos dados brutos**, com resolução temporal de **10 minutos**, abrangendo o período de **2013 a 2025**.

### 🐍 Scripts

* **Padronização e fusão:** `Padronização e Fusão das Séries Temporais.py`
* **Arquivo gerado:** `ema_campinas_10min_2013_2025_bruta.parquet`
* **Inspeção:** `inspecionar_parquet.py`

### 🔧 Principais Ações Realizadas

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

## 🚀 Como Executar

### 1. Requisitos

O projeto utiliza Python e as seguintes bibliotecas:

* `pandas`
* `openpyxl`
* `pyarrow`

Instale todas elas com:

```powershell
pip install pandas openpyxl pyarrow
```

### 2. Gerar a Base Parquet

Execute o script principal:

```powershell
python "Padronização e Fusão das Séries Temporais.py"
```

O processamento deverá gerar:

```text
ema_campinas_10min_2013_2025_bruta.parquet
```

### 3. Inspecionar os Dados Gerados

Para verificar a estrutura e o conteúdo da base Parquet:

```powershell
python inspecionar_parquet.py
```

---

## 📊 Estrutura do Processamento

O fluxo atual do projeto pode ser representado da seguinte forma:

```text
Dados originais
      │
      ▼
┌──────────────────────┐
│ Ingestão das planilhas│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Reconstrução temporal│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Padronização das     │
│ variáveis            │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Regularização em     │
│ intervalos de 10 min │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Base Parquet bruta   │
│ 2013–2025            │
└──────────────────────┘
```

---

## 🔬 Próximas Etapas

As próximas etapas do projeto incluem:

* Controle de qualidade dos dados meteorológicos;
* Identificação e tratamento de valores discrepantes;
* Avaliação de falhas e períodos sem observações;
* Investigação de alterações instrumentais e de sítio;
* Homogeneização das séries temporais;
* Análise estatística e climatológica;
* Investigação de tendências e extremos meteorológicos.

---

## 🏛️ Instituição

**Centro de Pesquisas Meteorológicas e Climáticas Aplicadas à Agricultura — CEPAGRI**

**Universidade Estadual de Campinas — UNICAMP**

Campinas — São Paulo — Brasil
