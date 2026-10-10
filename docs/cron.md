# Automatizacion diaria a medianoche

**Linux / macOS (cron)** - `crontab -e`:

```
0 0 * * * cd /ruta/a/solarbi-apellido1-apellido2 && python3 etl/run_etl.py >> logs/etl.log 2>&1
```

Significado: minuto 0, hora 0, todos los dias del mes, todos los meses, todos los dias de la semana.

**Windows (Programador de tareas)**: Accion = `python.exe`, Argumentos = `etl\run_etl.py`,
Iniciar en = carpeta del repositorio, Desencadenador = Diariamente a las 12:00 a. m.
