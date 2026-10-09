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

CREATE TABLE IF NOT EXISTS ies (
    codigo_ies      INTEGER PRIMARY KEY,
    nome            TEXT NOT NULL,
    codigo_ibge_municipio INTEGER NOT NULL REFERENCES municipios(codigo_ibge),
    categoria_administrativa TEXT
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

CREATE TABLE IF NOT EXISTS concluintes_ti (
    id                          BIGSERIAL PRIMARY KEY,
    ano_censo                   SMALLINT NOT NULL,
    codigo_ibge_municipio_nascimento INTEGER REFERENCES municipios(codigo_ibge),
    codigo_ibge_municipio_curso INTEGER NOT NULL REFERENCES municipios(codigo_ibge),
    codigo_ies                  INTEGER REFERENCES ies(codigo_ies),
    codigo_curso_cine           TEXT,
    quantidade                  INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_concluintes_ano ON concluintes_ti(ano_censo);
CREATE INDEX IF NOT EXISTS idx_concluintes_origem ON concluintes_ti(codigo_ibge_municipio_nascimento);
CREATE INDEX IF NOT EXISTS idx_concluintes_destino ON concluintes_ti(codigo_ibge_municipio_curso);

CREATE TABLE IF NOT EXISTS empregos_ti (
    id                      BIGSERIAL PRIMARY KEY,
    competencia             DATE NOT NULL,
    codigo_ibge_municipio   INTEGER NOT NULL REFERENCES municipios(codigo_ibge),
    cbo                     TEXT NOT NULL,
    admissoes               INTEGER NOT NULL DEFAULT 0,
    desligamentos           INTEGER NOT NULL DEFAULT 0,
    saldo                   INTEGER NOT NULL DEFAULT 0,
    salario_medio_nominal   NUMERIC(12, 2),
    salario_medio_real      NUMERIC(12, 2)
);

CREATE INDEX IF NOT EXISTS idx_empregos_competencia ON empregos_ti(competencia);
CREATE INDEX IF NOT EXISTS idx_empregos_municipio ON empregos_ti(codigo_ibge_municipio);

CREATE TABLE IF NOT EXISTS ipca_mensal (
    competencia         DATE PRIMARY KEY,
    numero_indice        NUMERIC(14, 6) NOT NULL,
    variacao_mensal_pct  NUMERIC(8, 4)
);

-- grafo direcionado e ponderado município-a-município (origem -> destino)
CREATE TABLE IF NOT EXISTS grafo_arestas (
    id                              BIGSERIAL PRIMARY KEY,
    ano                             SMALLINT NOT NULL,
    codigo_ibge_municipio_origem    INTEGER NOT NULL REFERENCES municipios(codigo_ibge),
    codigo_ibge_municipio_destino   INTEGER NOT NULL REFERENCES municipios(codigo_ibge),
    peso_alunos                     INTEGER NOT NULL,
    distancia_km_haversine          DOUBLE PRECISION,
    UNIQUE (ano, codigo_ibge_municipio_origem, codigo_ibge_municipio_destino)
);

CREATE INDEX IF NOT EXISTS idx_grafo_ano ON grafo_arestas(ano);

-- marcadores das linhas verticais do dashboard
CREATE TABLE IF NOT EXISTS eventos_exogenos (
    id           SERIAL PRIMARY KEY,
    nome         TEXT NOT NULL,
    ano          SMALLINT NOT NULL,
    descricao    TEXT
);

INSERT INTO eventos_exogenos (nome, ano, descricao) VALUES
    ('Adoção do SISU pela UTFPR', 2014, 'reflexo nos concluintes a partir de 2017/2018'),
    ('Pandemia de COVID-19', 2020, 'possível salto no raio de captação'),
    ('Popularização da IA Generativa (ChatGPT)', 2022, 'possível mudança no perfil de ingressantes')
ON CONFLICT DO NOTHING;
