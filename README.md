# Raio de Atuação e Impacto Socioeconômico da UTFPR-CM frente aos Polos de TI do Paraná

TCC: uma análise em Teoria dos Grafos comparando a UTFPR Campus Campo Mourão aos
grandes polos formadores de TI do Paraná, só com dados abertos.

## Cronograma

- **TCC1 (até nov/2026):** pipeline de dados, modelagem em grafos e carga no
  PostgreSQL.
- **TCC2 (1º sem/2027):** dashboard Streamlit sobre os dados tratados, com deploy
  em nuvem gratuita.

## Metodologia em duas camadas

O INEP deixou de publicar o microdado de aluno do Censo da Educação Superior (LGPD),
então a origem do estudante não vem mais do Censo. O trabalho usa duas camadas,
detalhadas em [`docs/validacao-bases.md`](docs/validacao-bases.md):

1. **Capilaridade e raio (QP1, QP2, H1, H5):** microdados do SISU. Cada aresta liga
   o município de residência do aluno matriculado ao município do campus, nos
   cursos de TI. Compara a UTFPR-CM com as instituições públicas dos polos que
   aderiram ao SISU.
2. **Mercado, densidade e absorção (QP3, H2, H3, H4, H6):** concluintes de TI por
   município (Censo da Educação Superior, agregado), admissões e salários de TI
   (CAGED, deflacionados pelo IPCA) e população (IBGE).

| Fonte | Onde |
|---|---|
| SISU, CAGED, RAIS | Base dos Dados (BigQuery) |
| Censo da Educação Superior (cadastro de cursos e IES) | microdados do INEP, em `data/raw/inep/` |
| Programas de pós-graduação | dados abertos da CAPES (programas 2024) |
| IPCA | API do Banco Central (série 433) |
| População | API do IBGE (estimativas + Censo 2022) |
| Coordenadas dos municípios | [kelvins/municipios-brasileiros](https://github.com/kelvins/municipios-brasileiros) |

## Configuração do ambiente

Pré-requisitos: Python 3.10+, Docker e uma conta Google.

```bash
make venv                  # cria o ambiente virtual
source .venv/bin/activate  # ativa (precisa ser no seu shell)
make install               # instala as dependências
make env                   # cria o .env a partir do exemplo
make db-up                 # sobe o PostgreSQL
make test                  # roda os testes
```

Acesso ao BigQuery (sem cartão, pelo BigQuery Sandbox):

1. Crie um projeto em [console.cloud.google.com](https://console.cloud.google.com)
   e abra o BigQuery nele; sem faturamento, o projeto entra em modo Sandbox.
2. Instale o [gcloud CLI](https://cloud.google.com/sdk/docs/install) e rode
   `gcloud auth application-default login`.
3. Coloque o ID do projeto em `GCP_BILLING_PROJECT_ID` no `.env`.

## Rodando o pipeline

```bash
make pipeline   # = make raio mercado polos carga
```

| Alvo | O que faz | Saída |
|---|---|---|
| `raio` | camada 1: fluxo SISU, arestas, raio (total, anual, triênio), distribuição por distância, H5 (democratização), cobertura do SISU e influenciadores | `data/processed/arestas_sisu_ti.parquet`, `raio_*.csv`, `distribuicao_distancia_por_ies.csv`, `democratizacao_*.csv`, `cobertura_sisu.csv`, `influenciadores.csv` |
| `mercado` | camada 2: concluintes (INEP), CAGED, IPCA e população | `data/processed/mercado_*.csv` |
| `polos` | escore dos grandes polos (INEP, RAIS, CAPES) | `data/processed/polos.csv` |
| `carga` | aplica `sql/`, recarrega as tabelas e atualiza as views | PostgreSQL |
| `figuras` | figuras da monografia a partir de `data/processed/` (fora do `pipeline`) | `docs/figuras/*.pdf` e `*.png` |

O Censo da Educação Superior vem dos microdados do INEP em `data/raw/inep/<ano>/`
(cadastro de cursos e de IES, 2015-2024), não do BigQuery: o agregado da Base dos
Dados não identifica a IES. O programa de pós da CAPES é baixado sozinho.

As consultas ao BigQuery ficam em cache em `data/interim/`. Para refazê-las, rode a
camada com `--atualizar` (ex.: `python -m tcc_grafos.camada_raio --atualizar`).

### Dados em outro computador

`data/` não vai pro git. Para não precisar refazer as consultas ao BigQuery (nem
configurar o GCP), copie estes arquivos para os mesmos caminhos:

```
data/interim/fluxo_sisu.parquet         cache do SISU
data/interim/cursos_ti_inep.parquet     cursos de TI do INEP (sai de data/raw/inep/)
data/interim/cursos_censo_municipio.parquet  todos os cursos do INEP (curso, município)
data/interim/caged_ti.parquet           cache do CAGED
data/interim/rais_ti.parquet            cache da RAIS (escore de polos)
data/raw/ibge/municipios_coordenadas.csv
data/raw/ibge/populacao_municipios.csv
```

Com eles, `make pipeline` roda sem GCP (o IPCA vem da API do Banco Central, sem
login). Os dois arquivos do IBGE são baixados de novo automaticamente se faltarem.

Outros alvos: `dashboard`, `db-down`, `db-reset` (apaga o volume do banco), `db-logs`,
`psql`, `pgadmin` (http://localhost:5050), `lint`.

## Estrutura

```
data/                      raw, interim e processed (não versionado)
docs/                      validação das bases, trabalhos relacionados, referencias.bib
sql/                       schema e views materializadas
src/tcc_grafos/
  config.py                recorte (anos, UF), códigos Cine e CBO de TI
  camada_raio.py           camada 1
  camada_mercado.py        camada 2
  etl/                     extração (basedosdados), IPCA, população, municípios
  graph/                   arestas e métricas (Haversine, raio, graus, CAGR)
  polos/                   escore dos grandes polos
  db/                      conexão e carga no PostgreSQL
dashboard/                 app Streamlit (esqueleto; conteúdo no TCC2)
tests/
```

## Status

Pipeline das duas camadas rodando de ponta a ponta e carregando no PostgreSQL.
Pendências: atualizar os caches do SISU e do CAGED (`--atualizar`) e rodar o escore
de polos (`make polos`), que dependem do BigQuery. Decisões e resultados em
[`docs/resultados-preliminares.md`](docs/resultados-preliminares.md).
