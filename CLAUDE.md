# Contexto do projeto

TCC do Kalil (UTFPR Campo Mourão), orientador: prof. André.
"Raio de Atuação e Impacto Socioeconômico da UTFPR-CM frente aos Polos de TI do
Paraná: uma Análise em Teoria dos Grafos".

- **TCC1 (até nov/2026):** pipeline de dados, grafos e carga no PostgreSQL, com a
  metodologia escrita.
- **TCC2 (1º sem/2027):** dashboard Streamlit e deploy em nuvem gratuita.
- Proposta original em `docs/proposta-tcc.pdf` (QP1-QP3, H1-H6).

## Metodologia (decidida com o André em out/2026)

O INEP deixou de publicar o microdado de aluno do Censo da Educação Superior (LGPD,
desde 2022, e reescreveu os anos antigos). Não existe mais origem do aluno no dado
aberto. O SEDAP (acesso a dado protegido) foi descartado: a UTFPR não tem núcleo e o
processo arrisca o prazo. Tudo é feito com dados abertos, em duas camadas:

1. **Raio e capilaridade (QP1, QP2, H1, H5):** SISU. Aresta = município de
   residência do matriculado -> município do campus, em cursos de TI. Compara a
   UTFPR-CM com as instituições públicas dos polos que aderiram ao SISU.
2. **Mercado, densidade e absorção (QP3, H2, H3, H4, H6):** concluintes de TI por
   município (Censo, agregado) + CAGED deflacionado pelo IPCA + população do IBGE.

Histórico completo da validação em `docs/validacao-bases.md`.

## Onde fica cada coisa

- `src/tcc_grafos/config.py`: constantes do método (códigos IBGE, curso da
  UTFPR-CM, CBO, idade do recém-formado, ano da quebra do CAGED, polos
  provisórios). Mudou filtro, muda aqui.
- `camada_raio.py` (camada 1: raio, triênios, faixas de distância, H5,
  cobertura do SISU), `camada_mercado.py` (camada 2: H2, H3, H4, H6) e
  `camada_polos.py` (escore): rodam com `python -m tcc_grafos.<camada> [--atualizar]`.
- `etl/`: `basedosdados_extract.py` (SISU, CAGED e RAIS no BigQuery),
  `inep_cursos.py` (Censo da Educação Superior pelos microdados do INEP),
  `capes.py` (programas de pós), `ipca.py`, `populacao.py` (SIDRA), `municipios.py`.
- `graph/arestas.py` monta as arestas; `graph/metrics.py` calcula raio,
  distribuição por distância, CAGR, tendência log-linear e influenciadores.
- `db/load.py` carrega no Postgres; schema em `sql/001_schema.sql` e views em
  `sql/002_materialized_views.sql`.
- `polos/scoring.py`: z-scores dos critérios da proposta; `make polos` roda fora
  do `make pipeline` porque precisa da RAIS.
- `figuras.py` (`make figuras`): as 8 figuras da monografia em `docs/figuras/`
  (PDF para o texto, PNG para conferir). Campo Mourão em azul, o resto em cinza;
  cores validadas com a skill de dataviz. Rodar de novo depois do pipeline.
- `dashboard/`: só o esqueleto de navegação do Streamlit (TCC2).

## Armadilhas já resolvidas (não repetir)

- Código IBGE de Campo Mourão é **4104303** (4104808 é Cascavel).
- TI no Censo = **área específica Cine 061** (`CO_CINE_AREA_ESPECIFICA == 61`). O
  rótulo e a área detalhada mudam de versão por ano (a coluna vira
  `CO_CINE_ROTULO2` em alguns anos); filtrar por prefixo do rótulo perdia a 0616
  (Eng. de Computação) e a 0617 (Ciência de Dados).
- SISU × Censo: casar o curso pelo **par (`id_curso`, município do campus)**. O
  SISU tem códigos inválidos que coincidem com cursos de TI de outros municípios
  (Matemática com código 36 = Ciência da Computação em MT); só pelo código, 399
  de 3.774 matrículas de outras áreas entravam como TI. Par inexistente no Censo
  cai no nome (`TERMOS_CURSO_TI_SISU`). Contar `COUNT(DISTINCT inscricao_enem)`.
- O Censo vem dos microdados do INEP (`data/raw/inep/`), não da Base dos Dados:
  o agregado de lá não identifica a IES. Os arquivos de 2024 batem com a Base dos
  Dados; o de IES muda de nome em 2022 (`CADASTRO_IES` -> `ED_SUP_IES`).
- Objeto em Campo Mourão = só o BCC da UTFPR-CM (`CURSOS_UTFPR_CM`, CO_IES 588).
  Nos polos, todas as IES.
- CBO de TI: famílias 2122, 2123, 2124, 3171, 3172.
- `tipo_modalidade_ensino`: 1 = presencial, 2 = EAD. Usar presencial nas razões
  per capita. No microdado do INEP o EAD vem **por polo de apoio** (até ~1.100
  linhas do mesmo curso no ano, uma por município do polo), não na sede; em
  Maringá o EAD de TI passa o presencial.
- Concluintes da UFPR e da UNIOESTE despencam em 2020, 2021 e 2023 (UFPR: 9 em
  2023) e voltam em 2024; o salto do PR em 2024 é recuperação. Somas do período
  não são afetadas.
- SISU na Base dos Dados vai só de **2017 a 2022**. `status_matricula` é o que a
  IES lançou no Sisu Gestão. "Pendente" só aparece entre **não aprovados** (lista
  de espera); a matrícula que falta está entre aprovados sem status. "Efetivada"
  cobre 52-72% dos ingressantes via ENEM do Censo nos campi da UTFPR (58% no BCC).
  A sensibilidade usa todos os aprovados (`status_aprovado`).
- Schema mudou? `CREATE TABLE IF NOT EXISTS` não altera tabela existente: rodar
  `make db-reset` antes da carga.
- Censo 2025 ainda não saiu: ano sem Censo é "sem dado", nunca zero.
- CAGED: tabela antiga até 2019, Novo CAGED (eSocial) a partir de 2020 (quebra
  metodológica, não é efeito da pandemia). Salário médio é o das admissões. Taxas
  de crescimento não atravessam a quebra. O salto de admissões de 2021 é dentro do
  Novo CAGED, então é mercado.
- População: estimativas IBGE (agregado 6579) + Censo 2022 (agregado 4714); 2023 é
  interpolado.
- Metadados da Base dos Dados: `bd.get_tables`/`get_columns` estão quebrados na lib;
  usar o GraphQL em `https://backend.basedosdados.org/api/v1/graphql`.

## Ambiente

- BigQuery pelo **Sandbox, sem faturamento** (o Kalil não quer cartão). Login com
  `gcloud auth application-default login`; ID do projeto em
  `GCP_BILLING_PROJECT_ID` no `.env`.
- `data/` não vai pro git. As consultas ficam em cache em `data/interim/`; o pacote
  com o necessário fica no Google Drive do Kalil (ver README, "Dados em outro
  computador"). Rodar uma camada com `--atualizar` refaz a consulta.
- Postgres via docker na porta 5434. `make db-reset` recria o volume. Sem `.env`,
  o `DATABASE_URL` padrão do `config.py` aponta para a 5432 e não conecta: criar o
  `.env` com `make env`.
- `make pipeline` = camada 1 + camada 2 + escore de polos + carga. `make test` e `make lint` antes
  de commitar.

## Estado atual e pendências

`make pipeline` (raio, mercado, polos, carga) rodando de ponta a ponta com todos
os caches atualizados no BigQuery (29/out/2026). Números, as 9 decisões de método
(todas fechadas; o Kalil decide, não depende do André) e a análise da pandemia em
`docs/resultados-preliminares.md`. Em resumo: H1, H2 (indicador aproximado), H3 e
H4 negativas; H5 confirma frente aos polos; H6 confirma por pouco (1,12 com o BCC,
0,65 com todas as IES de Campo Mourão). O escore com a RAIS confirma o top-5 da
lista `MUNICIPIOS_POLOS_PROVISORIOS` (com e sem o critério da CAPES).

Falta: escrita da monografia e o
dashboard (TCC2). Os números congelam em 13/nov.

Ao fechar uma pendência ou decidir algo, atualizar esta seção e o
`docs/resultados-preliminares.md` no mesmo commit. Referências em `docs/referencias.bib`
(só entram itens com metadados conferidos) e `docs/trabalhos-relacionados.md`.

## Convenções

- Commit: uma linha curta em português, direta, sem cara de IA e sem rodapé de
  coautoria. Commitar e dar push só quando o Kalil pedir.
- Comentários de código só quando necessários, curtos. Nada no código, nos
  comentários ou nos commits pode indicar que foi gerado por IA.
- Não inventar números nem referências: conferir na fonte antes de escrever.
