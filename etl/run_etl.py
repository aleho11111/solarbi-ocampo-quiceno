"""
Punto de entrada unico del ETL de SolarBI.
Uso:  python etl/run_etl.py

Pasos:
  1. Bronze: lee data/bronze/telemetria.csv (nunca se modifica).
  2. Silver: aplica reglas de calidad y guarda data/silver/lectura_5min.csv.
  3. Gold:   carga silver.lectura_5min y dwh.fact_energia_dia en PostgreSQL.

La carga es idempotente: se usa UPSERT (INSERT ... ON CONFLICT DO UPDATE)
con la clave primaria de cada tabla, asi que correrlo varias veces no duplica filas.
"""
import json
import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

RAIZ = Path(__file__).resolve().parent.parent
BRONZE = RAIZ / "data" / "bronze" / "telemetria.csv"
SILVER = RAIZ / "data" / "silver" / "lectura_5min.csv"
REPORTE = RAIZ / "data" / "silver" / "reporte_calidad.json"
SQL_ESQUEMA = RAIZ / "sql" / "01_esquema.sql"

INTERVALOS_POR_DIA = 288  # 24 h * 12 lecturas por hora (cada 5 min)
POTENCIA_NOMINAL_KW = 5.0  # inversor de 5 kWp

# Rangos fisicos validos
P_MIN, P_MAX = 0.0, POTENCIA_NOMINAL_KW * 1.1   # kW (hasta 10 % sobre la nominal)
IRR_MIN, IRR_MAX = 0.0, 1400.0                  # W/m2
T_MIN, T_MAX = -10.0, 100.0                     # grados C


# ---------------------------------------------------------------- Silver ----
def limpiar(bronze: pd.DataFrame):
    """Aplica las reglas de calidad y devuelve (filas_validas, reporte)."""
    reporte = {"filas_leidas": int(len(bronze))}
    df = bronze.copy()

    # Regla 1: duplicados (misma fila repetida)
    dup = df.duplicated(keep="first")
    reporte["rechazadas_duplicados"] = int(dup.sum())
    df = df[~dup]

    # Regla 2: datos faltantes en las variables principales
    faltantes = df[["p_ac_kw", "irradiancia_wm2"]].isna().any(axis=1)
    reporte["rechazadas_faltantes"] = int(faltantes.sum())
    df = df[~faltantes]

    # Regla 3: rango fisico valido
    en_rango = (
        df["p_ac_kw"].between(P_MIN, P_MAX)
        & df["irradiancia_wm2"].between(IRR_MIN, IRR_MAX)
        & df["temp_modulo_c"].between(T_MIN, T_MAX)
    )
    reporte["rechazadas_rango_fisico"] = int((~en_rango).sum())
    df = df[en_rango]

    reporte["filas_validas"] = int(len(df))
    reporte["pct_datos_validos"] = round(100 * len(df) / len(bronze), 2)
    return df.reset_index(drop=True), reporte


def resumen_diario(silver: pd.DataFrame) -> pd.DataFrame:
    """Energia diaria (kWh) y % de datos validos por dia y dispositivo."""
    s = silver.copy()
    s["fecha_key"] = s["ts"].dt.date
    s["energia_intervalo_kwh"] = s["p_ac_kw"] * 5 / 60  # potencia * 5/60 de hora
    g = s.groupby(["fecha_key", "dispositivo_id"]).agg(
        energia_kwh=("energia_intervalo_kwh", "sum"),
        lecturas_validas=("ts", "count"),
    ).reset_index()
    g["pct_datos_validos"] = 100 * g["lecturas_validas"] / INTERVALOS_POR_DIA
    g = g.rename(columns={"dispositivo_id": "dispositivo_key"})
    g["energia_kwh"] = g["energia_kwh"].round(3)
    g["pct_datos_validos"] = g["pct_datos_validos"].round(2)
    return g[["fecha_key", "dispositivo_key", "energia_kwh", "pct_datos_validos"]]


# ------------------------------------------------------------------ Gold ----
def conectar():
    load_dotenv(RAIZ / ".env")
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "solarbi"),
        user=os.getenv("PGUSER", "solarbi"),
        password=os.getenv("PGPASSWORD", ""),
    )


def cargar(silver: pd.DataFrame, diario: pd.DataFrame):
    with conectar() as conn, conn.cursor() as cur:
        cur.execute(SQL_ESQUEMA.read_text(encoding="utf-8"))

        filas = [
            (r.ts.to_pydatetime(), int(r.dispositivo_id), float(r.p_ac_kw),
             float(r.irradiancia_wm2), float(r.temp_modulo_c))
            for r in silver.itertuples(index=False)
        ]
        execute_values(cur, """
            INSERT INTO silver.lectura_5min
                (ts, dispositivo_id, p_ac_kw, irradiancia_wm2, temp_modulo_c)
            VALUES %s
            ON CONFLICT (ts, dispositivo_id) DO UPDATE SET
                p_ac_kw = EXCLUDED.p_ac_kw,
                irradiancia_wm2 = EXCLUDED.irradiancia_wm2,
                temp_modulo_c = EXCLUDED.temp_modulo_c
        """, filas)

        filas_d = [
            (r.fecha_key, int(r.dispositivo_key), float(r.energia_kwh),
             float(r.pct_datos_validos))
            for r in diario.itertuples(index=False)
        ]
        execute_values(cur, """
            INSERT INTO dwh.fact_energia_dia
                (fecha_key, dispositivo_key, energia_kwh, pct_datos_validos)
            VALUES %s
            ON CONFLICT (fecha_key, dispositivo_key) DO UPDATE SET
                energia_kwh = EXCLUDED.energia_kwh,
                pct_datos_validos = EXCLUDED.pct_datos_validos
        """, filas_d)

        cur.execute("SELECT COUNT(*) FROM silver.lectura_5min")
        n_silver = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM dwh.fact_energia_dia")
        n_gold = cur.fetchone()[0]
    return n_silver, n_gold


# ------------------------------------------------------------------ main ----
def main():
    bronze = pd.read_csv(BRONZE, parse_dates=["ts"])
    silver, rep = limpiar(bronze)

    SILVER.parent.mkdir(parents=True, exist_ok=True)
    silver.to_csv(SILVER, index=False)
    REPORTE.write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")

    print("== Reporte de calidad (Silver) ==")
    print(f"Filas leidas:               {rep['filas_leidas']}")
    print(f"Rechazadas por duplicados:  {rep['rechazadas_duplicados']}")
    print(f"Rechazadas por faltantes:   {rep['rechazadas_faltantes']}")
    print(f"Rechazadas por rango fisico:{rep['rechazadas_rango_fisico']}")
    print(f"Filas validas:              {rep['filas_validas']}")
    print(f"% de datos validos:         {rep['pct_datos_validos']} %")

    diario = resumen_diario(silver)
    n_silver, n_gold = cargar(silver, diario)

    print("== Carga en PostgreSQL (Gold) ==")
    print(f"silver.lectura_5min     -> {n_silver} filas")
    print(f"dwh.fact_energia_dia    -> {n_gold} filas")
    print(diario.to_string(index=False))


if __name__ == "__main__":
    main()
