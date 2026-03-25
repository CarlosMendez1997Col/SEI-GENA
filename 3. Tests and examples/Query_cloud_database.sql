-- Database
CREATE DATABASE "GENA_database"
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Spanish_Spain.1252'
    LC_CTYPE = 'Spanish_Spain.1252'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

-- SEI-GENA Schema
CREATE SCHEMA IF NOT EXISTS "GENA_Schema";
CREATE TABLE IF NOT EXISTS "GENA_Schema".licitaciones (institucion TEXT, titulo TEXT, url TEXT, informacion TEXT);

SELECT * FROM "GENA_Schema".licitaciones

SELECT institucion, COUNT(*) as total_convocatorias FROM "GENA_Schema".licitaciones GROUP BY institucion ORDER BY total_convocatorias DESC;

SELECT institucion, titulo, url FROM "GENA_Schema".licitaciones WHERE informacion ILIKE '%cambio climático%' OR informacion ILIKE '%resiliencia%' OR informacion ILIKE '%adaptación%';

SELECT institucion, COUNT(*) as registros_sin_texto FROM "GENA_Schema".licitaciones WHERE informacion IS NULL OR length(informacion) < 100 GROUP BY institucion;

SELECT titulo, institucion, url FROM "GENA_Schema".licitaciones WHERE informacion ILIKE '%Colombia%' OR titulo ILIKE '%Colombia%';

CREATE OR REPLACE VIEW "GENA_Schema".vista_oportunidades_verdes AS SELECT institucion, titulo, url, substring(informacion from 1 for 300) || '...' as resumen_previo
FROM "GENA_Schema".licitaciones WHERE informacion ILIKE '%cambio climático%' OR informacion ILIKE '%sostenibilidad%' OR informacion ILIKE '%biodiversidad%' OR informacion ILIKE '%renovable%' OR titulo ILIKE '%clima%';
SELECT * FROM "GENA_Schema".vista_oportunidades_verdes

CREATE OR REPLACE VIEW "GENA_Schema".auditoria_calidad_datos AS SELECT institucion, COUNT(*) AS total_registros, SUM(CASE WHEN length(informacion) < 100 OR informacion IS NULL THEN 1 ELSE 0 END) AS registros_vacios_o_cortos,
ROUND(AVG(length(informacion)), 0) AS promedio_caracteres_por_texto FROM "GENA_Schema".licitaciones GROUP BY institucion ORDER BY registros_vacios_o_cortos DESC;
SELECT * FROM "GENA_Schema".auditoria_calidad_datos

CREATE OR REPLACE VIEW "GENA_Schema".foco_colombia AS SELECT institucion, titulo, url FROM "GENA_Schema".licitaciones WHERE  titulo ILIKE '%Colombia%' OR informacion ILIKE '%Colombia%';
SELECT * FROM "GENA_Schema".foco_colombia

ALTER TABLE "GENA_Schema".licitaciones ADD COLUMN search_vector tsvector;

UPDATE "GENA_Schema".licitaciones SET search_vector = to_tsvector('spanish', titulo || ' ' || informacion);

SELECT titulo, institucion, ts_rank(search_vector, query) as relevancia
FROM "GENA_Schema".licitaciones, to_tsquery('spanish', 'clima & colombia') query
WHERE search_vector @@ query
ORDER BY relevancia DESC;

SELECT a.titulo, a.institucion as inst_1, b.institucion as inst_2
FROM "GENA_Schema".licitaciones a
JOIN "GENA_Schema".licitaciones b ON a.titulo = b.titulo
WHERE a.url <> b.url;
