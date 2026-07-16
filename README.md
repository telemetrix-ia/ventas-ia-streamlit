# 🖥️ MCP Agent - Sistema de Ventas de Computadoras

Agente conversacional con **memoria** y **3 herramientas** para consultar un sistema de ventas de computadoras, usando **LangChain** + **NVIDIA Nemotron** (gratuito vía OpenRouter).

## 📁 Estructura del proyecto

```
mcp-colab/
├── mcp_agent.py                  # MCP Agent con memoria conversacional
├── streamlit_app.py              # Frontend Streamlit (chat UI)
├── setup_db.py                   # Genera CSVs + base SQLite
├── ventas_computadoras_colab.py  # Version para Google Colab
├── ventas_computadoras.db        # Base de datos SQLite
├── datos/                        # CSVs del dataset
│   ├── productos.csv
│   ├── clientes.csv
│   ├── ventas.csv
│   └── detalle_ventas.csv
└── README.md
```

## ⚙️ Requisitos

- Python 3.10+
- API Key de [OpenRouter](https://openrouter.ai/keys) (modelo gratuito `nvidia/nemotron-3-ultra-550b-a55b:free`)

## 🚀 Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd mcp-colab
```

### 2. Crear entorno virtual (opcional pero recomendado)

```bash
python -m venv .venx
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac
```

### 3. Instalar dependencias

```bash
pip install langchain langchain-community langchain-openai pandas openai streamlit tabulate
```

> En Windows PowerShell puede añadir `requests==2.32.4` para evitar warnings con google-colab.

### 4. Inicializar la base de datos (solo primera vez)

```bash
python setup_db.py
```

Genera 4 archivos CSV en `datos/` y la base SQLite `ventas_computadoras.db` con:
- 20 productos
- 20 clientes
- 100 ventas
- 314 detalles

### 5. Configurar API Key

**Opción A - Variable de entorno (recomendada):**

```bash
set OPENROUTER_API_KEY=sk-or-v1-xxxxx
```

**Opción B - El sistema te la pedirá al ejecutar:**

Al iniciar el agente, te aparecerá un prompt para ingresar la key.

### 6. Ejecutar

#### 🔹 Modo CLI (con tracing en consola)

```bash
python mcp_agent.py
```

Comandos disponibles durante la sesion:
- `salir` / `exit` - Terminar
- `memoria` - Ver el historial de la conversacion
- `trazas` - Ver el log de herramientas invocadas

#### 🔸 Modo Streamlit (interfaz grafica)

```bash
streamlit run streamlit_app.py
```

Se abrira en `http://localhost:8501`. Interfaz con:
- Chat historico
- Sidebar con informacion del sistema
- Expander para ver llamadas a herramientas
- Boton para limpiar memoria

#### 🔹 Google Colab

1. Abre [Google Colab](https://colab.research.google.com)
2. Carga `ventas_computadoras_colab.py` o copia cada celda manualmente
3. Ejecuta celda por celda
4. Cuando llegues a la configuracion de API Key, te aparecera un input seguro

## 🛠️ Herramientas del agente

| Tool | Descripcion | Ejemplos de uso |
|------|-------------|-----------------|
| `consultar_catalogo` | Busca productos por nombre, categoria o marca | "laptops", "mouse logitech", "monitores" |
| `consultar_ventas` | Historial de ventas por cliente o numero | "ventas de Carlos Lopez", "venta #5" |
| `consultar_estadisticas` | Metricas: top productos, ingresos, categorias | "top 5 productos", "ingresos totales" |

## 💬 Ejemplos de preguntas

```
> Que laptops tienen en stock?
> Cuales son los 5 productos mas vendidos?
> Quien es el cliente que mas ha comprado?
> Cuanto ingreso total se genero?
> Ventas por categoria
> Que mouse tienen disponibles?
> Muestrame las ventas de Maria Garcia
```

## 🧠 Memoria conversacional

El agente recuerda las ultimas **6 interacciones** (pregunta + respuesta). Puedes hacer preguntas de seguimiento:

```
> Que laptops tienen?
> Cual es la mas cara de esas?
> Y la mas barata?
```

## 📊 Modelo usado

- **Modelo:** `nvidia/nemotron-3-ultra-550b-a55b:free` (gratuito)
- **Proveedor:** [OpenRouter](https://openrouter.ai/)
- **API:** OpenAI-compatible (ChatOpenAI + OpenRouter base_url)
- **Rate limit:** 32 requests/worker (el sistema reintenta automaticamente)

## 🔄 Arquitectura

```
Usuario → Streamlit/CLI → MCPAgent (LangChain)
                             ├── consultar_catalogo → SQLite
                             ├── consultar_ventas    → SQLite
                             └── consultar_estadisticas → SQLite
                        Memoria (ConversationBufferWindowMemory)
                        Tracing (ToolTracingHandler)
```
