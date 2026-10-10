-- Ejemplo de UPSERT (lo mismo que hace run_etl.py desde Python)
INSERT INTO dwh.fact_energia_dia (fecha_key, dispositivo_key, energia_kwh, pct_datos_validos)
VALUES ('2026-10-05', 1, 25.0, 95.0)
ON CONFLICT (fecha_key, dispositivo_key)
DO UPDATE SET energia_kwh = EXCLUDED.energia_kwh,
              pct_datos_validos = EXCLUDED.pct_datos_validos;
