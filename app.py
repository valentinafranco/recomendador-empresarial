import sqlite3
import json
from datetime import datetime

import streamlit as st

# Configuración de la aplicación
st.set_page_config(
    page_title="Diagnóstico empresarial",
    page_icon="📊",
    layout="centered"
)

DB_PATH = "diagnostico.db"


# Crear la base de datos
def crear_base_datos():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS respuestas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                empresa TEXT NOT NULL,
                sector TEXT NOT NULL,
                tamano TEXT NOT NULL,
                necesidades TEXT NOT NULL,
                sistemas TEXT NOT NULL,
                nivel TEXT NOT NULL
            )
        """)


# Guardar un diagnóstico
def guardar_respuesta(datos):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            INSERT INTO respuestas (
                fecha, empresa, sector, tamano,
                necesidades, sistemas, nivel
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, datos)

        return cursor.lastrowid


# Inicializar la base de datos
crear_base_datos()


# Título y descripción
st.title("Diagnóstico de necesidades empresariales")
st.write(
    "Completa este formulario para identificar "
    "las necesidades tecnológicas de tu empresa."
)

st.caption("Prototipo de prueba · Versión 1.0")


# Formulario
with st.form("formulario_diagnostico"):

    st.subheader("Información de la empresa")

    empresa = st.text_input(
        "Nombre de la empresa",
        value="Empresa de prueba",
        max_chars=150
    )

    sector = st.selectbox(
        "Sector económico",
        [
            "Telecomunicaciones",
            "Manufactura",
            "Servicios financieros",
            "Comercio",
            "Tecnología",
            "Salud",
            "Otro"
        ],
        index=0
    )

    tamano = st.selectbox(
        "Tamaño de la empresa",
        ["Pequeña", "Mediana", "Grande"],
        index=1
    )

    st.divider()
    st.subheader("Necesidades y herramientas")

    opciones = [
        "Planeación financiera",
        "Consolidación de información",
        "Integración de datos",
        "Automatización de procesos",
        "Business Intelligence y dashboards",
        "Analítica avanzada",
        "Inteligencia artificial"
    ]

    necesidades = st.multiselect(
        "¿Qué necesita mejorar tu empresa?",
        opciones,
        default=["Integración de datos"]
    )

    sistemas = st.selectbox(
        "¿Qué herramientas utiliza actualmente?",
        [
            "Excel",
            "Power BI",
            "ERP",
            "Bases de datos SQL",
            "Varias herramientas desconectadas",
            "Otras"
        ],
        index=0
    )

    nivel = st.selectbox(
        "Nivel de madurez analítica",
        ["Básico", "Intermedio", "Avanzado"],
        index=1
    )

    enviar = st.form_submit_button(
        "Guardar diagnóstico",
        type="primary",
        use_container_width=True
    )


# Validar y guardar
if enviar:
    empresa = empresa.strip()

    if not empresa:
        st.error("Ingresa el nombre de la empresa.")

    elif not necesidades:
        st.error("Selecciona al menos una necesidad.")

    else:
        try:
            fecha = datetime.now().astimezone().isoformat(
                timespec="seconds"
            )

            datos = (
                fecha,
                empresa,
                sector,
                tamano,
                json.dumps(necesidades, ensure_ascii=False),
                sistemas,
                nivel
            )

            registro_id = guardar_respuesta(datos)

            st.success(
                f"¡Diagnóstico guardado! Número de registro: "
                f"{registro_id}"
            )

        except sqlite3.Error:
            st.error(
                "No se pudo guardar el diagnóstico. "
                "Inténtalo nuevamente."
            )


# Mostrar registros guardados
st.divider()
st.subheader("Diagnósticos registrados")

with sqlite3.connect(DB_PATH) as conn:
    conn.row_factory = sqlite3.Row

    registros = conn.execute("""
        SELECT id, fecha, empresa, sector, tamano,
               necesidades, sistemas, nivel
        FROM respuestas
        ORDER BY id DESC
    """).fetchall()

if registros:
    filas = []

    for r in registros:
        fila = dict(r)
        fila["necesidades"] = ", ".join(
            json.loads(fila["necesidades"])
        )
        filas.append(fila)

    st.dataframe(
        filas,
        use_container_width=True,
        hide_index=True
    )

    st.caption(f"Total de registros: {len(filas)}")

else:
    st.info(
        "Todavía no hay registros. "
        "Completa el formulario para comenzar."
    )
