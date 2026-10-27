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

## Armadilhas já resolvidas (não repetir)

- Código IBGE de Campo Mourão é **4104303** (4104808 é Cascavel).
- Cine de TI: filtrar por **prefixo** (`PREFIXOS_CINE_TI`, área 061). O
  `id_curso_cine` muda de versão por ano (ex. `"0613S01"` e `0615S02`).
- CBO de TI: famílias 2122, 2123, 2124, 3171, 3172.
- `tipo_modalidade_ensino`: 1 = presencial, 2 = EAD. Usar presencial nas razões
  per capita: o EAD infla Maringá (Unicesumar).
- SISU na Base dos Dados vai só de **2017 a 2022**. Matrícula confirmada é
  `status_matricula = 'Efetivada'`, que subconta (parte fica `Pendente`). O SISU não
  tem Cine: o curso de TI é achado pelo nome (`TERMOS_CURSO_TI_SISU`).
- No SISU, o curso de TI da UTFPR-CM aparece como "Ciência da Computação", não CSTI.
- Censo 2025 ainda não saiu: ano sem Censo é "sem dado", nunca zero.
- CAGED: tabela antiga até 2019, Novo CAGED a partir de 2020 (quebra
  metodológica). Salário médio é o das admissões.
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
- Postgres via docker na porta 5434. `make db-reset` recria o volume.
- `make pipeline` = camada 1 + camada 2 + carga. `make test` antes de commitar.

## Estado atual e pendências

Pipeline das duas camadas rodando de ponta a ponta. Números e decisões de método
pendentes em `docs/resultados-preliminares.md`. Em resumo: H1, H4 e H6 não se
confirmam com os dados atuais; H3 (salário real) é a mais favorável à UTFPR-CM.

Falta: escore dos grandes polos (`polos/scoring.py`, depende de dado da CAPES), H2
(retenção), H5 (precisa da rede pública/privada dos cursos no Censo), as decisões
de método com o André, e o dashboard (TCC2). Referências em `docs/referencias.bib`
(só entram itens com metadados conferidos) e `docs/trabalhos-relacionados.md`.

## Convenções

- Commit: uma linha curta em português, direta, sem cara de IA e sem rodapé de
  coautoria. Commitar e dar push só quando o Kalil pedir.
- Comentários de código só quando necessários, curtos. Nada no código, nos
  comentários ou nos commits pode indicar que foi gerado por IA.
- Não inventar números nem referências: conferir na fonte antes de escrever.
