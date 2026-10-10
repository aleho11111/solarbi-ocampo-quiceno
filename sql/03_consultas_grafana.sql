-- Panel 1: irradiancia y potencia cada 5 minutos (serie de tiempo)
SELECT ts AS "time", irradiancia_wm2 AS "Irradiancia (W/m2)", p_ac_kw * 1000 AS "Potencia AC (W)"
FROM silver.lectura_5min
WHERE $__timeFilter(ts) AND dispositivo_id = ${dispositivo}
ORDER BY ts;

-- Panel 2: porcentaje de datos validos (stat/gauge)
SELECT AVG(pct_datos_validos) AS "% datos validos"
FROM dwh.fact_energia_dia
WHERE dispositivo_key = ${dispositivo};

-- Variable de dashboard "dispositivo"
SELECT DISTINCT dispositivo_id FROM silver.lectura_5min ORDER BY 1;
