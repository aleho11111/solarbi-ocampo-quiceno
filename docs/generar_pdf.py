# -*- coding: utf-8 -*-
import json, re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Preformatted, KeepTogether)

import os
from pathlib import Path
from reportlab.platypus import Image


INTEGRANTE_1 = "Jaime Alejandro Ocampo"
INTEGRANTE_2 = ""
FECHA = "9 de octubre de 2026"
REPO_URL = "https://github.com/aleho11111/solarbi-ocampo-quiceno"
TARIFA_FUENTE = ""       # ej: "EPM, tarifa, septiembre 2026: 895 COP/kWh (https://www.epm.com.co/clientesyusuarios/energia/tarifas-energia/), consultada el 10/10/2026"
LO_QUE_COSTO = "conectar entre si las aplicaciones"
# Capturas: guardarlas en docs/capturas/ con estos nombres png:
#   paso1, paso2, paso3, paso4, paso5, github_colaboradores, github_commits
ROOT = Path(__file__).resolve().parent.parent
CAPT = ROOT / "docs" / "capturas"
OUT = str(ROOT / "docs" / ("_".join([n.replace(" ", "") for n in (INTEGRANTE_1, INTEGRANTE_2) if n]) + "_Consulta_BI_G50.pdf"))
rep = json.load(open(ROOT / "data" / "silver" / "reporte_calidad.json"))

ss = getSampleStyleSheet()
azul = colors.HexColor("#1F3A5F")
gris = colors.HexColor("#EEF1F5")
naranja = colors.HexColor("#C2410C")

body = ParagraphStyle("body", parent=ss["Normal"], fontName="Helvetica", fontSize=10,
                      leading=13.5, alignment=TA_JUSTIFY, spaceAfter=4)
fuente = ParagraphStyle("fuente", parent=body, fontSize=8.5, textColor=colors.HexColor("#555555"),
                        alignment=0, spaceAfter=8)
h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=16,
                    textColor=azul, spaceBefore=6, spaceAfter=8, keepWithNext=1)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=12,
                    textColor=azul, spaceBefore=10, spaceAfter=4, keepWithNext=1)
h3 = ParagraphStyle("h3", parent=ss["Heading3"], fontName="Helvetica-Bold", fontSize=10.5,
                    textColor=colors.black, spaceBefore=6, spaceAfter=2, keepWithNext=1)
cel = ParagraphStyle("cel", parent=body, fontSize=8.3, leading=10.3, alignment=0, spaceAfter=0)
celb = ParagraphStyle("celb", parent=cel, fontName="Helvetica-Bold", textColor=colors.white)
cen = ParagraphStyle("cen", parent=body, alignment=TA_CENTER)
codigo = ParagraphStyle("codigo", fontName="Courier", fontSize=8, leading=10)
pend = ParagraphStyle("pend", parent=body, fontSize=9, textColor=naranja, alignment=TA_CENTER)

story = []
P = lambda t, s=body: Paragraph(t, s)

def tabla(filas, anchos, cabecera=True):
    data = []
    for i, f in enumerate(filas):
        data.append([Paragraph(str(c), celb if (i == 0 and cabecera) else cel) for c in f])
    t = Table(data, colWidths=anchos, repeatRows=1 if cabecera else 0)
    est = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9AA5B1")),
           ("VALIGN", (0, 0), (-1, -1), "TOP"),
           ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if cabecera:
        est.append(("BACKGROUND", (0, 0), (-1, 0), azul))
        for r in range(1, len(filas)):
            if r % 2 == 0:
                est.append(("BACKGROUND", (0, r), (-1, r), gris))
    t.setStyle(TableStyle(est))
    return t

def caja_captura(texto, alto=4.2, clave=None):
    if clave:
        for ext in ("png", "jpg", "jpeg"):
            f = CAPT / f"{clave}.{ext}"
            if f.exists():
                from reportlab.lib.utils import ImageReader
                iw, ih = ImageReader(str(f)).getSize()
                ancho = 16.5 * cm
                altura = ancho * ih / iw
                if altura > 9 * cm:
                    altura = 9 * cm
                    ancho = altura * iw / ih
                return Image(str(f), width=ancho, height=altura)
    t = Table([[Paragraph("[PEGAR CAPTURA] " + texto, pend)]], colWidths=[16.5 * cm], rowHeights=[alto * cm])
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.8, naranja),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF7ED"))]))
    return t

def pendiente(valor, aviso):
    return valor if valor else f"<font color='#C2410C'>[COMPLETAR: {aviso}]</font>"

conteo = []   # (codigo, palabras)

def resp(codigo_p, titulo, texto, src, extra=None):
    n = len(re.sub(r"<[^>]+>", "", texto).split())
    conteo.append((codigo_p, n))
    story.append(KeepTogether([P(f"<b>{codigo_p}.</b> {titulo}", h3), P(texto), P("Fuente: " + src, fuente)] + (extra or [])))

# ----------------------------------------------------------------- Portada
story += [Spacer(1, 3.5 * cm),
          P("<b>Institución Universitaria Pascual Bravo</b>", cen), Spacer(1, 0.4 * cm),
          P("Inteligencia de Negocios · Grupo 50 · Semestre 2026-II", cen), Spacer(1, 1.5 * cm),
          Paragraph("SolarBI Pascual: Power BI y Grafana, gobernanza de datos, automatización ETL e IoT",
                    ParagraphStyle("t", parent=h1, fontSize=22, leading=27, alignment=TA_CENTER)),
          Spacer(1, 0.6 * cm), P("Trabajo de consulta", cen), Spacer(1, 2 * cm),
          P("<b>Integrantes</b>", cen), P(INTEGRANTE_1, cen), P(INTEGRANTE_2, cen),
          Spacer(1, 1.2 * cm),
          P("<b>Docente:</b> Ramiro Grisales Montoya", cen),
          P("<b>Curso y grupo:</b> Inteligencia de Negocios · Grupo 50", cen),
          P("<b>Fecha:</b> " + FECHA, cen),
          Spacer(1, 1.2 * cm),
          P("Repositorio: " + pendiente(REPO_URL, "enlace del repositorio"), cen),
          PageBreak()]

# ----------------------------------------------------------------- Parte A
story.append(P("Parte A · Consulta", h1))
story.append(P("Bloque 1 · Power BI y Grafana", h2))

resp("D1", "¿Qué es Grafana?",
     "Grafana es una plataforma para visualizar y monitorear datos, sobre todo series de tiempo. Sus componentes son: "
     "<i>data sources</i> (las conexiones a las bases, por ejemplo PostgreSQL), <i>panels</i> (cada gráfico o indicador), "
     "<i>dashboards</i> (el conjunto de paneles), <i>variables</i> (listas que cambian las consultas, como elegir un inversor) "
     "y <i>alerting</i> (reglas que avisan cuando un valor pasa un umbral). Grafana OSS es gratuita, se instala en nuestro "
     "equipo y nosotros la mantenemos. Grafana Cloud es el servicio alojado por Grafana Labs, con plan gratuito y planes de pago, "
     "sin instalar nada. En SolarBI usamos OSS en el computador con PostgreSQL como data source.",
     "Grafana Labs, documentación oficial [1].")

story.append(P("<b>D2.</b> Tabla comparativa Power BI vs. Grafana", h3))
story.append(tabla([
    ["Criterio", "Power BI", "Grafana"],
    ["1. Propósito principal", "Análisis de negocio, informes y cuadros de mando para tomar decisiones.",
     "Monitoreo de sistemas y equipos, sobre todo con series de tiempo."],
    ["2. Usuario típico", "Analista de negocio y directivos.", "Operadores, ingenieros y personal de operación (DevOps/planta)."],
    ["3. Conexión a los datos", "Muchos conectores; modo Import o DirectQuery.", "Data sources (plugins); consulta la base directamente cada vez."],
    ["4. Modelo semántico y lenguaje", "Modelo de datos con relaciones y medidas en DAX.",
     "No tiene modelo propio: se escribe la consulta del origen (SQL en PostgreSQL)."],
    ["5. Actualización y tiempo real", "Actualización programada (Import) o consulta directa; tiempo real limitado.",
     "Auto-refresh cada pocos segundos o minutos; pensado para tiempo casi real."],
    ["6. Alertas", "Alertas de datos en el servicio sobre tarjetas y medidores (más limitadas).",
     "Alerting integrado con reglas, umbrales y notificaciones."],
    ["7. Licenciamiento y costo", "Desktop gratis; para publicar y compartir se necesita licencia (Pro/PPU) o capacidad.",
     "OSS gratis; Cloud con plan gratuito y de pago; Enterprise de pago."],
    ["8. Control de acceso", "Roles del workspace y seguridad a nivel de fila (RLS).",
     "Organizaciones, equipos y roles (Viewer, Editor, Admin); RBAC más fino en Cloud/Enterprise."],
    ["9. Despliegue", "Desktop (Windows) y servicio en la nube de Microsoft.",
     "Se instala en cualquier sistema (Docker, instalador) o se usa en la nube."],
], [3.6 * cm, 6.5 * cm, 6.5 * cm]))
story.append(P("Fuente: Microsoft Learn [2] y Grafana Labs [1].", fuente))

resp("D3", "Tipos de dashboard y KPIs",
     "Un dashboard <b>operativo</b> muestra lo que pasa ahora para actuar rápido (el operador de la planta). Uno <b>analítico</b> "
     "sirve para explorar datos históricos y encontrar causas (el analista). Uno <b>estratégico</b> muestra pocos indicadores "
     "resumidos para decidir (el directivo). En SolarBI, lo que cambia minuto a minuto va a Grafana y lo que se analiza "
     "por día o se convierte en dinero va a Power BI, como muestra la tabla.",
     "Microsoft Learn [2] y Grafana Labs [1].")
story.append(tabla([
    ["KPI", "Tipo de dashboard", "Herramienta", "Por qué"],
    ["Energía (kWh)", "Operativo (hoy) y analítico (histórico)", "Grafana para el día; Power BI para comparar días",
     "La potencia cada 5 min se ve mejor como serie de tiempo."],
    ["Yield y Performance Ratio", "Analítico", "Power BI", "Son medidas calculadas (DAX) que se comparan entre días y plantas."],
    ["Ahorro (COP)", "Estratégico", "Power BI", "Usa una tarifa como parámetro y es lo que le interesa al directivo."],
    ["Disponibilidad y alarmas", "Operativo", "Grafana", "Necesita refresco frecuente y alertas con umbrales."],
    ["% de datos válidos", "Operativo (calidad)", "Grafana", "Un gauge con colores avisa pronto si la calidad baja."],
], [3.2 * cm, 3.9 * cm, 4.0 * cm, 5.5 * cm]))
story.append(Spacer(1, 6))

resp("D4", "Modos de almacenamiento y actualización",
     "En <b>Import</b> Power BI copia los datos a su modelo: es rápido, pero hay que actualizarlo. En <b>DirectQuery</b> no copia nada y "
     "consulta la base cada vez que se usa un visual: los datos están al día, pero es más lento y limita algo de DAX. La "
     "<i>actualización programada</i> (scheduled refresh) recarga el modelo en horas definidas del servicio de Power BI. Para SolarBI usaríamos "
     "<b>Import</b>: <i>fact_energia_dia</i> es pequeña, el ETL corre una vez al día y una actualización diaria después de la medianoche basta. "
     "El auto-refresh de Grafana, en cambio, repite la consulta a la base cada cierto tiempo (por ejemplo cada 5 minutos) sin guardar copia.",
     "Microsoft Learn [2] y Grafana Labs [1].")

resp("D5", "Interactividad: variables vs. segmentadores",
     "Las variables de Grafana (templating) se definen en el dashboard y se escriben dentro de la consulta como <i>${dispositivo}</i>; "
     "al cambiar la lista, Grafana reemplaza el valor y vuelve a ejecutar el SQL. En Power BI, los segmentadores y filtros son controles "
     "visuales que filtran el modelo sin escribir la consulta, a nivel de visual, página o informe. Para SolarBI se crea la variable "
     "<i>dispositivo</i> con una consulta a la tabla de lecturas, y en cada panel el filtro cambia según lo elegido (si el usuario escoge 2, "
     "la condición queda <i>dispositivo_id = 2</i>).",
     "Grafana Labs [1] y Microsoft Learn [2].")
story.append(Preformatted(
    "-- Variable:\nSELECT DISTINCT dispositivo_id FROM silver.lectura_5min ORDER BY 1\n\n"
    "-- Consulta del panel:\nSELECT ts AS \"time\", p_ac_kw FROM silver.lectura_5min\n"
    "WHERE $__timeFilter(ts) AND dispositivo_id = ${dispositivo}  -- con 2 elegido: dispositivo_id = 2",
    codigo))
story.append(Spacer(1, 6))

story.append(P("Bloque 2 · Gobernanza de datos", h2))
resp("G1", "Data governance, data management y data quality",
     "Según DAMA-DMBOK, la gobernanza de datos (<i>data governance</i>) es el conjunto de políticas, roles y decisiones que dicen "
     "quién puede hacer qué con los datos y bajo qué reglas. La gestión de datos (<i>data management</i>) es el trabajo del día a día "
     "para guardar, mover e integrar los datos. La calidad (<i>data quality</i>) es una parte de la gestión: mide si los datos son completos, "
     "válidos y exactos. En SolarBI, la gobernanza define que el mínimo aceptable es 95 % de datos válidos; el ETL es la gestión; "
     "y medir ese porcentaje es la calidad.",
     "DAMA International, DAMA-DMBOK [3].")

resp("G2", "Data owner, data steward y data custodian",
     "El <b>data owner</b> es el dueño del dato en el negocio: decide para qué se usa y quién accede. El <b>data steward</b> cuida "
     "la calidad y las definiciones del día a día. El <b>data custodian</b> se encarga de lo técnico: almacenar, respaldar y proteger. "
     "En el equipo SolarBI: el <i>product owner</i> es el owner; el <i>data modeler</i> y el <i>BI analyst</i> son stewards, porque definen "
     "el esquema y validan que los KPIs signifiquen lo mismo; y el <i>data engineer</i> es el custodian, porque administra PostgreSQL y el ETL.",
     "DAMA International, DAMA-DMBOK [3].")

resp("G3", "El contrato de datos",
     "El <i>data contract</i> es un acuerdo escrito entre quien produce los datos y quien los usa. Debe incluir: el esquema (columnas y tipos), "
     "las unidades (kW, W/m<super>2</super>, °C), la frecuencia (cada 5 minutos), el responsable de la fuente y los niveles de calidad "
     "(por ejemplo 95 % de datos válidos). Si la fuente cambia un campo sin avisar (por ejemplo, pasa la potencia de kW a W o cambia el nombre), "
     "el ETL puede fallar o, peor, cargar valores 1000 veces más grandes sin error, y el cuadro de mando mostraría energía y ahorro equivocados.",
     "DAMA International, DAMA-DMBOK [3].")

resp("G4", "Gobernanza de indicadores",
     "La <i>única fuente de verdad</i> (single source of truth) es un lugar oficial donde se calcula cada dato, para que todos vean la misma cifra. "
     "El <i>catálogo de KPIs</i> es la lista documentada de los indicadores con su definición, fórmula y responsable. Si un KPI se calcula en DAX "
     "en Power BI y en SQL en Grafana, pueden dar números distintos (por ejemplo, si uno incluye datos inválidos y el otro no), y el equipo "
     "pierde la confianza. Por eso en SolarBI el cálculo base se hace una sola vez en la capa Gold y las dos herramientas lo leen.",
     "DAMA International, DAMA-DMBOK [3] y Microsoft Learn [2].")
story.append(tabla([
    ["Campo", "KPI 1", "KPI 2"],
    ["Nombre", "Yield específico", "Porcentaje de datos válidos"],
    ["Fórmula", "Energía diaria (kWh) / capacidad instalada (kWp)", "Lecturas válidas del día / 288 lecturas esperadas x 100"],
    ["Unidad", "kWh/kWp", "%"],
    ["Fuente", "dwh.fact_energia_dia", "silver.lectura_5min (resumido en dwh.fact_energia_dia)"],
    ["Responsable", "BI analyst", "Data engineer"],
    ["Frecuencia", "Diaria", "Diaria"],
], [2.6 * cm, 6.9 * cm, 7.1 * cm]))
story.append(Spacer(1, 6))

resp("G5", "Ley 1581 de 2012",
     "La Ley 1581 de 2012 protege los datos personales, es decir, información de personas naturales identificadas o que se pueden identificar. "
     "Los datos de SolarBI (potencia, irradiancia y temperatura de un inversor) son datos técnicos de un equipo, por eso no son personales. "
     "Esto cambiaría si el tablero muestra qué operador atendió cada alarma, porque ya se relaciona información con una persona y se necesitaría "
     "autorización, una finalidad clara y control de acceso. Nuestra postura: recolectar solo lo necesario, usar códigos o roles en vez de nombres, "
     "restringir quién ve el tablero y nunca subir credenciales o datos personales a GitHub.",
     "Congreso de Colombia, Ley 1581 de 2012 [4].")

story.append(P("Bloque 3 · Automatización de procesos ETL", h2))
resp("E1", "ETL vs. ELT y capas Bronze, Silver y Gold",
     "En <b>ETL</b> los datos se transforman antes de cargarse al destino; en <b>ELT</b> se cargan primero crudos y se transforman dentro del destino. "
     "En SolarBI, <i>Bronze</i> guarda el dato crudo (extraer y cargar), <i>Silver</i> aplica las reglas de calidad (transformar) y <i>Gold</i> deja "
     "el resumen diario listo para los tableros. Power Query sí es una herramienta ETL liviana: extrae de varias fuentes, transforma con pasos "
     "y carga al modelo de Power BI. Pero no sirve para orquestar ni para grandes volúmenes, por eso la limpieza principal la hacemos en Python.",
     "Microsoft Learn [2] y DAMA-DMBOK [3].")

resp("E2", "Carga completa, incremental e idempotencia",
     "La carga completa borra y vuelve a cargar todo: es simple, pero lenta si hay muchos datos. La carga incremental solo procesa lo nuevo o lo "
     "que cambió: es más rápida, pero hay que saber qué cambió. Una carga es <b>idempotente</b> si al ejecutarla varias veces el resultado es el mismo, "
     "sin filas repetidas. En <i>fact_energia_dia</i> se logra con la clave primaria (fecha_key, dispositivo_key) y un UPSERT "
     "(INSERT ... ON CONFLICT DO UPDATE): si el día ya existe se actualiza y si no, se inserta. Así, correr el ETL tres veces dejó siempre 3 filas.",
     "PostgreSQL, documentación de INSERT [12].")

story.append(P("<b>E3.</b> Tres formas de automatizar un flujo", h3))
story.append(tabla([
    ["", "cron / Programador de tareas", "Apache Airflow", "Actualización programada de Power BI"],
    ["Qué es", "Programa del sistema operativo que ejecuta comandos en horarios fijos.",
     "Plataforma para crear, programar y vigilar flujos de trabajo (DAGs).",
     "Función del servicio de Power BI que recarga un modelo en horarios definidos."],
    ["Qué automatiza", "Cualquier script, como python etl/run_etl.py.",
     "Flujos de varios pasos con dependencias, reintentos y registro.",
     "Solo la actualización de los datos del modelo del informe."],
    ["Cuándo conviene", "Un solo script sencillo, como el ETL de SolarBI a la medianoche.",
     "Varios procesos encadenados o equipos grandes que necesitan monitoreo.",
     "Cuando el informe ya está publicado y solo hay que refrescarlo después del ETL."],
], [2.3 * cm, 4.6 * cm, 4.8 * cm, 4.9 * cm]))
story.append(P("Fuente: Apache Airflow [6] y Microsoft Learn [2].", fuente))

resp("E4", "Actualización incremental en Power BI",
     "La actualización incremental hace que Power BI solo recargue los datos recientes en vez de toda la tabla. Se crean dos parámetros de fecha "
     "con los nombres <i>RangeStart</i> y <i>RangeEnd</i>, se filtra la tabla con ellos (fecha mayor o igual a RangeStart y menor que RangeEnd) y se define "
     "una política, por ejemplo guardar 2 años y actualizar los últimos 3 días. Vale la pena con tablas grandes que crecen, como las lecturas de 5 minutos. "
     "Para <i>fact_energia_dia</i>, que solo suma una fila por día, recargar todo es más simple y suficiente.",
     "Microsoft Learn, incremental refresh [9].")

story.append(P("Bloque 4 · Internet de las Cosas (IoT)", h2))
flujo = Table([[Paragraph(x, ParagraphStyle("d", parent=cel, alignment=TA_CENTER, textColor=colors.white, fontName="Helvetica-Bold"))
                for x in ["Inversor<br/>(dispositivo)", "Gateway<br/>(edge)", "Broker<br/>MQTT", "BRONZE<br/>csv crudo",
                          "SILVER<br/>lectura_5min", "GOLD<br/>fact_energia_dia", "Visual<br/>(Power BI / Grafana)"]]],
              colWidths=[2.3 * cm] * 7, rowHeights=[1.4 * cm])
flujo.setStyle(TableStyle([("BACKGROUND", (0, 0), (2, 0), colors.HexColor("#4B6A8F")),
                           ("BACKGROUND", (3, 0), (3, 0), colors.HexColor("#8C5A2B")),
                           ("BACKGROUND", (4, 0), (4, 0), colors.HexColor("#6B7280")),
                           ("BACKGROUND", (5, 0), (5, 0), colors.HexColor("#B7791F")),
                           ("BACKGROUND", (6, 0), (6, 0), colors.HexColor("#2F6B4F")),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("LINEAFTER", (0, 0), (5, 0), 2, colors.white),
                           ("BOX", (0, 0), (-1, -1), 0.5, colors.white)]))
resp("I1", "Arquitectura IoT por capas",
     "La arquitectura tiene cinco capas: el <b>dispositivo</b> (inversor y medidor con sensores), el <b>gateway o edge</b> (recoge los datos y los "
     "envía), la <b>red o broker</b> (por ejemplo un broker MQTT), el <b>almacenamiento</b> (PostgreSQL o un lago de datos) y la <b>aplicación</b> "
     "(Power BI o Grafana). Una lectura del inversor llega primero cruda a Bronze, después se limpia y queda en Silver, y al final se resume en Gold "
     "para el visual, como se ve en el diagrama.",
     "OASIS, MQTT 5.0 [5] y DAMA-DMBOK [3].",
     extra=[Spacer(1, 4), flujo, P("Figura 1. Recorrido de una lectura, de izquierda a derecha: cada caja es una capa por donde pasa el dato.", fuente)])

resp("I2", "MQTT",
     "MQTT es un protocolo liviano de mensajes de tipo <i>publish/subscribe</i>. Los dispositivos publican un mensaje en un <i>topic</i> "
     "(un texto jerárquico) hacia el <i>broker</i>, y el broker lo entrega a quienes están suscritos a ese topic; así quien publica y quien "
     "recibe no se conocen. QoS 0 envía a lo sumo una vez (puede perderse), QoS 1 al menos una vez (puede repetirse) y QoS 2 exactamente una vez "
     "(más lento). Para SolarBI, con lecturas cada 5 minutos, serviría QoS 1, porque las repetidas ya las limpia la regla de duplicados.",
     "OASIS, MQTT Version 5.0 [5].")
story.append(Preformatted(
    "pascualbravo/solar/sede1/inversor01/p_ac_kw\n"
    "pascualbravo/solar/sede1/inversor01/estado\n"
    "pascualbravo/solar/sede1/estacion01/irradiancia_wm2\n"
    "pascualbravo/solar/sede1/estacion01/temp_modulo_c", codigo))
story.append(Spacer(1, 6))

story.append(P("<b>I3.</b> Modbus, MQTT y OPC UA", h3))
story.append(tabla([
    ["", "Modbus (RTU/TCP)", "MQTT", "OPC UA"],
    ["Modelo de comunicación", "Maestro/esclavo: el maestro pregunta y el esclavo responde.",
     "Publish/subscribe con un broker en medio.", "Cliente/servidor (con opción publish/subscribe)."],
    ["Uso típico", "Leer registros de inversores, medidores y PLC.", "Enviar telemetría de dispositivos IoT hacia servidores o la nube.",
     "Integrar sistemas industriales y SCADA."],
    ["Formato de los datos", "Registros numéricos de 16 bits (hay que conocer el mapa).",
     "Mensaje libre (casi siempre JSON o texto).", "Modelo de información con tipos y nombres."],
    ["Seguridad", "Casi ninguna por sí solo (sin cifrado ni usuarios).", "Usuario y clave, y TLS para cifrar.",
     "Cifrado, certificados y autenticación incluidos."],
], [2.9 * cm, 4.6 * cm, 4.5 * cm, 4.6 * cm]))
story.append(P("En los inversores y medidores de una planta solar esperaríamos <b>Modbus</b> (RTU por RS-485 o TCP). El gateway puede publicarlo en "
               "<b>MQTT</b>, y OPC UA aparece en plantas grandes con SCADA. Fuente: Modbus Organization [11], OASIS [5] y OPC Foundation [8].", body))

resp("I4", "Batch vs. streaming y granularidad",
     "El procesamiento por lotes (<i>batch</i>) trabaja con datos acumulados en momentos fijos (el ETL de medianoche); el <i>streaming</i> procesa cada dato "
     "apenas llega. Al pasar de lecturas de 5 minutos a un resumen diario se gana: menos filas, consultas más rápidas y KPIs simples como energía diaria o yield. "
     "Se pierde el detalle: picos, caídas por nubes o fallas de pocos minutos, y no se puede ver lo que pasa ahora. Grafana atiende mejor la granularidad de 5 minutos "
     "(monitoreo) y Power BI la diaria (análisis).",
     "OASIS, MQTT 5.0 [5] y Microsoft Learn [2].")

story.append(P("Bloque 5 · Control de versiones", h2))
resp("V1", "Git, GitHub y versionado de tableros",
     "<b>Git</b> es el sistema que guarda el historial de cambios en nuestro equipo; <b>GitHub</b> es la plataforma en internet que aloja repositorios Git y "
     "permite trabajar en equipo. Un <i>repository</i> es la carpeta del proyecto con su historial, un <i>commit</i> es un punto guardado con un mensaje, una "
     "<i>branch</i> es una línea paralela de trabajo y un <i>pull request</i> es la solicitud para revisar y unir una rama. El .pbix es binario, así que Git no puede "
     "mostrar qué cambió ni mezclar cambios de dos personas; el formato .pbip guarda el proyecto en carpetas con archivos de texto y sí permite ver diferencias. "
     "Un dashboard de Grafana se exporta como JSON y se guarda en el repositorio.",
     "Pro Git [7] y Microsoft Learn, proyectos de Power BI Desktop [10].")

# ----------------------------------------------------------------- Parte B
story += [PageBreak(), P("Parte B · Práctica guiada: los mismos datos en dos herramientas", h1)]

story.append(P("Paso 1 · Bronze: datos crudos", h2))
story.append(P("Se usó el simulador base (<i>etl/simulador.py</i>), que genera 3 días de telemetría de un inversor de 5 kWp, con lecturas cada 5 minutos "
               "y anomalías inyectadas (potencia negativa, datos faltantes y filas duplicadas). Se agregó una semilla fija (<i>random.seed(42)</i>) para que "
               "los datos sean iguales en cada ejecución. El archivo <i>data/bronze/telemetria.csv</i> no se modifica después de generarse."))
story.append(caja_captura("Terminal con 'python etl/simulador.py' y las primeras filas de telemetria.csv", 4.2, "paso1"))

story.append(P("Paso 2 · Silver: reglas de calidad", h2))
story.append(P("Con Python (pandas) se aplicaron tres reglas en este orden: (1) duplicados, (2) datos faltantes en potencia o irradiancia y (3) rango físico "
               "válido (potencia entre 0 y 5,5 kW, irradiancia entre 0 y 1400 W/m<super>2</super> y temperatura entre -10 y 100 °C)."))
story.append(tabla([
    ["Concepto", "Filas"],
    ["Filas leídas (Bronze)", rep["filas_leidas"]],
    ["Rechazadas por duplicados", rep["rechazadas_duplicados"]],
    ["Rechazadas por datos faltantes", rep["rechazadas_faltantes"]],
    ["Rechazadas por rango físico (potencia negativa)", rep["rechazadas_rango_fisico"]],
    ["Filas válidas (Silver)", rep["filas_validas"]],
    ["Porcentaje de datos válidos", f"{rep['pct_datos_validos']} %"],
], [11 * cm, 4 * cm]))
story.append(Spacer(1, 4))
story.append(caja_captura("Salida del reporte de calidad en la terminal (python etl/run_etl.py)", 4.2, "paso2"))

story.append(P("Paso 3 · Gold: carga en PostgreSQL", h2))
story.append(P("El script <i>etl/run_etl.py</i> es el único punto de entrada: lee Bronze, limpia, y carga <i>silver.lectura_5min</i> y <i>dwh.fact_energia_dia</i> con UPSERT. "
               "La energía de cada intervalo es la potencia por 5/60 de hora. Se ejecutó tres veces y los conteos no cambiaron, lo que demuestra que la carga es idempotente."))
story.append(tabla([
    ["Ejecución", "silver.lectura_5min", "dwh.fact_energia_dia"],
    ["1", "832", "3"], ["2", "832", "3"], ["3", "832", "3"],
], [4 * cm, 5.5 * cm, 5.5 * cm]))
story.append(Spacer(1, 4))
story.append(P("Para correrlo cada día a la medianoche (sin implementarlo), la expresión cron sería: "
               "<font face='Courier'>0 0 * * * cd /ruta/al/repo &amp;&amp; python3 etl/run_etl.py</font>. "
               "En el Programador de tareas de Windows: desencadenador diario a las 12:00 a. m. y acción <i>python.exe etl\\run_etl.py</i>."))
story.append(caja_captura("Dos ejecuciones seguidas de run_etl.py con los mismos conteos + consulta COUNT(*) en PostgreSQL", 4.2, "paso3"))

story.append(P("Paso 4 · Power BI", h2))
story.append(P("Power BI Desktop se conectó a PostgreSQL (base <i>solarbi</i>). La página tiene una tarjeta con el yield (kWh/kWp), un gráfico de columnas con la "
               "energía diaria y una tarjeta con el ahorro estimado en COP. Todo sale de medidas DAX (<i>Energía kWh</i>, <i>Yield kWh/kWp</i> y <i>Ahorro COP</i>) y la tarifa es un "
               "parámetro. Fuente de la tarifa: " + pendiente(TARIFA_FUENTE, "tarifa de energía del operador, con enlace y fecha de consulta") + "."))
story.append(caja_captura("Página de Power BI con las dos tarjetas y el gráfico de columnas", 6, "paso4"))

story.append(P("Paso 5 · Grafana", h2))
story.append(P("Se instaló Grafana OSS y se agregó PostgreSQL como data source. El dashboard tiene: una serie de tiempo con irradiancia y potencia cada 5 minutos "
               "(consulta con <i>$__timeFilter</i>), un gauge con el porcentaje de datos válidos y umbrales de color (rojo menor a 90 %, amarillo de 90 a 95 % y verde desde 95 %), "
               "y una variable <i>dispositivo</i> aplicada en las consultas. El dashboard se exportó como JSON en <i>grafana/dashboard.json</i>."))
story.append(caja_captura("Dashboard de Grafana con los paneles y la variable de dispositivo", 6, "paso5"))

story.append(P("Paso 6 · Reflexión", h2))
story.append(P("Con los mismos datos, Power BI resolvió mejor los cálculos de negocio: el yield y el ahorro en COP salen de medidas DAX con un parámetro de tarifa y "
               "se entienden fácil en un informe. Grafana resolvió mejor la serie de tiempo cada 5 minutos y el monitoreo, con auto-refresh y umbrales de color "
               "que avisan rápido si el porcentaje de datos válidos baja. Lo que más nos costó fue "
               + pendiente(LO_QUE_COSTO, "su experiencia real, por ejemplo conectar PostgreSQL, escribir las medidas DAX o instalar Grafana") + ". "
               + "Para el operador de la planta usaríamos Grafana, porque necesita ver lo que pasa ahora y recibir alertas. Para un directivo usaríamos Power BI, "
               "porque necesita pocos indicadores resumidos, como la energía y el ahorro."))

# ----------------------------------------------------------------- Parte C
story += [PageBreak(), P("Parte C · Repositorio en GitHub", h1)]
story.append(P("<b>Enlace al repositorio:</b> " + pendiente(REPO_URL, "enlace del repositorio")))
story.append(P("El repositorio incluye README con nombres, curso, descripción, pasos para reproducir y tabla de quién hizo qué; un .gitignore que excluye el archivo .env; "
               "y la estructura pedida (docs, data, etl, sql, powerbi y grafana). No se subieron contraseñas ni cadenas de conexión."))
story.append(caja_captura("Settings > Collaborators con los dos integrantes", 5, "github_colaboradores"))
story.append(Spacer(1, 6))
story.append(caja_captura("Historial de commits (Commits) donde se vean los dos autores", 5, "github_commits"))

# ----------------------------------------------------------------- Referencias
story += [P("Referencias", h1)]
refs = [
    "[1] Grafana Labs. <i>Grafana documentation</i>. https://grafana.com/docs/grafana/latest/",
    "[2] Microsoft. <i>Power BI documentation</i>. Microsoft Learn. https://learn.microsoft.com/power-bi/",
    "[3] DAMA International. <i>DAMA-DMBOK: Data Management Body of Knowledge</i> (2.ª ed.). Technics Publications, 2017.",
    "[4] Congreso de la República de Colombia. <i>Ley 1581 de 2012</i>, por la cual se dictan disposiciones generales para la protección de datos personales. "
    "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981",
    "[5] OASIS. <i>MQTT Version 5.0</i>. https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html",
    "[6] Apache Software Foundation. <i>Apache Airflow documentation</i>. https://airflow.apache.org/docs/apache-airflow/stable/",
    "[7] Chacon, S. y Straub, B. <i>Pro Git</i>. https://git-scm.com/book",
    "[8] OPC Foundation. <i>OPC Unified Architecture</i>. https://opcfoundation.org/about/opc-technologies/opc-ua/",
    "[9] Microsoft. <i>Incremental refresh for semantic models in Power BI</i>. https://learn.microsoft.com/power-bi/connect-data/incremental-refresh-overview",
    "[10] Microsoft. <i>Power BI Desktop projects (PBIP)</i>. https://learn.microsoft.com/power-bi/developer/projects/projects-overview",
    "[11] Modbus Organization. <i>Modbus</i>. https://modbus.org",
    "[12] The PostgreSQL Global Development Group. <i>INSERT (ON CONFLICT)</i>. https://www.postgresql.org/docs/current/sql-insert.html",
]
for r in refs:
    story.append(P(r, ParagraphStyle("ref", parent=body, alignment=0, fontSize=9, leading=12, leftIndent=14, firstLineIndent=-14)))


# unir cada título con el elemento que le sigue (evita títulos sueltos al final de página)
nueva = []
i = 0
while i < len(story):
    it = story[i]
    if isinstance(it, Paragraph) and it.style.name in ("h1", "h2") and i + 1 < len(story):
        sig = story[i + 1]
        resto = list(sig._content) if isinstance(sig, KeepTogether) else [sig]
        nueva.append(KeepTogether([it] + resto))
        i += 2
    else:
        nueva.append(it)
        i += 1
story = nueva

def pie(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(2 * cm, 1.2 * cm, "Inteligencia de Negocios · Grupo 50 · Consulta SolarBI · 2026-II")
    canvas.drawRightString(letter[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                        topMargin=2 * cm, bottomMargin=2 * cm,
                        title="Consulta SolarBI - Inteligencia de Negocios G50")
doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=pie)

print("PDF creado:", OUT)
print("Palabras por respuesta:")
for c, n in conteo:
    print(c, n, "OK" if n <= 120 else "<<< PASA DE 120")
