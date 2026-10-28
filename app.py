import logging

import streamlit as st
from supabase import create_client


# --------------------------------------------------
# 1. CONFIGURACIÓN
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Diagnóstico empresarial",
    page_icon="📊",
    layout="centered"
)


@st.cache_resource
def conectar_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


try:
    supabase = conectar_supabase()
except Exception:
    logger.exception("Error al conectar con Supabase")
    st.error(
        "No fue posible iniciar el servicio. "
        "Inténtalo más tarde."
    )
    st.stop()


# --------------------------------------------------
# 2. REGLAS DE RECOMENDACIÓN PARA LA DEMOSTRACIÓN
# --------------------------------------------------

PUNTUACIONES = {
    "Planeación financiera": {
        "Pigment": 3,
        "CCH Tagetik": 3,
        "Anaplan": 3,
        "Microsoft Fabric": 1
    },
    "Consolidación de información": {
        "Pigment": 1,
        "CCH Tagetik": 3,
        "Anaplan": 1,
        "Microsoft Fabric": 2
    },
    "Integración de datos": {
        "Pigment": 1,
        "CCH Tagetik": 1,
        "Anaplan": 1,
        "Microsoft Fabric": 3
    },
    "Automatización de procesos": {
        "Pigment": 2,
        "CCH Tagetik": 2,
        "Anaplan": 2,
        "Microsoft Fabric": 2
    },
    "Business Intelligence y dashboards": {
        "Pigment": 1,
        "CCH Tagetik": 1,
        "Anaplan": 1,
        "Microsoft Fabric": 3
    },
    "Analítica avanzada": {
        "Pigment": 2,
        "CCH Tagetik": 1,
        "Anaplan": 2,
        "Microsoft Fabric": 3
    },
    "Inteligencia artificial": {
        "Pigment": 1,
        "CCH Tagetik": 1,
        "Anaplan": 1,
        "Microsoft Fabric": 3
    }
}

SOLUCIONES = [
    "Pigment",
    "CCH Tagetik",
    "Anaplan",
    "Microsoft Fabric"
]


def calcular_resultados(necesidades):
    puntuacion_maxima = len(necesidades) * 3
    resultados = []

    for solucion in SOLUCIONES:
        puntuacion = sum(
            PUNTUACIONES[necesidad][solucion]
            for necesidad in necesidades
        )

        coincidencias = [
            necesidad
            for necesidad in necesidades
            if PUNTUACIONES[necesidad][solucion] >= 2
        ]

        resultados.append({
            "solucion_recomendada": solucion,
            "puntuacion": puntuacion,
            "puntuacion_maxima": puntuacion_maxima,
            "porcentaje": round(
                puntuacion / puntuacion_maxima * 100, 2
            ),
            "coincidencias": coincidencias
        })

    return resultados


# --------------------------------------------------
# 3. GUARDAR DIAGNÓSTICO Y RESULTADOS
# --------------------------------------------------

def procesar_diagnostico(datos):
    # Primero guardamos las respuestas originales.
    respuesta = (
        supabase.table("respuestas")
        .insert(datos)
        .execute()
    )

    if not respuesta.data:
        raise RuntimeError("No se confirmó el diagnóstico.")

    diagnostico = respuesta.data[0]
    diagnostico_id = diagnostico["id"]

    # Calculamos las cuatro puntuaciones automáticamente.
    resultados = calcular_resultados(datos["necesidades"])

    # Cada fila queda relacionada con el diagnóstico original.
    filas_resultados = []

    for resultado in resultados:
        filas_resultados.append({
            "diagnostico_id": diagnostico_id,
            "empresa": datos["empresa"],
            "sector": datos["sector"],
            "tamano": datos["tamano"],
            "necesidades": datos["necesidades"],
            "solucion_recomendada":
                resultado["solucion_recomendada"],
            "puntuacion": resultado["puntuacion"],
            "puntuacion_maxima":
                resultado["puntuacion_maxima"],
            "porcentaje": resultado["porcentaje"],
            "coincidencias": resultado["coincidencias"],
            "modelo_version": "reglas_demo_v1"
        })

    # Guardamos los resultados para el análisis interno.
    supabase.table("resultados_modelo").insert(
        filas_resultados
    ).execute()

    return diagnostico_id


# --------------------------------------------------
# 4. FORMULARIO PÚBLICO
# --------------------------------------------------

st.title("Diagnóstico de necesidades empresariales")

st.write(
    "Completa este formulario para ayudarnos a comprender "
    "las necesidades tecnológicas de tu empresa."
)

st.caption("Formulario de diagnóstico empresarial")

with st.form("formulario_diagnostico"):

    st.subheader("Información de la empresa")

    empresa = st.text_input(
        "Nombre de la empresa",
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
        ]
    )

    tamano = st.selectbox(
        "Tamaño de la empresa",
        ["Pequeña", "Mediana", "Grande"],
        index=1
    )

    st.divider()
    st.subheader("Necesidades y herramientas")

    necesidades = st.multiselect(
        "¿Qué necesita mejorar tu empresa?",
        list(PUNTUACIONES.keys()),
        default=[]
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
        ]
    )

    nivel = st.selectbox(
        "Nivel de madurez analítica",
        ["Básico", "Intermedio", "Avanzado"],
        index=1
    )

    enviar = st.form_submit_button(
        "Enviar diagnóstico",
        type="primary",
        use_container_width=True
    )


# --------------------------------------------------
# 5. PROCESAMIENTO AUTOMÁTICO
# --------------------------------------------------

if enviar:
    empresa = empresa.strip()

    if not empresa:
        st.error("Ingresa el nombre de la empresa.")

    elif not necesidades:
        st.error("Selecciona al menos una necesidad.")

    else:
        datos = {
            "empresa": empresa,
            "sector": sector,
            "tamano": tamano,
            "necesidades": necesidades,
            "sistemas": sistemas,
            "nivel": nivel
        }

        try:
            procesar_diagnostico(datos)

            st.success(
                "¡Gracias! Tu diagnóstico fue recibido "
                "correctamente."
            )
            st.write(
                "La información se ha registrado. "
                "Puedes cerrar esta página."
            )

        except Exception:
            logger.exception(
                "Error al guardar o procesar un diagnóstico"
            )
            st.error(
                "No fue posible completar el procesamiento. "
                "Inténtalo nuevamente más tarde."
            )
