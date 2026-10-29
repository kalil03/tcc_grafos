# Resultados preliminares

Saída do pipeline (`make pipeline`) em 29/out/2026, com os caches do SISU, do
CAGED e da RAIS atualizados no BigQuery. Os números ainda são preliminares:
congelam em 13/nov.

**Objeto:** no vértice de Campo Mourão entra só o BCC da UTFPR-CM (curso 1164656
no Censo, CO_IES 588). Nos polos, todas as IES de TI do município, como na
proposta.

**Definição de TI** (a mesma nas duas camadas): área específica Cine 061 nos
microdados do INEP.

- No Censo, o filtro antigo por prefixo do rótulo (0611-0615, 0619) perdia a 0616
  (Engenharia de Computação, Internet das Coisas) e a 0617 (Ciência de Dados). Em
  Ponta Grossa, isso dava 61 concluintes em 2015, contra 91 de fato.
- No SISU, o curso é recortado pelo par (código INEP do curso, município do
  campus). O código sozinho não serve: o SISU tem códigos inválidos que coincidem
  com cursos de TI de outros municípios (Matemática com o código de uma Ciência da
  Computação de MT, por exemplo), o que punha 399 de 3.774 matrículas de outras
  áreas na conta. Quando o par não existe no Censo, vale o nome do curso; é o caso
  do BCC de Campo Mourão em 2018, registrado com o código 1486.
- No SISU, cada aluno é contado uma vez (inscrições distintas), porque o mesmo
  candidato pode aparecer em mais de uma chamada.

## Camada 1: raio de atuação (SISU, matriculados em TI, 2017-2022)

**Raio por IES/campus, com 40 ou mais matriculados** (ponderado pelos alunos; IC
de 95% da mediana por bootstrap, 2.000 reamostras de alunos):

| IES (campus) | Matriculados | Raio médio (km) | Raio mediano (km) | IC 95% da mediana |
|---|---:|---:|---:|---:|
| UTFPR (Santa Helena) | 155 | 704 | 715 | 573-774 |
| **UTFPR (Campo Mourão)** | **239** | **388** | **321** | **148-409** |
| UTFPR (Medianeira) | 217 | 564 | 302 | 94-607 |
| UNESPAR (Apucarana) | 52 | 324 | 204 | 50-290 |
| UEL (Londrina) | 48 | 185 | 160 | 43-267 |
| UTFPR (Ponta Grossa) | 452 | 331 | 140 | 98-222 |
| UTFPR (Cornélio Procópio) | 523 | 321 | 134 | 109-172 |
| UENP (Bandeirantes) | 56 | 162 | 93 | 46-125 |
| UNICENTRO (Guarapuava) | 72 | 269 | 76 | 0-221 |
| UTFPR (Dois Vizinhos) | 259 | 386 | 47 | 38-96 |
| UTFPR (Pato Branco) | 223 | 178 | 24 | 0-42 |
| UTFPR (Toledo) | 223 | 211 | 18 | 0-37 |
| UFPR (Curitiba) | 160 | 267 | 8 | 0-15 |
| UTFPR (Curitiba) | 380 | 168 | 0 | 0-12 |
| UNIOESTE (Cascavel) | 81 | 208 | 0 | 0-38 |
| UNIOESTE (Foz do Iguaçu) | 77 | 348 | 0 | 0-0 |
| UTFPR (Guarapuava) | 173 | 95 | 0 | 0-0 |

**Distribuição por distância, UTFPR-CM × IES públicas dos polos:**

| IES (município) | Alunos | Até 100 km | Acima de 300 km | De fora do PR |
|---|---:|---:|---:|---:|
| **UTFPR (Campo Mourão)** | **239** | **41,4%** | **51,9%** | **51,0%** |
| UTFPR (Ponta Grossa) | 452 | 45,8% | 39,2% | 48,0% |
| UTFPR (Curitiba) | 380 | 71,8% | 22,6% | 25,5% |
| UFPR (Curitiba) | 160 | 65,0% | 25,6% | 30,6% |
| UNIOESTE (Cascavel) | 81 | 72,8% | 22,2% | 16,0% |
| UEL (Londrina) | 48 | 43,8% | 27,1% | 50,0% |
| UEM (Maringá) | 11 | 81,8% | 18,2% | 9,1% |

- **QP1:** Campo Mourão tem o 2º maior raio mediano entre os campi da UTFPR e o
  maior entre os polos. O IC (148-409 km) se sobrepõe ao da UTFPR de Ponta Grossa
  (98-222) e ao da UEL (43-267), então contra esses dois a diferença não é
  conclusiva; contra Curitiba, Cascavel e Maringá, é. A atração é bimodal: 41,4% vêm de até 100 km e 51,9% de mais de 300 km. Por isso
  a métrica principal é a **mediana**, e a distribuição acompanha.
- **Sensibilidade com todos os aprovados** (selecionados pelo SISU, matriculados
  ou não): Campo Mourão 369 km (IC 350-409, 1.316 aprovados), contra Ponta Grossa
  76 km, Londrina 20 km, Cascavel 20 km, Curitiba 8 km (UTFPR e UFPR) e Maringá
  0 km. A conclusão de QP1 se mantém.
- UEL e UEM quase não usam o SISU em TI (48 e 11 matriculados em seis anos), então
  Londrina e Maringá ficam mal representados na camada 1. É uma limitação.

### QP2: municípios influenciadores

O grafo tem 3.453 matriculados de 2017-2022: 2.142 do Paraná e 1.311 de fora. O
estado de São Paulo é o 2º maior exportador (796), muito à frente de Minas Gerais
(84) e Santa Catarina (80).

Principais origens (out-degree ponderado restrito às arestas que chegam a cada
destino):

| UTFPR-CM | Alunos | Parcela | Grandes polos | Alunos | Parcela |
|---|---:|---:|---|---:|---:|
| Campo Mourão | 42 | 17,6% | Curitiba | 304 | 26,9% |
| Maringá | 11 | 4,6% | Ponta Grossa | 125 | 11,0% |
| São Paulo (capital) | 9 | 3,8% | Cascavel | 46 | 4,1% |
| Peabiru | 8 | 3,3% | São Paulo (capital) | 29 | 2,6% |
| Goioerê | 7 | 2,9% | São José dos Pinhais | 23 | 2,0% |
| Curitiba | 5 | 2,1% | Castro | 18 | 1,6% |
| Brasília | 5 | 2,1% | Londrina | 17 | 1,5% |

A UTFPR-CM tem a base de origem mais pulverizada: a própria cidade dá 17,6% dos
alunos, e o resto vem de muitos municípios pequenos. Nos polos, a própria cidade
pesa mais (Curitiba, 26,9%).

### H1 (raio crescendo mais rápido que nos polos): não se confirma

Raio mediano por triênio (as amostras anuais são pequenas demais para um CAGR
entre o primeiro e o último ano):

| Município | 2017-2019 | 2020-2022 |
|---|---:|---:|
| **Campo Mourão** | **418 km, IC 321-506 (83 alunos)** | **148 km, IC 83-350 (156)** |
| Ponta Grossa | 138 km, IC 98-223 (176) | 157 km, IC 99-243 (276) |
| Curitiba | 0 km, IC 0-12 (235) | 0 km, IC 0-14 (305) |
| Londrina | 50 km, IC 0-267 (14) | 174 km, IC 51-283 (34) |
| Cascavel | 0 km, IC 0-84 (33) | 0 km, IC 0-38 (48) |

O raio de Campo Mourão caiu enquanto o número de alunos quase dobrou: entraram
mais alunos da região a partir de 2020. Os intervalos quase não se sobrepõem
(321-506 contra 83-350), então a queda é provável, não ruído. A H1 é reportada
como resultado negativo. O nível do raio, que é alto, responde a QP1, e a queda
coincide com a pandemia (ver abaixo).

### H5 (democratização do acesso): confirma frente aos polos

Parcela dos matriculados vindos de municípios **sem curso de TI público e
presencial com vagas no ano de ingresso** (cadastro de cursos do INEP, Brasil
inteiro, porque metade dos alunos vem de fora do PR):

| IES (município) | Alunos | Sem oferta pública na origem |
|---|---:|---:|
| **UTFPR (Campo Mourão)** | **239** | **43,9%** |
| UTFPR (Ponta Grossa) | 452 | 38,1% |
| UTFPR (Curitiba) | 380 | 26,6% |
| UNIOESTE (Cascavel) | 81 | 24,7% |
| UFPR (Curitiba) | 160 | 23,1% |
| UEL (Londrina) | 48 | 50,0% |
| UEM (Maringá) | 11 | 18,2% |

Campo Mourão fica acima de todos os polos com amostra razoável. A UEL passa, mas
com 48 alunos em seis anos. Entre os campi da UTFPR, Campo Mourão fica no meio
(Cornélio Procópio 46,1%, Dois Vizinhos 45,2%, Toledo 23,3%). Por triênio, Campo
Mourão sobe de 41,0% para 45,5%.

### Cobertura do SISU e o que é "Pendente"

A Base dos Dados descreve `status_matricula` como "a situação de matrícula
registrada pela IES no sistema Sisu Gestão". No BCC de Campo Mourão:

- **"Pendente" só aparece entre candidatos não aprovados** (`status_aprovado`
  falso): é a lista de espera sem desfecho registrado, não matrícula perdida.
- **A matrícula que falta está entre os aprovados sem status nenhum** (257
  registros em 2017, 141 em 2019).
- Desde 2021 há "Efetivada" também na lista de espera (14 em 2021, 50 em 2022).

Comparando com os ingressantes via ENEM que a própria UTFPR declarou ao Censo:

| Ano | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 |
|---|---:|---:|---:|---:|---:|---:|
| SISU "Efetivada" | 3 | 51 | 29 | 31 | 41 | 84 |
| Censo, ingresso ENEM | 65 | 59 | 69 | 65 | 71 | 86 |
| Cobertura | 5% | 86% | 42% | 48% | 58% | 98% |

O SISU registra como "Efetivada" 58% da entrada (239 de 415). Nos campi da
UTFPR a cobertura fica entre 52% e 72% (`data/processed/cobertura_sisu.csv`).
Consequências:

- os totais do SISU são uma **amostra** da entrada, não a entrada toda;
- 2017 quase não tem registro em Campo Mourão (3 de 65), o que pesa no triênio
  2017-2019;
- a comparação de raio supõe que quem teve a matrícula registrada não vem de
  lugares diferentes de quem não teve; a sensibilidade com todos os aprovados
  (acima) dá a mesma conclusão;
- o Censo registra ingresso por vestibular no BCC a partir de 2023 (23
  ingressantes em 2023 e 57 em 2024, contra 10 via ENEM em 2024), então depois
  de 2022 o SISU deixaria de cobrir a maior parte da entrada.

## Camada 2: mercado, densidade e absorção (2015-2025)

Salário real a preços de 2025 (salário médio das admissões). Concluintes:
presenciais, 2015-2024; em Campo Mourão, só o BCC da UTFPR-CM.

| Município | Saldo de vagas TI | Salário real médio | Formandos/100 mil hab. | Formandos | Vagas por formando | Jovens graduados admitidos por formando |
|---|---:|---:|---:|---:|---:|---:|
| Curitiba | 5.030 | 5.797 | 38,3 | 7.216 | 0,66 | 2,11 |
| **Campo Mourão** | **204** | **4.262** | **12,2** | **119** | **1,12** | **1,39** |
| Maringá | 1.992 | 3.710 | 33,3 | 1.387 | 1,32 | 2,51 |
| Londrina | 2.330 | 3.393 | 25,9 | 1.463 | 1,65 | 2,31 |
| Ponta Grossa | 509 | 3.217 | 25,4 | 898 | 0,52 | 0,69 |
| Cascavel | 536 | 3.022 | 23,0 | 770 | 0,58 | 1,48 |

- **H3 (salário real crescendo mais que nos polos): não se confirma.** Campo
  Mourão tem o 2º maior salário real, mas a série oscila muito porque são de 50 a
  150 admissões por ano. Crescimento anual do salário real, separado pela quebra
  do CAGED (CAGR entre as pontas / tendência log-linear com todos os anos):

  | Município | 2015-2019 (CAGED antigo) | 2020-2025 (Novo CAGED) |
  |---|---:|---:|
  | **Campo Mourão** | **-12,5% / -12,4%** | **-0,5% / -0,4%** |
  | Curitiba | +3,1% / +2,9% | -0,8% / -1,2% |
  | Londrina | +1,5% / +1,8% | +0,5% / +0,3% |
  | Maringá | +2,5% / +2,7% | +0,6% / -1,6% |
  | Ponta Grossa | +1,3% / -0,4% | +2,8% / +3,0% |
  | Cascavel | +0,7% / +1,0% | 0,0% / -0,2% |

- **H4 (mais formandos por habitante): não se confirma.** Só com o BCC, Campo
  Mourão tem 12,2 formandos por 100 mil habitantes, o menor do grupo.
- **H6 (mais de uma vaga por formando): confirma por pouco.** Com o BCC isolado,
  são 1,12 vaga de TI por formando (saldo de 133 em 2015-2024 para 119
  formandos). Somando todas as IES de Campo Mourão, cai para 0,65. As vagas do
  CAGED também absorvem formandos das outras IES da cidade, então os dois números
  vão para o texto, com o 1,12 como resultado principal (decisões 1 e 5). Londrina
  (1,65) e Maringá (1,32) ficam acima. O saldo de 2025 (71) fica de fora porque
  ainda não há Censo de 2025.
- **H2 (retenção), pelo indicador aproximado: não se confirma.** A retenção
  individual não é mensurável com dado aberto. O indicador é o número de admissões
  em TI de pessoas com superior completo e até 29 anos, por formando presencial
  do município (CAGED: `grau_instrucao` 9, 10, 11 ou 80). Em Campo Mourão são 165
  admissões para 119 formandos (1,39), abaixo de Curitiba, Londrina, Maringá e
  Cascavel; só Ponta Grossa fica abaixo (0,69). Com todas as IES de Campo Mourão
  no denominador, cai para 0,80. O indicador não prova que são as mesmas pessoas
  nem diz a área do diploma.

## Pandemia e quebra do CAGED

Em 2020 acontecem três coisas ao mesmo tempo, e o texto precisa separá-las:

1. **Mudança de sistema do CAGED.** A partir da competência de janeiro de 2020, as
   empresas passaram a declarar admissões e desligamentos pelo eSocial (Portaria
   SEPRT nº 1.127/2019), e a série virou o Novo CAGED. Não é efeito da pandemia; a
   comparação 2019 × 2020 é que fica comprometida. Por isso as taxas de salário
   são calculadas separadamente antes e depois.
2. **O boom de contratações em TI.** As admissões de TI no Paraná ficam estáveis
   de 2019 para 2020 (11.025 → 10.768) e saltam 58% em 2021 (17.030), caindo
   depois (12.741 em 2023). Como 2020 e 2021 já são os dois do Novo CAGED, **esse
   salto é do mercado, não da mudança de sistema**. A parcela de jovens graduados
   entre os admitidos cai de 31% (2019) para 23% (2021): o boom contratou
   proporcionalmente menos recém-formados. Em Campo Mourão as admissões dobram (60
   em 2020, 106 em 2021) e, ao contrário de Curitiba, não voltam a cair: 110 em
   2024 e 146 em 2025. A Brasscom também registra a aceleração de 2021, mas os
   números variam entre os relatórios e precisam ser conferidos no original antes
   de citar.
3. **O ensino remoto.** A Portaria MEC nº 343/2020 autorizou substituir aulas
   presenciais por meios digitais. No Censo, esses cursos continuam
   **presenciais**, então o filtro presencial não muda por causa do ensino remoto
   emergencial. O BCC continuou formando gente (17 em 2019, 10 em 2020, 10 em 2021,
   23 em 2024), e as matrículas cresceram de 258 (2019) para 404 (2024).

Outros efeitos que entram como contexto ou limitação:

- **EAD.** Os concluintes de TI em EAD no Paraná passam de 808 (2019) para 4.042
  (2024), e os ingressantes de 5.350 para 23.508; os municípios com polo de EAD de
  TI vão de 149 para 245. O microdado registra o EAD por polo de apoio (uma linha
  por município do polo, com os concluintes dali). Fica fora das razões por
  habitante porque o polo não é uma IES do município e misturaria modalidades: em
  Maringá, o EAD de TI (2.142 concluintes em 2015-2024) passa o presencial (1.387).
- **Trabalho remoto.** O CAGED registra o emprego no município do estabelecimento.
  Um egresso que mora em Campo Mourão e trabalha remoto para uma empresa de outra
  cidade não aparece em Campo Mourão. Isso subestima a absorção local (H2 e H6)
  justamente a partir de 2020.
- **Raio na pandemia.** A queda do raio de Campo Mourão em 2020-2022 (H1) é
  compatível com alunos preferindo estudar perto de casa na pandemia, mas os
  dados não permitem afirmar a causa.
- **Concluintes presenciais em 2020, 2021 e 2023.** O salto do Paraná em 2024
  (1.667 em 2023, 2.427 em 2024) é recuperação, não mudança de formato: o número
  de cursos presenciais é estável (154 a 169 por ano), e as quedas se concentram
  em universidades públicas. A UFPR tem 133 concluintes em 2022, 9 em 2023 e 121
  em 2024 (e 39 e 37 em 2020 e 2021, contra 107 em 2019); a UNIOESTE tem zero em
  2020 e 2021. As matrículas seguem estáveis nesses anos, o que é compatível com
  atraso de calendário acadêmico (formatura registrada no ano seguinte); a causa
  não foi conferida. As razões do período (somas de 2015-2024) não são afetadas;
  as séries anuais de concluintes, sim.

## Grandes polos (escore da proposta)

Critérios (a) concluintes presenciais de TI 2015-2024, (b) média anual de IES com
curso presencial de TI, (c) estoque de empregos de TI (média dos vínculos ativos
em 31/12 na RAIS) e (d) programa de pós em Computação (CAPES, área de avaliação
Computação, programas em funcionamento em 2024). Campo Mourão fica fora do
ranking. Escore = soma dos z-scores entre os 47 municípios com curso presencial
de TI.

| Posição | Município | Concluintes | IES/ano | Vínculos TI | Pós CAPES | Escore | Escore sem (d) |
|---:|---|---:|---:|---:|:-:|---:|---:|
| 1 | Curitiba | 7.216 | 21,5 | 17.844 | sim | 21,30 | 18,91 |
| 2 | Londrina | 1.463 | 8,1 | 3.123 | sim | 6,11 | 3,72 |
| 3 | Maringá | 1.387 | 6,2 | 3.025 | sim | 5,42 | 3,03 |
| 4 | Cascavel | 770 | 6,1 | 1.302 | sim | 4,14 | 1,75 |
| 5 | Ponta Grossa | 898 | 3,5 | 752 | sim | 3,26 | 0,87 |
| 6 | Cornélio Procópio | 441 | 1,0 | 102 | sim | 1,82 | - |
| 7 | Foz do Iguaçu | 505 | 4,6 | 508 | não | 0,32 | 0,74 |
| (ref.) | Campo Mourão | 205 | 2,0 | 322 | sim | 1,98 | - |

O top-5 é o mesmo da lista provisória, com e sem o critério da CAPES. Sem a CAPES,
Foz do Iguaçu fica perto de Ponta Grossa (0,74 contra 0,87). Programas de
Computação no PR em 2024: UFPR e PUCPR (Informática) e UTFPR (Computação Aplicada)
em Curitiba, UEL em Londrina, UEM em Maringá, UNIOESTE em Cascavel, UTFPR em Ponta
Grossa, em Cornélio Procópio e em Campo Mourão (mestrado desde 2021).

## Decisões de método

Decididas (out/2026):

1. **Curso-objeto: só o BCC da UTFPR-CM.** O CSTI (109550) não tem ingressante
   desde 2015 e formou os últimos em 2017 (9, 2 e 2 concluintes em 2015-2017). Os
   primeiros formandos do BCC no Censo são de 2015 (2 concluintes), que é o
   início do recorte. **A introdução da proposta precisa ser corrigida:** ela diz
   que o impacto se mede a partir da primeira turma do CSTI, em 2015; os dados
   mostram que 2015 é a primeira turma do BCC. Se o CSTI entrasse, seriam 132
   formandos e a H6 cairia para 1,01.
2. **Métrica do raio:** mediana ponderada como principal, com IC de 95% por
   bootstrap; a média e a distribuição por faixa de distância como apoio.
3. **Matrícula no SISU:** "Efetivada" como base, com a cobertura (SISU × Censo)
   reportada e uma análise de sensibilidade com todos os aprovados.
4. **Hipóteses negativas:** H1, H2 (indicador aproximado), H3 e H4 são
   reportadas como negativas, sem reformular. O nível do raio entra como resposta
   a QP1, não como hipótese nova.
5. **Grandes polos:** escore da proposta, top-5, com Campo Mourão fora do ranking.
   Nos polos entram todas as IES; no vértice de Campo Mourão, só a UTFPR-CM.
6. **H2:** indicador aproximado pelo CAGED (admissões de jovens com superior
   completo por formando), declarado como tal. **H5:** origem sem curso de TI
   público e presencial com vagas no ano de ingresso.
7. **Quebra do CAGED:** taxas separadas para 2015-2019 e 2020-2025, com 2020
   marcado nos gráficos. O boom de 2021 é tratado como efeito de mercado (mesma
   metodologia de 2020 e 2021).
8. **Recorte da camada 1:** 2017-2022 (o que o SISU cobre na Base dos Dados). A
   camada 2 continua em 2015-2025.
9. **Evolução do raio:** triênios 2017-2019 × 2020-2022.

## Fontes

Com entrada em `referencias.bib`:

- Quebra do CAGED: `seprt2019portaria1127` (Portaria SEPRT 1.127/2019) e
  `mte2021notatecnica` (nota técnica do Novo CAGED, dez/2021).
- Ensino remoto: `mec2020portaria343` (Portaria MEC 343/2020).
- Escore de polos, critério (d): `capes_programas2024`.
- Significado do `status_matricula`: `basedosdados_sisu`.
- Histórico do câmpus: `utfpr2012campocm17anos`.
- Dados: `inep_censo_microdados`, `mec_sisu_dados`, `me_caged_novocaged`,
  `basedosdados`.

`[validar]`, sem entrada no .bib (conferir no original antes de citar número):

- Brasscom, demanda de talentos em TIC (contratações de 2020 e 2021):
  https://brasscom.org.br/wp-content/uploads/2025/12/BRI2-2021-007-01-Demanda-de-Talentos-em-TIC-e-Sigma-TCEM-v112.pdf
- Canaltech, "Tecnologia gerou 122 mil vagas de emprego em 2021" (levantamento do
  Observatório Acate com dados do CAGED):
  https://canaltech.com.br/empreendedorismo/tecnologia-gerou-122-mil-vagas-de-emprego-em-2021-no-brasil-211003/
- Convergência Digital, TICs criaram 76 mil empregos no primeiro semestre:
  https://convergenciadigital.com.br/carreira/tics-criaram-76-mil-empregos-no-primeiro-semestre
- INEP, Notas Estatísticas do Censo da Educação Superior 2021 (procurar dados de
  concluintes e EAD na pandemia):
  https://download.inep.gov.br/publicacoes/institucionais/estatisticas_e_indicadores/notas_estatisticas_censo_da_educacao_superior_2021.pdf
- UTFPR, convocados do SISU em Campo Mourão (listas por chamada, para conferir
  matrícula): https://antigo.utfpr.edu.br/cursos/estudenautfpr/sisu/convocados/campo-mourao/convoca_3a_sisu_CM.pdf

## Figuras

`make figuras` gera em `docs/figuras/`: `mapa_origens_cm`, `raio_mediano_por_ies`,
`distribuicao_distancia`, `raio_por_trienio`, `democratizacao_por_ies`,
`admissoes_ti`, `salario_real` e `escore_polos` (PDF e PNG).

## Pendências

1. Levar para o banco as saídas que ainda são só CSV (triênio, H5, distribuição,
   cobertura, principais origens), quando o dashboard precisar (TCC2).
