-- Esquemas y tablas del proyecto SolarBI (Silver y Gold)
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS dwh;

-- Silver: lecturas limpias cada 5 minutos
CREATE TABLE IF NOT EXISTS silver.lectura_5min (
    ts               TIMESTAMP        NOT NULL,
    dispositivo_id   INTEGER          NOT NULL,
    p_ac_kw          DOUBLE PRECISION NOT NULL,
    irradiancia_wm2  DOUBLE PRECISION NOT NULL,
    temp_modulo_c    DOUBLE PRECISION,
    PRIMARY KEY (ts, dispositivo_id)
);

-- Gold: resumen diario por dispositivo
CREATE TABLE IF NOT EXISTS dwh.fact_energia_dia (
    fecha_key         DATE             NOT NULL,
    dispositivo_key   INTEGER          NOT NULL,
    energia_kwh       DOUBLE PRECISION NOT NULL,
    pct_datos_validos DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (fecha_key, dispositivo_key)
);
