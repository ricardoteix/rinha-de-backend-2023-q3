--CREATE DATABASE "rinha"
--    WITH
--    OWNER = postgres
--    ENCODING = 'UTF8'
--    CONNECTION LIMIT = -1
--    IS_TEMPLATE = False;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS pessoas (
    id uuid DEFAULT uuid_generate_v4 () PRIMARY KEY, -- maybe use generating in backend simplifies and accelerate things
    nome VARCHAR(100) COLLATE pg_catalog."default" NOT NULL,
    apelido VARCHAR(32) COLLATE pg_catalog."default" NOT NULL,
    nascimento DATE NOT NULL,
    stack TEXT COLLATE pg_catalog."default"
);

ALTER TABLE pessoas ADD CONSTRAINT constraint_apelido UNIQUE (apelido);

TRUNCATE TABLE pessoas;