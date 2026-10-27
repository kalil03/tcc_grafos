-- códigos de município no padrão IBGE de 7 dígitos

CREATE TABLE IF NOT EXISTS municipios (
    codigo_ibge     INTEGER PRIMARY KEY,
    nome            TEXT NOT NULL,
    uf              CHAR(2) NOT NULL,
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS populacao_municipio (
    codigo_ibge     INTEGER NOT NULL REFERENCES municipios(codigo_ibge),
    ano             SMALLINT NOT NULL,
    populacao       INTEGER NOT NULL,
    PRIMARY KEY (codigo_ibge, ano)
);

CREATE TABLE IF NOT EXISTS polos (
    codigo_ibge_municipio INTEGER NOT NULL REFERENCES municipios(codigo_ibge),
    ano_referencia  SMALLINT NOT NULL,
    score           NUMERIC,
    rank            SMALLINT,
    is_grande_polo  BOOLEAN NOT NULL DEFAULT FALSE,
    is_utfpr_cm     BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (codigo_ibge_municipio, ano_referencia)
);

-- camada 1: matriculados via SISU em cursos de TI, município de origem -> campus
CREATE TABLE IF NOT EXISTS grafo_arestas (
    ano                             SMALLINT NOT NULL,
    codigo_ibge_municipio_origem    INTEGER NOT NULL REFERENCES municipios(codigo_ibge),
    codigo_ibge_municipio_destino   INTEGER NOT NULL REFERENCES municipios(codigo_ibge),
    peso_alunos                     INTEGER NOT NULL,
    distancia_km_haversine          DOUBLE PRECISION,
    PRIMARY KEY (ano, codigo_ibge_municipio_origem, codigo_ibge_municipio_destino)
);

CREATE INDEX IF NOT EXISTS idx_grafo_destino ON grafo_arestas(codigo_ibge_municipio_destino);

CREATE TABLE IF NOT EXISTS raio_atuacao (
    codigo_ibge_municipio_destino   INTEGER NOT NULL REFERENCES municipios(codigo_ibge),
    ano                             SMALLINT NOT NULL,
    alunos                          INTEGER NOT NULL,
    raio_medio_km                   DOUBLE PRECISION,
    raio_mediano_km                 DOUBLE PRECISION,
    PRIMARY KEY (codigo_ibge_municipio_destino, ano)
);

-- camada 2: formandos de TI (Censo), mercado de TI (CAGED) e população, por ano
CREATE TABLE IF NOT EXISTS mercado_ti_anual (
    codigo_ibge                 INTEGER NOT NULL REFERENCES municipios(codigo_ibge),
    ano                         SMALLINT NOT NULL,
    populacao                   INTEGER,
    concluintes_total           INTEGER,
    concluintes_presencial      INTEGER,
    admissoes                   INTEGER NOT NULL,
    desligamentos               INTEGER NOT NULL,
    saldo                       INTEGER NOT NULL,
    salario_nominal             NUMERIC(12, 2),
    salario_real                NUMERIC(12, 2),
    concl_presencial_por_100k   DOUBLE PRECISION,
    saldo_ti_por_100k           DOUBLE PRECISION,
    vagas_por_formando          DOUBLE PRECISION,
    PRIMARY KEY (codigo_ibge, ano)
);

-- marcadores das linhas verticais do dashboard
CREATE TABLE IF NOT EXISTS eventos_exogenos (
    ano          SMALLINT PRIMARY KEY,
    nome         TEXT NOT NULL,
    descricao    TEXT
);

INSERT INTO eventos_exogenos (ano, nome, descricao) VALUES
    (2014, 'Adoção do SISU pela UTFPR', 'reflexo nos concluintes a partir de 2017/2018'),
    (2020, 'Pandemia de COVID-19', 'possível salto no raio de captação'),
    (2022, 'Popularização da IA Generativa (ChatGPT)', 'possível mudança no perfil de ingressantes')
ON CONFLICT (ano) DO NOTHING;
