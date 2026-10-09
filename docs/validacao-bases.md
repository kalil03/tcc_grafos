# Validação das bases de dados

Checagem feita em out/2026 contra a API de metadados da Base dos Dados (BigQuery)
e os portais oficiais. Objetivo: confirmar se conseguimos todas as bases, se
precisam de limpeza e como se cruzam.

## ⚠️ Resumo executivo — tem um problema sério no coração do projeto

O dado que sustenta o **raio de atuação** (QP1, QP2, H1, H5) é o **município de
origem do aluno** (`CO_MUNICIPIO_NASCIMENTO`) cruzado com o município do curso.
Esse dado é **microdado em nível de aluno**, e:

1. **A Base dos Dados não tem.** O dataset `br_inep_censo_educacao_superior` só
   expõe **2 tabelas: `curso` e `ies`**, ambas agregadas. A tabela `curso` tem
   `quantidade_concluintes`, `id_municipio` (do curso), `id_curso_cine`,
   `sigla_uf` — mas **nenhum campo de origem/nascimento do aluno**. A query de
   exemplo que veio na proposta (tabela `...aluno`) **não existe** na BD.
2. **O INEP parou de publicar o microdado de aluno — verificado na fonte.**
   Inspecionei o diretório interno dos ZIPs oficiais do INEP (download.inep.gov.br)
   de 2015, 2017, 2018, 2019, 2020, 2021 e 2023: **nenhum** contém o arquivo
   `MICRODADOS_CADASTRO_ALUNOS`; todos têm só `MICRODADOS_CADASTRO_CURSOS` e
   `..._IES`. Os pacotes têm 8–38 MB (se tivessem aluno, teriam GBs). Ou seja, o
   INEP reescreveu retroativamente todos os anos (readequação de 2022, LGPD).
   **Baixar manualmente não resolve** — o dado não está lá, em ano nenhum.
3. **Esse campo existiu** (arquivo `DM_ALUNO`, ~5,4 GB, 2014–2018 tinham
   `CO_MUNICIPIO_NASCIMENTO`), mas as versões atuais no portal estão sem ele. A
   parte da mensagem do orientador que cita "MICRODADOS_CADASTRO_ALUNOS (município
   de origem...)" está desatualizada; `MICRODADOS_CADASTRO_CURSOS` segue válido.

**Consequência:** com dado **aberto**, o grafo município→município só sai pras
federais (SISU). MAS a pesquisa aprofundada achou duas saídas que recuperam a
origem inclusive das privadas/estaduais — **SEDAP/INEP** (microdado identificado,
acesso protegido) e **Censo 2022/IBGE** (público, nível cidade). Ver a seção
"Soluções" abaixo. Decisão de qual via seguir é com o André, mas o projeto
**não está travado**.

### Caminho de resgate: microdados do SISU (validado ✅)

O **SISU está na própria Base dos Dados** (`mec.sisu`, tabela `microdados`, 52
colunas — confirmado via API em out/2026). Resolve o fluxo origem→destino:

- `id_municipio_candidato`, `sigla_uf_candidato` — **origem** (residência do candidato)
- `id_municipio_campus`, `id_ies`, `sigla_ies`, `id_campus` — **destino**
- `id_curso`, `nome_curso` — filtro de TI
- `status_matricula`, `status_aprovado` — contar só quem matriculou de fato
- `modalidade_concorrencia`, `tipo_cota` — subsídio pra H5 (democratização/cotas)

Grafo = `id_municipio_candidato → id_municipio_campus`, ponderado pela contagem.

**Ressalvas importantes (levar ao André):**
1. É "residência" do candidato, não "nascimento"; cobre **ingressantes via SISU**,
   não concluintes. Na prática é um proxy até melhor de "atração", mas muda o texto
   da metodologia.
2. **Cobertura institucional:** o SISU só pega IES que **usam** o SISU — federais
   (UTFPR, UFPR...). **Estaduais (UEM, UEL, UENP) e privadas (PUCPR, Unicesumar)
   não entram.** Isso bate direto no conceito de "polo = todas as IES da cidade":
   para Maringá (UEM + Unicesumar, ambas fora do SISU) o grafo via SISU fica quase
   vazio. Saída provável: comparar UTFPR-CM com **outros polos federais via SISU**,
   ou assumir o recorte "público federal" explicitamente.
3. **Anos:** no portal, ~2017–2022 (confirmar o último ano no BD). O recorte
   2015–2016 fica de fora (o INEP curso agregado ainda cobre esses anos pro lado
   destino).
4. **É ingressante, não "todos os alunos":** o SISU cobre quem *entrou* via SISU
   (federais), não o corpo discente inteiro nem outras formas de ingresso.

### A origem de aluno de IES privada/estadual é irrecuperável publicamente

Portas investigadas e fechadas (out/2026): **INEP aluno** (removido, LGPD);
**PROUNI** (`mec.prouni` na BD — só localização da IES e demografia do bolsista,
`id_municipio`/`sigla_uf`/`nome_municipio_ies` são todos da IES, **sem** município
do beneficiário); **ENEM** (tem cidade do candidato, mas não liga ao local de
matrícula); **vestibular próprio** (UEM, UEL, privadas) — publicam só a *lista de
aprovados* (nome + curso, às vezes estatística agregada de origem, como a UEL
"13.306 de municípios do PR"), **não microdado por candidato com município**;
dados descentralizados por instituição/banca, sem repositório aberto padronizado.
Via teórica: pedido por LAI a cada estadual pode render origem *agregada*
(inviável pra muitos polos, e privadas não se obrigam à LAI). **Linkage por nome
(listas de aprovados × IBGE) não funciona:** a API de nomes do IBGE só dá
frequência agregada do nome por localidade (quantos "João" há em cada município),
não um cadastro nome→cidade; nomes têm homônimos (não identificam); e cruzar
nomes pra inferir atributo pessoal é reidentificação (LGPD) — justamente o que foi
barrado. Onde haveria nome (vestibular) a resolução é impossível; onde há origem
(SISU) o nome é desnecessário. Conclusão: a origem
de quem estuda em PUCPR/Unicesumar/UEM só existe nos sistemas internos delas, que
não publicam. Logo, **no dado aberto**, o grafo de atração é viável apenas para
IES federais (via SISU); o *tamanho* do polo (concluintes por município, todas as
IES) sai do INEP `curso`. Para recuperar a origem das privadas/estaduais, é
preciso sair do dado aberto — ver a seção "Soluções" (SEDAP e Censo 2022).

Outras saídas possíveis: (a) pedir à UTFPR-CM os dados de origem dos próprios
alunos (resolve só o nosso lado, não os polos); (b) arquivos originais pré-2022
de 2014–2019, se acharmos cópia íntegra (reprodutibilidade frágil); (c)
reescopar QP1/QP2 (ver seção final).

## Soluções que recuperam a origem (pesquisa aprofundada, out/2026)

Esgotando o dado **aberto**, a origem só sai do SISU (federais). Mas indo além do
dado aberto, apareceram dois caminhos que recuperam a origem **inclusive de
privadas/estaduais** — e há precedente acadêmico de que é assim que se faz.

### Solução A — SEDAP/INEP (acesso a dado protegido) — padrão-ouro

O INEP tem o **Serviço de Acesso a Dados Protegidos (SEDAP)**, regido pela Portaria
637/2019: pesquisadores acessam o **microdado identificado** (até 20 anos) para
pesquisa científica, em ambiente controlado. Isso inclui o Censo da Educação
Superior em **nível de aluno** — ou seja, devolve `município de nascimento +
município do curso + situação de concluinte`, a coluna exata que o INEP tirou do
dado aberto, e **para TODAS as IES** (públicas e privadas, porque o Censo coleta
de todas). **Resolve o problema por inteiro**, inclusive os polos privados.

- **Processo:** solicitação por e-mail (sedap@inep.gov.br) com projeto de pesquisa,
  currículo Lattes, documento e **carta de vínculo institucional**; análise em
  ~15 dias; acesso por até 90 dias; produto final enviado ao fim.
- **Onde:** sala segura (sede do INEP em Brasília) e salas em Unicamp, Insper,
  UFMG; o INEP anunciou expansão do acesso **a todas as IES federais** (salas/acesso
  remoto). Como a UTFPR é federal, confirmar se temos sala/acesso — isso evitaria
  viagem a Brasília.
- **Saída:** só **resultados agregados** saem da sala (auditados). Como o grafo e
  as métricas já são agregados, dá pra calcular tudo lá dentro e exportar a lista
  de arestas/indicadores. Serve.
- **Ressalvas:** burocracia + prazo; a elegibilidade de um TCC de graduação precisa
  ser confirmada — mas com o André como pesquisador responsável e vínculo UTFPR é
  plausível. É o que a literatura usou (ver Barufi abaixo).
- **Escopo:** SEDAP é **só INEP** (educação: Censo Superior, ENEM, ENADE, Saeb...).
  Resolve a origem do aluno, mas **não** tem CAGED (salários), IBGE (população,
  IPCA) nem CAPES — essas seguem das fontes públicas de sempre. SEDAP cobre a peça
  difícil, não o TCC inteiro.

### Solução B — Censo Demográfico 2022 (IBGE), aberto

Os **microdados da amostra do Censo 2022** (liberados em dez/2025, IBGE FTP) têm
**migração** (município de residência anterior / data-fixa 2017–2022),
**deslocamento para estudo** e **educação/frequenta ensino superior**. Dá pra medir
o fluxo origem→destino de estudantes de ensino superior por **município**, cobrindo
**qualquer instituição** (pública, privada, federal, estadual) — resolve a lacuna
dos polos no nível de cidade, sem burocracia.

- **Limites:** é amostra (~11%) → precisa de pesos e os municípios pequenos ficam
  ruidosos; mede a pessoa, **não a instituição** → não isola UTFPR-CM dentro de
  Campo Mourão (só "Campo Mourão" como cidade). Casa bem com o conceito "polo =
  cidade"; pra isolar a UTFPR-CM, combinar com SISU/SEDAP.
- **Verificar:** semântica exata de "deslocamento para estudo" vs migração nas
  notas metodológicas do IBGE.

### Precedente acadêmico (isto já foi feito)

- **Barufi (2012/2014)** foi pioneira em analisar migração de estudantes
  universitários no Brasil cruzando **microdados identificados** do INEP (ENADE +
  Censo da Educação Superior + ENEM) — exatamente a via SEDAP.
- **Pelegrini, Sá & França (2022)** modelam a mobilidade de universitários no
  Brasil com **modelo gravitacional** (*Higher Education*) — método direto pro
  nosso grafo/raio. Ambos no `referencias.bib`.

### Recomendação de combinação

- **UTFPR-CM isolada (QP1/QP2):** SISU já resolve, público e rápido; SEDAP pra
  versão robusta (nascimento, concluintes, todos os anos).
- **Comparação com polos (inclui privadas/estaduais):** Censo 2022 (cidade) e/ou
  SEDAP (instituição).
- **Não depende de nada disso:** CAGED+IPCA, população, coordenadas.

## Status base por base

| Base | Onde | Status | Observação |
|---|---|---|---|
| INEP Censo Superior — **curso/IES** | BD `br_inep_censo_educacao_superior` | ✅ | Agregados por curso: concluintes/ingressantes por município do curso, cine, UF |
| INEP — **origem do aluno** | — | ❌ | Removido (LGPD). É o gargalo do grafo (ver resumo) |
| **SISU** (origem→destino) | BD `br_mec_sisu.microdados` | ✅ | Tem origem (município do candidato) e destino (campus/IES); só IES que usam SISU (ver ressalvas) |
| **CAGED / Novo CAGED** | BD `br_me_caged` (5 tabelas) | ✅ | Salário, saldo, CBO, município — base do mercado (QP3, H2, H3, H6) |
| **RAIS** | BD `br_me_rais` | ✅ | Para a série pré-Novo CAGED (quebra metodológica a tratar) |
| **IPCA** | BD `br_ibge_ipca` / API BCB (já feito) | ✅ | Deflacionamento já implementado via BCB em `etl/ipca.py` |
| **População municipal** | BD `br_ibge_populacao` | ✅ | Per capita (H4) |
| **Coordenadas dos municípios** | BD `br_bd_diretorios_brasil.municipio` | ✅ | Lat/long pro Haversine; resolve o gargalo de coordenadas |
| **CAPES** (pós stricto sensu) | só achei `br_capes.bolsas` | 🟡 | Não achei tabela de programas/avaliação na BD; pode exigir GeoCapes/Sucupira ou sair do escore |

## Cruzamento dos dados (join keys)

- **Chave geográfica:** todas as bases na BD usam `id_municipio` de **7 dígitos**
  padronizado. Isso **elimina** o problema clássico de o CAGED usar 6 dígitos e o
  INEP 7 — mais um motivo pra usar a BD e não misturar com arquivo bruto.
- **Tempo:** INEP por `ano`; CAGED por competência mensal → agregar pra ano pra
  casar com o INEP; IPCA por mês → serve pra deflacionar antes de agregar.
- **Domínio TI:** INEP por `id_curso_cine` (códigos Cine-Brasil); CAGED por `cbo`
  (famílias de TI). Ambos a validar contra os manuais oficiais.
- **Grafo:** se vier do SISU, a chave é `municipio_residencia_candidato` →
  `municipio_da_IES`. Se viesse do INEP aluno, seria nascimento → curso.

## Limpeza necessária (resumo)

- CAGED: harmonizar **RAIS (antigo) × Novo CAGED** (competências e layout
  diferentes) e converter competência pra data mensal.
- INEP curso: filtrar Cine de TI e UF=PR; os agregados já vêm limpos pela BD.
- SISU: provavelmente o que mais dá trabalho de padronizar (um arquivo por
  edição/ano, nomes de coluna mudando entre anos).
- Deflacionar salários (IPCA) antes de qualquer média.

## Impacto nas perguntas e hipóteses

| Item | Depende de origem do aluno? | Situação |
|---|---|---|
| QP1 / H1 (raio e crescimento) | **Sim** | ❌ com INEP; 🟡 viável via SISU |
| QP2 (influenciadores no grafo) | **Sim** | ❌ com INEP; 🟡 viável via SISU |
| H5 (democratização/origem interior) | **Sim** | ❌ com INEP; 🟡 viável via SISU |
| QP3 / H3 (salário real) | Não | ✅ CAGED + IPCA |
| H4 (per capita) | Não | ✅ INEP curso + população |
| H2 / H6 (retenção/absorção) | Parcial | 🟡 "destino" ✅; "retenção na origem" depende do fluxo |

## Recomendação

1. **Validar o SISU já** (é o que destrava metade das hipóteses). Baixar o
   dicionário e uma edição, confirmar que dá pra montar residência→IES.
2. **Levar o achado ao André antes de codar o grafo** — a proposta assume um dado
   que o INEP não publica mais. Decidir juntos: pivotar pro SISU, mudar o proxy,
   ou reescopar QP1/QP2.
3. **Seguir o que já é verde** em paralelo: CAGED+IPCA (QP3/H3), população (H4) e
   coordenadas — esses não dependem da decisão acima.
