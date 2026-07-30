"""Dashboard Streamlit (TCC2). Por enquanto só o esqueleto de navegação.

Rodar com: streamlit run dashboard/app.py
"""

import streamlit as st

st.set_page_config(
    page_title="UTFPR-CM vs. Polos de TI do Paraná",
    layout="wide",
)

st.title("Raio de Atuação e Impacto Socioeconômico da UTFPR-CM")
st.caption("Uma análise em Teoria dos Grafos frente aos polos de TI do Paraná (2015-2025).")

st.info("Dashboard em construção (TCC2). Depende da pipeline de ETL (TCC1) rodando.")

st.markdown(
    """
    ### Perguntas que este dashboard responde
    - **QP1**: Raio médio de atuação da UTFPR-CM vs. grandes polos.
    - **QP2**: Municípios "influenciadores" na exportação de estudantes de TI.
    - **QP3**: Mercado de trabalho formal de TI (saldo de vagas e salário real).

    Ver `dashboard/pages/` para as páginas de cada questão de pesquisa.
    """
)
