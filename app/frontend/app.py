"""
app.py - Frontend Streamlit para el generador de pliegos multiagente.
"""

import time
import streamlit as st
import requests

API_URL = "http://localhost:8080/v1/agent-anlist/"


# ── Funcion auxiliar ───────────────────────────────────────────────────
async def stream_desde_api(payload):
    """
    Convierte la respuesta de la API en un generador que Streamlit entiende.
    """
    url = "http://localhost:8080/v1/agent-generator/"
    try:
        with requests.post(url, json={"prompt" : payload}, stream=True, timeout=600) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=None):
                if chunk:
                    yield chunk.decode("utf-8")
    except Exception as e:
        st.error(f"Error de conexión: {e}")


def generar_markdown_desde_json_indices(datos):
    """Convierte el JSON de la API en un string Markdown formateado"""
    if not datos:
        print("No hay datos para convertir")
        return ""

    md = f"## {datos.get('titulo', 'Pliego de Prescripciones')}\n\n"
    md += f"**Resumen:** {datos.get('resumen_proyecto', '')}\n\n"
    md += "---\n\n"

    for item in datos.get("apartados", []):
        titulo = item.get("titulo", "Sin título")
        desc = item.get("descripcion", "Sin descripción")
        md += f"* **{titulo}**: {desc}\n"

    return md


# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Generador de Pliegos PPT · IA Multiagente",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Estilos personalizados ────────────────────────────────────────────────────
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main { background: #0e1117; }

    /* Hero section */
    .hero-container {
        background: linear-gradient(135deg, #1a1f35 0%, #0d1117 50%, #1a2444 100%);
        border: 1px solid rgba(99, 130, 255, 0.2);
        border-radius: 16px;
        padding: 2.5rem 3rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6382ff, #a78df5, #6382ff);
        background-size: 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s infinite;
        margin-bottom: 0.5rem;
    }
    @keyframes shimmer {
        0% { background-position: 200% center; }
        100% { background-position: -200% center; }
    }
    .hero-subtitle {
        color: #8b9ab5;
        font-size: 1rem;
        margin-top: 0.5rem;
    }

    /* Cards */
    .card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Section labels */
    .section-label {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        color: #6382ff;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }

    /* Step badge */
    .step-badge {
        display: inline-block;
        background: rgba(99, 130, 255, 0.15);
        border: 1px solid rgba(99, 130, 255, 0.4);
        color: #7a95ff;
        border-radius: 20px;
        padding: 0.2rem 0.75rem;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* Progress log */
    .progress-log {
        background: #0d1117;
        border: 1px solid rgba(99, 130, 255, 0.15);
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 0.82rem;
        color: #c9d1d9;
        max-height: 320px;
        overflow-y: auto;
        line-height: 1.7;
    }

    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(90deg, #6382ff, #a78df5);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
        transition: opacity 0.2s;
    }
    .stDownloadButton > button:hover { opacity: 0.85; }

    /* Primary button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #6382ff, #a78df5);
        border: none;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
        padding: 0.75rem;
        transition: all 0.2s;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 25px rgba(99, 130, 255, 0.35);
    }

    /* Tags info */
    .info-tag {
        display: inline-block;
        background: rgba(99,130,255,0.1);
        border: 1px solid rgba(99,130,255,0.3);
        color: #7a95ff;
        border-radius: 6px;
        padding: 0.15rem 0.5rem;
        font-size: 0.78rem;
        margin: 0.1rem;
    }

    hr { border-color: rgba(255,255,255,0.07); }
</style>
""",
    unsafe_allow_html=True,
)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero-container">
    <div class="hero-title">📋 Generador de Pliegos PPT</div>
    <div class="hero-subtitle">
        Sistema multiagente con IA · Strands Agents + AWS Bedrock + RAG
    </div>
    <div style="margin-top: 1rem;">
        <span class="info-tag">🤖 Agente Analista</span>
        <span class="info-tag">🔍 Agente Buscador (RAG)</span>
        <span class="info-tag">✍️ Agente Redactor</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Formulario ────────────────────────────────────────────────────────────────
col_form, col_result = st.columns([1, 1], gap="large")

with col_form:
    st.markdown(
        '<div class="section-label">📝 Datos del proyecto</div>', unsafe_allow_html=True
    )

    tipo_proyecto = st.text_input(
        "Tipo de proyecto",
        placeholder="Ej: Suministro e instalación de equipos informáticos",
        help="Categoría o denominación del contrato",
    )
    descripcion = st.text_area(
        "Descripción del proyecto",
        placeholder="Describe en detalle el objeto del contrato, los servicios o suministros a contratar...",
        height=120,
        help="Cuanto más detallada, mejor será el pliego generado",
    )
    caracteristicas_tecnicas = st.text_area(
        "Características técnicas clave",
        placeholder='Ej: 200 equipos portátiles, procesador i5, 16GB RAM, pantalla 13", SO Windows 11...',
        height=90,
        help="Especificaciones técnicas, cantidades, modelos, estándares...",
    )

    col1, col2 = st.columns(2)
    with col1:
        plazo_ejecucion = st.text_input(
            "Plazo de ejecución",
            placeholder="Ej: 12 meses",
            help="Duración del contrato o plazo de entrega",
        )
    with col2:
        presupuesto = st.text_input(
            "Presupuesto base (IVA excluido)",
            placeholder="Ej: 250.000 €",
        )

    col3, col4 = st.columns(2)
    with col3:
        localizacion = st.text_input(
            "Localización / Ámbito",
            placeholder="Ej: Comunidad de Madrid",
        )
    with col4:
        selected_lang_name = st.selectbox(
            "Selecciona el idioma del pliego:",
            options=["Español", "Inglés", "Francés", "Alemán"],
        )

    max_pages = st.number_input(
        "Máximo de hojas del pliego", min_value=1, max_value=100, value=5
    )

    st.markdown("<br>", unsafe_allow_html=True)
    generar_btn = st.button(
        "🚀 Generar Pliego con IA",
        type="primary",
        disabled=not (
            tipo_proyecto
            and descripcion
            and caracteristicas_tecnicas
            and plazo_ejecucion
            and presupuesto
            and localizacion
            and selected_lang_name
            and max_pages
        ),
    )

# ── Resultados ────────────────────────────────────────────────────────────────
with col_result:
    st.markdown(
        '<div class="section-label">📊 Progreso y resultado</div>',
        unsafe_allow_html=True,
    )

    if "documento_final" not in st.session_state:
        st.session_state["documento_final"] = None
    if "log_mensajes" not in st.session_state:
        st.session_state["log_mensajes"] = []

    log_placeholder = st.empty()
    result_placeholder = st.empty()

    # Mostrar log previo si lo hay
    if st.session_state["log_mensajes"]:
        log_html = "<br>".join(st.session_state["log_mensajes"])
        log_placeholder.markdown(
            f'<div class="progress-log">{log_html}</div>', unsafe_allow_html=True
        )


# ── Acción principal ──────────────────────────────────────────────────────────
if "documento_final" not in st.session_state:
    st.session_state["documento_final"] = []
if "log_mensajes" not in st.session_state:
    st.session_state["log_mensajes"] = []
if "ejecutando_api" not in st.session_state:
    st.session_state["ejecutando_api"] = False
if "indices_creados" not in st.session_state:
    st.session_state["indices_creados"] = False
if "propuesta_indices" not in st.session_state:
    st.session_state["propuesta_indices"] = None
if "propuesta_doc_indice" not in st.session_state:
    st.session_state["propuesta_doc_indice"] = []
if "doc_indice_creados" not in st.session_state:
    st.session_state["doc_indice_creados"] = []
if "indice" not in st.session_state:
    st.session_state["indice"] = 1
st.session_state["log_mensajes"] = ["🚀 Iniciando agentes..."]

if generar_btn:
    st.session_state["ejecutando_api"] = True
    st.session_state["propuesta_doc_indice"] = []
    st.session_state["doc_indice_creados"] = []
    st.session_state["propuesta_indices"] = None
    st.session_state["indices_creados"] = False
    st.session_state["indice"] = 1
    st.session_state["log_mensajes"] = ["🚀 Iniciando proceso..."]
    indice = 1
    st.rerun()

if st.session_state["ejecutando_api"] or st.session_state["propuesta_indices"]:
    with col_result:
        if (
            st.session_state["propuesta_indices"] is None
            and st.session_state["ejecutando_api"]
        ):
            with st.spinner("🤖 Los agentes están trabajando..."):
                try:
                    with st.chat_message("assistant", avatar="🧐"):
                        payload = {
                            "tipo_proyecto": tipo_proyecto,
                            "descripcion": descripcion,
                            "caracteristicas_tecnicas": caracteristicas_tecnicas,
                            "plazo_ejecucion": plazo_ejecucion,
                            "presupuesto": presupuesto,
                            "lenguaje": selected_lang_name,
                            "max_pages": max_pages,
                            "localizacion": localizacion,
                        }

                        indices_res = requests.post(API_URL, json={"prompt": payload})

                        st.session_state["propuesta_indices"] = indices_res.json()[
                            "respuesta"
                        ]
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.session_state["ejecutando_api"] = False

        elif st.session_state["propuesta_indices"] is not None:
            with st.chat_message("assistant", avatar="🧐"):
                st.markdown(
                    generar_markdown_desde_json_indices(
                        st.session_state["propuesta_indices"]
                    )
                )

            if not st.session_state["indices_creados"]:
                st.write("---")
                c1, c2 = st.columns(2)

                if c1.button("✅ Aceptar", type="primary", key="acepta_final"):
                    st.session_state["indices_creados"] = True
                    lista_apartados = st.session_state["propuesta_indices"].get(
                        "apartados", []
                    )
                    cantidad = len(lista_apartados)
                    st.session_state["cantidad"] = cantidad
                    st.session_state["propuesta_doc_indice"] = [None] * cantidad
                    st.session_state["doc_indice_creados"] = [False] * cantidad
                    st.session_state["log_mensajes"].append(
                        "Indices creados correctamente."
                    )
                    st.rerun()

                if c2.button("❌ Rechazar indices", key="rechaza_final"):
                    st.session_state["propuesta_indices"] = None
                    st.session_state["indices_creados"] = False
                    st.session_state["log_mensajes"].append("Indices rechazados.")
                    st.rerun()

# ── Acción principal grafo ──────────────────────────────────────────────────────────
if st.session_state["indices_creados"]:
    if (
        st.session_state["ejecutando_api"]
        or st.session_state["propuesta_doc_indice"][st.session_state["indice"] - 1]
    ):
        with col_result:
            if (
                st.session_state["propuesta_doc_indice"][st.session_state["indice"] - 1]
                is None
                and st.session_state["ejecutando_api"]
            ):
                try:
                    with st.chat_message("assistant", avatar="🧐"):
                        # doc_indice = st.write_stream(
                        # stream_desde_api({"indice" : st.session_state["indice"]})
                        # # requests.post("http://localhost:8080/v1/agent-generator/", json={"prompt" : {"indice" : st.session_state["indice"]}}, stream=True, timeout=600)
                        # )
                        doc_indice = requests.post("http://localhost:8080/v1/agent-generator/", json={"prompt" : {"indice" : st.session_state["indice"]}})
                        st.session_state["propuesta_doc_indice"][
                            st.session_state["indice"] - 1
                        ] = doc_indice.json()["respuesta"]

                        # indices_res = requests.post(API_URL, json={"prompt": payload})

                        # st.session_state["propuesta_indices"] = indices_res.json()[
                        #     "respuesta"
                        # ]

                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.session_state["ejecutando_api"] = False

            elif (
                st.session_state["propuesta_doc_indice"][st.session_state["indice"] - 1]
                is not None
            ):
                with st.chat_message("assistant", avatar="🧐"):
                    st.markdown(
                        st.session_state["propuesta_doc_indice"][
                            st.session_state["indice"] - 1
                        ]
                    )

                if not st.session_state["doc_indice_creados"][
                    st.session_state["indice"] - 1
                ]:
                    st.write("---")
                    c1, c2 = st.columns(2)

                    if c1.button("✅ Aceptar", type="primary", key="acepta_final"):
                        st.session_state["doc_indice_creados"][
                            st.session_state["indice"] - 1
                        ] = True
                        st.session_state["documento_final"].append(st.session_state[
                            "propuesta_doc_indice"
                        ][st.session_state["indice"] - 1])
                        st.session_state["log_mensajes"].append(
                            f"Documento sobre indice {st.session_state.get('indice') - 1} creado correctamente."
                        )
                        if st.session_state["indice"] < (
                            st.session_state["cantidad"] - 1
                        ):
                            st.session_state["indice"] += 1
                        st.rerun()

                    if c2.button("❌ Rechazar indices", key="rechaza_final"):
                        st.session_state["propuesta_doc_indice"][
                            st.session_state["indice"] - 1
                        ] = None
                        st.session_state["doc_indice_creados"][
                            st.session_state["indice"] - 1
                        ] = False
                        st.session_state["log_mensajes"].append(
                            f"Documento sobre indice {st.session_state.get('indice') - 1} rechazado."
                        )
                        st.rerun()


# ── Mostrar documento final ───────────────────────────────────────────────────
if st.session_state.get("documento_final") and st.session_state.get("indices_creados"):
    doc = st.session_state["documento_final"]

    with col_result:
        st.success("✅ ¡Pliego generado correctamente!")
        st.download_button(
            label="⬇️ Descargar Pliego (.md)",
            data=doc.encode("utf-8"),
            file_name="pliego_prescripciones_tecnicas.md",
            mime="text/markdown",
        )

    st.divider()
    st.subheader("📄 Vista previa del pliego generado")
    st.markdown(doc)

    st.divider()
    col_dl1, col_dl2 = st.columns([1, 3])
    with col_dl1:
        st.download_button(
            label="⬇️ Descargar Pliego (.md)",
            data=doc.encode("utf-8"),
            file_name="pliego_prescripciones_tecnicas.md",
            mime="text/markdown",
            key="download_bottom",
        )


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "📋 Generador de Pliegos PPT · "
    "Powered by **AWS Bedrock** + **Strands Agents** + **ChromaDB** · "
    "Proyecto Final Módulo 5"
)
