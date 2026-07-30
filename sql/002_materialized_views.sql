-- views materializadas para o dashboard consultar direto
-- placeholder: escrever de verdade depois que concluintes_ti/empregos_ti/grafo_arestas
-- estiverem povoadas

-- planejadas: mv_raio_atuacao_anual (QP1), mv_influenciadores (QP2),
-- mv_mercado_ti_real (QP3), mv_retencao_regional (H2), mv_impacto_per_capita (H4),
-- mv_eficiencia_absorcao (H6)

-- exemplo:
-- CREATE MATERIALIZED VIEW IF NOT EXISTS mv_raio_atuacao_anual AS
-- SELECT ano, codigo_ibge_municipio_destino AS municipio_polo,
--        AVG(distancia_km_haversine) AS raio_medio_km,
--        SUM(peso_alunos) AS total_alunos
-- FROM grafo_arestas
-- GROUP BY ano, codigo_ibge_municipio_destino;
