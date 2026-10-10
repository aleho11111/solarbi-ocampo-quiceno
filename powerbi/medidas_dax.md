# Medidas DAX (Power BI)

Tablas usadas: `dwh.fact_energia_dia` (energia_kwh, pct_datos_validos, fecha_key) y el parametro `Tarifa_COP_kWh`.

Capacidad instalada: 5 kWp (parametro `Capacidad_kWp`).

```dax
Energia kWh =
SUM ( fact_energia_dia[energia_kwh] )

Yield kWh/kWp =
DIVIDE ( [Energia kWh], [Capacidad kWp] )

Ahorro COP =
[Energia kWh] * [Tarifa COP kWh Valor]

Pct Datos Validos =
AVERAGE ( fact_energia_dia[pct_datos_validos] ) / 100
```

Parametros (Inicio > Transformar datos > Administrar parametros, o "Nuevo parametro" de what-if):

```dax
Capacidad kWp = 5
Tarifa COP kWh Valor = 900   -- reemplazar por la tarifa real de su operador (citar la fuente)
```
