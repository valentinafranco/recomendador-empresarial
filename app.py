
import streamlit as st
from supabase import create_client


# Configuración de la aplicación
st.set_page_config(
    page_title="Diagnóstico empresarial",
    page_icon="📊",
    layout="centered"
)


# Conexión con Supabase
@st.cache_resource
def conectar_supabase():
    url = st.secrets["SUPABASE_URL"]
    clave = st.secrets["SUPABASE_KEY"]
    return create_client(url, clave)


try:
    supabase = conectar_supabase()
except Exception:
    st.error(
        "No se pudo conectar con la base de datos. "
        "Verifica la configuración de Secrets en Streamlit."
    )
    st.stop()


# Guardar un diagnóstico
def guardar_respuesta(datos):
    respuesta = (
        supabase.table("respuestas")
        .insert(datos)
        .execute()
    )

    if not respuesta.data:
        raise RuntimeError("No se recibió confirmación del registro.")

    return respuesta.data[0]["id"]


# Consultar los diagnósticos registrados
def obtener_respuestas():
    respuesta = (
        supabase.table("respuestas")
        .select(
            "id, fecha, empresa, sector, tamano, "
            "necesidades, sistemas, nivel"
        )
        .order("id", desc=True)
        .execute()
    )

    return respuesta.data or []


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
            datos = {
                "empresa": empresa,
                "sector": sector,
                "tamano": tamano,
                "necesidades": necesidades,
                "sistemas": sistemas,
                "nivel": nivel
            }

            registro_id = guardar_respuesta(datos)

            st.success(
                f"¡Diagnóstico guardado en la nube! "
                f"Número de registro: {registro_id}"
            )

        except Exception:
            st.error(
                "No se pudo guardar el diagnóstico. "
                "Verifica la conexión y la configuración "
                "de la base de datos."
            )


# Mostrar registros guardados en Supabase
st.divider()
st.subheader("Diagnósticos registrados")

try:
    registros = obtener_respuestas()

    if registros:
        filas = []

        for registro in registros:
            fila = dict(registro)

            necesidades_guardadas = fila.get("necesidades") or []

            if isinstance(necesidades_guardadas, list):
                fila["necesidades"] = ", ".join(
                    necesidades_guardadas
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

except Exception:
    st.error(
        "No se pudieron consultar los diagnósticos. "
        "Verifica la conexión y los permisos de la base de datos."
    )
