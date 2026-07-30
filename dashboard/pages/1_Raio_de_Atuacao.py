"""QP1: raio médio de atuação da UTFPR-CM vs. grandes polos.

Placeholder: trocar pela leitura de mv_raio_atuacao_anual quando existir.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

st.title("QP1: Raio de Atuação (km)")

exemplo = pd.DataFrame(
    {
        "ano": list(range(2015, 2026)),
        "utfpr_cm": [50, 55, 60, 90, 95, 110, 140, 150, 160, 175, 190],
        "media_grandes_polos": [200, 205, 210, 215, 218, 220, 225, 228, 230, 233, 235],
    }
)

fig = px.line(
    exemplo,
    x="ano",
    y=["utfpr_cm", "media_grandes_polos"],
    labels={"value": "Raio médio (km)", "ano": "Ano", "variable": "Série"},
    title="Evolução do raio médio de atuação (dados de exemplo)",
)

for ano_evento, nome_evento in [(2014, "SISU"), (2020, "COVID-19"), (2022, "IA Generativa")]:
    fig.add_vline(x=ano_evento, line_dash="dash", line_color="red")
    fig.add_annotation(x=ano_evento, y=1.02, yref="paper", text=nome_evento, showarrow=False)

st.plotly_chart(fig, use_container_width=True)
st.caption("dados de exemplo, trocar pela consulta real")
