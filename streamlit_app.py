"""
Streamlit Frontend - Sistema de Ventas de Computadoras
======================================================
Chat UI para interactuar con el MCP Agent con memoria.
"""

import streamlit as st
import time
from datetime import datetime

from mcp_agent import MCPAgent


# ============================================================
# CONFIGURACION DE PAGINA
# ============================================================

st.set_page_config(
    page_title="Sistema Ventas - MCP Agent",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# ESTILOS CSS
# ============================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 1.5rem;
    }
    .tool-call {
        background-color: #1a1a2e;
        color: #00ff88;
        padding: 8px 12px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 0.8rem;
        margin: 4px 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    .stChatInput {
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: white;
        padding: 10px 0;
        z-index: 100;
    }
    .chat-container {
        margin-bottom: 80px;
    }
    .memory-info {
        font-size: 0.75rem;
        color: #888;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# INICIALIZAR AGENTE EN SESSION STATE
# ============================================================

@st.cache_resource
def init_agent():
    return MCPAgent(verbose=False)

if "agent" not in st.session_state:
    st.session_state.agent = init_agent()
if "messages" not in st.session_state:
    st.session_state.messages = []

agent = st.session_state.agent


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🖥️ MCP Ventas")
    st.markdown("---")
    st.markdown("### Herramientas disponibles")
    st.info("🔍 **consultar_catalogo**\nBusca productos por nombre, categoría o marca.")
    st.info("📊 **consultar_ventas**\nHistorial de ventas por cliente o número.")
    st.info("📈 **consultar_estadisticas**\nMétricas: top productos, ingresos, etc.")

    st.markdown("---")
    st.markdown("### Memoria conversacional")
    st.markdown(f"<p class='memory-info'>Ventanas de contexto: {agent.memory_window} intercambios</p>", unsafe_allow_html=True)

    if st.button("🗑️ Limpiar memoria", use_container_width=True):
        agent.clear_memory()
        st.session_state.messages = []
        st.success("Memoria y chat limpiados.")
        st.rerun()

    st.markdown("---")
    st.markdown("### Info del modelo")
    st.markdown(f"**Modelo:** `{agent.llm.model}`")
    st.markdown(f"**Proveedor:** OpenRouter")

    st.markdown("---")
    st.markdown("### Dataset")
    st.markdown("📦 `ventas_computadoras.db`")
    st.markdown("- 20 productos")
    st.markdown("- 20 clientes")
    st.markdown("- 100 ventas registradas")


# ============================================================
# CHAT PRINCIPAL
# ============================================================

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown('<p class="main-header">🖥️ Sistema de Ventas</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Asistente MCP con memoria • Consulta productos, ventas y estadísticas</p>', unsafe_allow_html=True)

with col2:
    st.markdown("")
    st.markdown("")
    total_preguntas = len(agent.chat_history) // 2
    st.metric("Preguntas realizadas", total_preguntas)


# ============================================================
# CONTENEDOR DE CHAT
# ============================================================

chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])
            if "tools" in msg and msg["tools"]:
                with st.expander("🔧 Ver llamadas a herramientas", expanded=False):
                    for t in msg["tools"]:
                        st.markdown(f"<div class='tool-call'>🛠️ {t['tool']}({t['input']})<br>↳ {t['output'][:200]}</div>", unsafe_allow_html=True)

    # Input fijo al fondo
    prompt = st.chat_input("Escribe tu consulta... (ej: ¿Qué laptops tienes?)")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            placeholder.markdown("_Pensando..._")

            try:
                trazas_antes = len(agent.get_trace_history())
                respuesta = agent.ask(prompt)
                trazas_despues = agent.get_trace_history()

                nuevas_trazas = trazas_despues[trazas_antes:]
                tools_data = [
                    {"tool": t["tool"], "input": t["input"], "output": t["output"]}
                    for t in nuevas_trazas if t["evento"] == "tool_start"
                ]

                placeholder.markdown(respuesta)

                if tools_data:
                    with st.expander("🔧 Ver llamadas a herramientas", expanded=False):
                        for t in tools_data:
                            st.markdown(f"<div class='tool-call'>🛠️ {t['tool']}({t['input']})<br>↳ {t['output'][:300]}</div>", unsafe_allow_html=True)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": respuesta,
                    "tools": tools_data
                })

            except Exception as e:
                placeholder.error(f"Error: {e}")


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888; font-size: 0.8rem;'>"
    "MCP Agent con memoria • Sistema de Ventas de Computadoras "
    f"• {datetime.now().strftime('%Y')}</p>",
    unsafe_allow_html=True
)
