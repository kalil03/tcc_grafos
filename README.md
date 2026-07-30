# Raio de Atuação e Impacto Socioeconômico da UTFPR-CM frente aos Polos de TI do Paraná

TCC: uma análise em Teoria dos Grafos comparando a UTFPR Campus Campo Mourão
(curso de CSTI, concluintes desde 2015) aos grandes polos formadores de TI do
estado do Paraná, usando microdados públicos do INEP e do CAGED.

## Cronograma

- **TCC1 (até nov/2026):** pipeline de ETL, definição dos polos, modelagem em
  grafos, carga no PostgreSQL. Este repositório, por enquanto, é o TCC1.
- **TCC2 (1º sem/2027):** dashboard Streamlit sobre os dados já tratados, com
  deploy em nuvem gratuita.

## Estrutura do repositório

```
config/                  Parâmetros de configuração adicionais (se necessário)
data/
  raw/                   Microdados brutos baixados (não versionado)
  interim/               Dados intermediários limpos (parquet, não versionado)
  processed/             Dados finais prontos para carga (não versionado)
sql/
  001_schema.sql          Schema das tabelas (municípios, concluintes, empregos, grafo...)
  002_materialized_views.sql  Views materializadas que o dashboard vai consultar
src/tcc_grafos/
  config.py               Parâmetros centrais (recorte de ano/UF/domínio)
  etl/                     Download e limpeza dos microdados INEP/CAGED + IPCA
  graph/                   Construção do grafo e métricas (Haversine, centralidade, CAGR)
  polos/                   Critério multifatorial de classificação dos "grandes polos"
  db/                      Conexão e carga no PostgreSQL
dashboard/                 App Streamlit (esqueleto; conteúdo real no TCC2)
notebooks/                 Exploração ad-hoc
tests/                     Testes das funções matemáticas puras
```

## Configuração do ambiente

Pré-requisitos: Python 3.10+, Docker (para o PostgreSQL local).

```bash
make venv                  # cria o ambiente virtual
source .venv/bin/activate  # ativa (precisa ser no seu shell)
make install               # instala as dependências
make env                   # cria o .env a partir do exemplo (ajuste a senha se quiser)
make db-up                 # sobe o PostgreSQL; o schema em sql/ roda no primeiro start
make test                  # roda os testes
```

Outros alvos úteis (`make <alvo>`):

| Alvo        | O que faz                                      |
|-------------|------------------------------------------------|
| `dashboard` | sobe o dashboard Streamlit                     |
| `db-down`   | derruba o banco                                |
| `db-logs`   | acompanha os logs do banco                     |
| `psql`      | abre um psql no banco                          |
| `pgadmin`   | sobe o pgAdmin em http://localhost:5050        |
| `lint`      | roda o ruff                                    |

## Definição de "Polo" (resumo)

Os vértices do grafo são **municípios**, não instituições isoladas. Nos
municípios classificados como "grandes polos" (top-5 por um escore que soma
concluintes, nº de IES de TI, estoque de empregos CAGED e presença de
pós-graduação CAPES; ver `src/tcc_grafos/polos/scoring.py`), agregam-se
**todas** as IES de TI da cidade. Campo Mourão é tratado à parte: o vértice
representa exclusivamente a UTFPR-CM, nunca agregado com outras IES locais.
Isso é proposital; a justificativa completa está na seção 4 do projeto de pesquisa.

## Status

Repositório recém-criado: estrutura, schema e esqueleto do pipeline prontos.
Os scripts de download (`src/tcc_grafos/etl/download_inep.py` e
`download_caged.py`) têm URLs marcadas com `TODO`, a preencher assim que os
links das bases forem recebidos do orientador.
