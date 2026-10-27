-- QP2: alunos enviados (out-degree) e recebidos (in-degree) por município, no período
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_influenciadores AS
SELECT
    m.codigo_ibge,
    m.nome,
    m.uf,
    COALESCE(s.alunos, 0) AS alunos_enviados,
    COALESCE(e.alunos, 0) AS alunos_recebidos
FROM municipios m
LEFT JOIN (
    SELECT codigo_ibge_municipio_origem AS codigo_ibge, SUM(peso_alunos) AS alunos
    FROM grafo_arestas GROUP BY 1
) s USING (codigo_ibge)
LEFT JOIN (
    SELECT codigo_ibge_municipio_destino AS codigo_ibge, SUM(peso_alunos) AS alunos
    FROM grafo_arestas GROUP BY 1
) e USING (codigo_ibge)
WHERE s.alunos IS NOT NULL OR e.alunos IS NOT NULL;

-- H2/H3/H4/H6 no período; vagas_por_formando só com anos que têm formandos e CAGED
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_resumo_mercado AS
SELECT
    codigo_ibge,
    SUM(saldo) AS saldo,
    AVG(salario_real) AS salario_real_medio,
    AVG(concl_presencial_por_100k) AS concl_presencial_por_100k,
    SUM(concluintes_presencial) AS concluintes_presencial,
    SUM(saldo) FILTER (WHERE concluintes_presencial IS NOT NULL)::DOUBLE PRECISION
        / NULLIF(SUM(concluintes_presencial), 0) AS vagas_por_formando
FROM mercado_ti_anual
GROUP BY codigo_ibge;
