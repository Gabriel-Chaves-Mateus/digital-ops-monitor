-- 1. DIMENSÃO DE SISTEMAS DE ORIGEM

CREATE TABLE IF NOT EXISTS dim_sistema (
    id_sistema INTEGER PRIMARY KEY,
    nome_sistema TEXT NOT NULL,
    area_responsavel TEXT NOT NULL,
    criticidade_negocio TEXT NOT NULL
);

-- 2. DIMENSÃO DE TIPOS DE ROTINAS / PIPELINES

CREATE TABLE IF NOT EXISTS dim_rotina (
    id_rotina INTEGER PRIMARY KEY,
    nome_rotina TEXT NOT NULL,
    tipo_solucao TEXT NOT NULL, 
    frequencia_esperada TEXT NOT NULL,
    id_sistema INTEGER,
    FOREIGN KEY (id_sistema) REFERENCES dim_sistema(id_sistema)
);

-- 3. TABELA FATO DE EXECUÇÕES (Onde ficam os logs diários)

CREATE TABLE IF NOT EXISTS fato_execucoes (
    id_execucao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_rotina INTEGER NOT NULL,
    data_execucao TEXT NOT NULL,
    status TEXT NOT NULL,
    duracao_segundos INTEGER NOT NULL,
    codigo_erro TEXT,
    mensagem_erro TEXT,
    FOREIGN KEY(id_rotina) REFERENCES dim_rotina(id_rotina)
);

-- 4. VIEW ANALÍTICA (facilita o tabalho do Power BI / Qlik)

CREATE VIEW IF NOT EXISTS vw_monitoramento_sustentacao AS 
SELECT
    f.id_execucao,
    f.data_execucao,
    DATE(f.data_execucao) AS data_dia,
    r.nome_rotina,
    r.tipo_solucao,
    s.nome_sistema,
    s.area_responsavel,
    s.criticidade_negocio,
    f.status,
    f.duracao_segundos,
    COALESCE(f.codigo_erro, 'N/A') AS codigo_erro,
    COALESCE(f.mensagem_erro, 'Execucao normal') AS mensagem_erro
FROM fato_execucoes f
JOIN dim_rotina r ON f.id_rotina = r.id_rotina
JOIN dim_sistema s ON r.id_sistema = s.id_sistema;

