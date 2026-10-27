# Resultados preliminares

Saída do pipeline (`make pipeline`) em out/2026, com dados abertos. Os números são
preliminares: servem para orientar as decisões de método abaixo, não para a
monografia ainda.

## Camada 1: raio de atuação (SISU, matriculados em TI, 2017-2022)

**UTFPR-CM entre os campi da UTFPR com 100 ou mais matriculados em TI:**

| Campus | Matriculados | Raio médio (km) | Raio mediano (km) |
|---|---:|---:|---:|
| Santa Helena | 155 | 704 | 715 |
| **Campo Mourão** | **240** | **386** | **321** |
| Medianeira | 217 | 564 | 302 |
| Apucarana | 218 | 398 | 279 |
| Cornélio Procópio | 771 | 321 | 161 |
| Ponta Grossa | 453 | 331 | 140 |
| Pato Branco | 406 | 383 | 51 |
| Dois Vizinhos | 262 | 382 | 47 |
| Toledo | 426 | 328 | 38 |
| Curitiba | 635 | 236 | 8 |
| Guarapuava | 176 | 93 | 0 |

- Campo Mourão tem o **2º maior raio mediano** entre os campi da UTFPR e o maior
  entre os grandes polos (Curitiba, Londrina, Maringá, Cascavel, Ponta Grossa).
  Os campi do interior tendem a atrair de mais longe que o da capital, com
  exceção de Guarapuava.
- A atração é **bimodal**: 41,7% dos matriculados vêm de até 100 km, mas **50,8%
  vêm de fora do Paraná**. A média em km esconde isso; vale mostrar a distribuição.
- **H1 (raio crescendo) não aparece nos dados:** o raio mediano anual de Campo
  Mourão cai de 321 km (2018) para 77 km (2022), com mais alunos locais em 2022.
  As amostras anuais são pequenas (3 a 84 matriculados), então é tendência a
  confirmar, não conclusão.
- **QP2:** São Paulo é o 2º maior "exportador" de alunos para os cursos de TI do
  Paraná via SISU (1.179 matriculados, contra 2.806 do próprio Paraná).

## Camada 2: mercado, densidade e absorção (2015-2025)

Salário real a preços de 2025. Concluintes = todas as IES do município, só cursos
presenciais (o EAD infla Maringá por causa da Unicesumar).

| Município | Saldo de vagas TI | Salário real médio | Formandos TI pres./100 mil hab. | Vagas por formando |
|---|---:|---:|---:|---:|
| Curitiba | 5.030 | 5.797 | 38,0 | 0,66 |
| **Campo Mourão** | **204** | **4.262** | **21,3** | **0,65** |
| Maringá | 1.992 | 3.710 | 32,8 | 1,35 |
| Londrina | 2.330 | 3.393 | 21,5 | 1,99 |
| Ponta Grossa | 509 | 3.217 | 19,0 | 0,70 |
| Cascavel | 536 | 3.022 | 23,0 | 0,58 |

- **H3 (salário):** Campo Mourão tem o 2º maior salário real de TI, atrás só de
  Curitiba. Mas o salário real de 2025 é parecido com o de 2015: o ganho nominal
  recente foi corroído pela inflação.
- **H4 (per capita) não se confirma:** Campo Mourão fica no meio do grupo, abaixo
  de Curitiba, Maringá e Cascavel.
- **H6 (mais de uma vaga por formando) não se confirma:** 0,65 em Campo Mourão;
  só Londrina e Maringá passam de 1.

## Decisões de método pendentes

1. **Curso-objeto:** no SISU, o curso de TI da UTFPR-CM aparece como "Ciência da
   Computação", não CSTI. O Censo tem "Sistemas para Internet" (Cine 0615S03).
   Qual é o objeto, ou os dois?
2. **Métrica do raio:** a média ponderada é puxada por poucos alunos distantes.
   Proposta: usar a mediana como principal e reportar a média e a distribuição.
3. **Matrícula no SISU:** só "Efetivada" conta como matrícula, mas parte das
   matrículas fica como "Pendente" no dado. O ranking entre campi é mais confiável
   que o valor absoluto em km.
4. **Hipóteses que não se confirmaram (H1, H4, H6):** reportar como resultado
   negativo ou reformular (ex.: H4 comparando só instituições públicas)?
5. **Grandes polos:** a lista do config é provisória. Falta rodar o escore
   (`polos/scoring.py`), que depende de dado da CAPES ainda não integrado.
6. **H2 (retenção) e H5 (democratização)** ainda não têm cálculo no pipeline. H5
   precisa saber se o município de origem tem curso público de TI (dá para tirar
   do Censo, pela categoria administrativa).
7. **Quebra do CAGED em 2019/2020** (CAGED antigo × Novo CAGED): comparar os dois
   lados com cautela.
