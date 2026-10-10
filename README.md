# SolarBI Pascual · Consulta Power BI y Grafana

> *One governed dataset, two views: Grafana for real-time operations and Power BI for business decisions.*

## Datos del trabajo

| Campo | Contenido |
|---|---|
| Integrante 1 | NOMBRE COMPLETO 1 |
| Integrante 2 | NOMBRE COMPLETO 2 |
| Curso y grupo | Inteligencia de Negocios · Grupo 50 |
| Semestre | 2026-II |
| Docente | Ramiro Grisales Montoya |
| Institución | Institución Universitaria Pascual Bravo |

## Descripción

Trabajo de consulta del proyecto SolarBI Pascual. Se construye un flujo pequeño pero completo con datos simulados de un inversor de 5 kWp:

1. **Bronze**: datos crudos de telemetría (cada 5 min, 3 días) con anomalías inyectadas.
2. **Silver**: limpieza con 3 reglas de calidad (duplicados, faltantes y rango físico).
3. **Gold**: carga en PostgreSQL (`silver.lectura_5min` y `dwh.fact_energia_dia`) con carga idempotente (UPSERT).
4. **Visualización**: el mismo dato en Power BI (medidas DAX) y en Grafana (series de tiempo).

El análisis y las respuestas de la consulta están en `docs/` (PDF de entrega).

## Estructura del repositorio

```
solarbi-apellido1-apellido2/
├── README.md
├── .gitignore
├── .env.example      (plantilla de variables; el .env real NO se sube)
├── requirements.txt
├── docs/             PDF de la consulta y nota de cron
├── data/             bronze/ (crudo) y silver/ (limpio)
├── etl/              simulador.py, run_etl.py
├── sql/              tablas, UPSERT y consultas de Grafana
├── powerbi/          archivo .pbix o proyecto .pbip + medidas DAX
└── grafana/          dashboard.json exportado
```

## Cómo reproducir la práctica

**Requisitos:** Python 3.10+, PostgreSQL 14+, Power BI Desktop (Windows) y Grafana OSS.

1. Clonar el repositorio e instalar dependencias:
   ```bash
   git clone https://github.com/USUARIO/solarbi-apellido1-apellido2.git
   cd solarbi-apellido1-apellido2
   pip install -r requirements.txt
   ```
2. Crear la base de datos en PostgreSQL (una sola vez):
   ```sql
   CREATE USER solarbi WITH PASSWORD 'tu_clave';
   CREATE DATABASE solarbi OWNER solarbi;
   ```
3. Copiar `.env.example` a `.env` y poner los datos de conexión (el `.env` está en `.gitignore`).
4. Generar los datos crudos (Bronze):
   ```bash
   python etl/simulador.py
   ```
5. Ejecutar el ETL completo con un único comando (se puede correr varias veces, no duplica datos):
   ```bash
   python etl/run_etl.py
   ```
6. **Power BI:** abrir el archivo de la carpeta `powerbi/`, conectar a PostgreSQL (`localhost`, base `solarbi`) y actualizar. Las medidas están en `powerbi/medidas_dax.md`.
7. **Grafana:** agregar PostgreSQL como data source e importar `grafana/dashboard.json` (Dashboards > New > Import).

## Automatización

Para ejecutar el ETL cada día a medianoche: `0 0 * * * cd /ruta/al/repo && python3 etl/run_etl.py` (ver `docs/cron.md`).

## Quién hizo qué

| Tarea | Responsable |
|---|---|
| Repositorio, README y .gitignore | Integrante 1 |
| Simulador y reglas de calidad (Silver) | Integrante 1 |
| Carga en PostgreSQL y UPSERT (Gold) | Integrante 2 |
| Tablero en Power BI | Integrante 2 |
| Tablero en Grafana | Integrante 1 |
| Parte A (consulta) y PDF | Ambos |

## Seguridad

No se suben contraseñas ni cadenas de conexión. Las credenciales van en variables de entorno (`.env` excluido con `.gitignore`).
