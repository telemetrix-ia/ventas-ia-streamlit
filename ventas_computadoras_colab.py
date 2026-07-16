# ============================================================
# CELDA 1: INSTALAR DEPENDENCIAS
# ============================================================
# Los warnings de dependencias cruzadas son inofensivos en Colab
# !pip install -q langchain langchain-community langchain-openai pandas openai tabulate requests==2.32.4

# ============================================================
# CELDA 2: IMPORTACIONES
# ============================================================
import sqlite3
import pandas as pd
import os
import json
import re
import getpass
import time
from datetime import datetime, timedelta
import random

# ============================================================
# CELDA 3: CREAR DATASET CSV DE VENTAS DE COMPUTADORAS
# ============================================================

def crear_dataset():
    random.seed(42)

    productos = [
        [1, "Laptop ThinkPad X1 Carbon", "Laptop", "Lenovo", 24999.00, 15],
        [2, "Laptop MacBook Pro 14", "Laptop", "Apple", 35999.00, 10],
        [3, "Laptop Dell XPS 15", "Laptop", "Dell", 28999.00, 12],
        [4, "PC Desktop Ryzen 7", "Desktop", "AMD", 18999.00, 8],
        [5, "PC Desktop Intel i9", "Desktop", "Intel", 21999.00, 6],
        [6, "Monitor LG 27 4K", "Monitor", "LG", 6999.00, 20],
        [7, "Monitor Samsung 32 Curvo", "Monitor", "Samsung", 8499.00, 15],
        [8, "Teclado Mecanico Razer", "Teclado", "Razer", 2499.00, 30],
        [9, "Teclado Logitech MX Keys", "Teclado", "Logitech", 2199.00, 25],
        [10, "Mouse Logitech MX Master 3", "Mouse", "Logitech", 1799.00, 28],
        [11, "Mouse Razer DeathAdder", "Mouse", "Razer", 1299.00, 35],
        [12, "Audifonos Sony WH-1000XM5", "Audifonos", "Sony", 5499.00, 18],
        [13, "Webcam Logitech C920", "Webcam", "Logitech", 1599.00, 22],
        [14, "Disco SSD Samsung 1TB", "Almacenamiento", "Samsung", 2199.00, 40],
        [15, "Disco SSD WD 500GB", "Almacenamiento", "WD", 1299.00, 45],
        [16, "Memoria RAM Kingston 16GB", "RAM", "Kingston", 899.00, 50],
        [17, "Memoria RAM Corsair 32GB", "RAM", "Corsair", 1699.00, 30],
        [18, "Tarjeta Grafica RTX 4060", "GPU", "NVIDIA", 8999.00, 5],
        [19, "Tarjeta Grafica RTX 4090", "GPU", "NVIDIA", 24999.00, 3],
        [20, "Impresora HP LaserJet", "Impresora", "HP", 4599.00, 10],
    ]
    cols_productos = ["id", "nombre", "categoria", "marca", "precio", "stock"]
    df_productos = pd.DataFrame(productos, columns=cols_productos)

    nombres = [
        "Carlos Lopez", "Maria Garcia", "Juan Perez", "Ana Martinez",
        "Luis Rodriguez", "Sofia Hernandez", "Pedro Sanchez", "Elena Torres",
        "Diego Ramirez", "Laura Flores", "Andres Morales", "Valeria Ortiz",
        "Fernando Castillo", "Gabriela Reyes", "Ricardo Mendoza", "Isabel Cruz",
        "Jorge Navarro", "Patricia Vega", "Alberto Rios", "Monica Delgado"
    ]
    clientes = []
    for i, nombre in enumerate(nombres, 1):
        email = nombre.lower().replace(" ", ".") + "@email.com"
        telefono = f"55{random.randint(10000000, 99999999)}"
        clientes.append([i, nombre, email, telefono, "Ciudad de Mexico"])
    cols_clientes = ["id", "nombre", "email", "telefono", "direccion"]
    df_clientes = pd.DataFrame(clientes, columns=cols_clientes)

    ventas = []
    detalle = []
    detalle_id = 1
    for venta_id in range(1, 101):
        cliente_id = random.randint(1, 20)
        dias_atras = random.randint(0, 365)
        fecha = (datetime.now() - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
        num_items = random.randint(1, 5)
        total = 0
        for _ in range(num_items):
            prod = random.choice(productos)
            cant = random.randint(1, 3)
            precio = prod[4]
            subtotal = precio * cant
            total += subtotal
            detalle.append([detalle_id, venta_id, prod[0], cant, precio])
            detalle_id += 1
        ventas.append([venta_id, cliente_id, fecha, round(total, 2)])
    cols_ventas = ["id", "cliente_id", "fecha", "total"]
    df_ventas = pd.DataFrame(ventas, columns=cols_ventas)
    cols_detalle = ["id", "venta_id", "producto_id", "cantidad", "precio_unitario"]
    df_detalle = pd.DataFrame(detalle, columns=cols_detalle)

    os.makedirs("datos", exist_ok=True)
    df_productos.to_csv("datos/productos.csv", index=False)
    df_clientes.to_csv("datos/clientes.csv", index=False)
    df_ventas.to_csv("datos/ventas.csv", index=False)
    df_detalle.to_csv("datos/detalle_ventas.csv", index=False)
    print("Dataset creado exitosamente en la carpeta 'datos/'")
    return df_productos, df_clientes, df_ventas, df_detalle

df_productos, df_clientes, df_ventas, df_detalle = crear_dataset()

# ============================================================
# CELDA 4: CREAR BASE DE DATOS SQLITE
# ============================================================

conn = sqlite3.connect("ventas_computadoras.db")
cursor = conn.cursor()

cursor.executescript("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        categoria TEXT NOT NULL,
        marca TEXT NOT NULL,
        precio REAL NOT NULL,
        stock INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        email TEXT NOT NULL,
        telefono TEXT NOT NULL,
        direccion TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY,
        cliente_id INTEGER NOT NULL,
        fecha TEXT NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    );

    CREATE TABLE IF NOT EXISTS detalle_ventas (
        id INTEGER PRIMARY KEY,
        venta_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        FOREIGN KEY (venta_id) REFERENCES ventas(id),
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    );
""")

df_productos.to_sql("productos", conn, if_exists="replace", index=False)
df_clientes.to_sql("clientes", conn, if_exists="replace", index=False)
df_ventas.to_sql("ventas", conn, if_exists="replace", index=False)
df_detalle.to_sql("detalle_ventas", conn, if_exists="replace", index=False)
conn.commit()
print("Base de datos SQLite creada y datos cargados exitosamente.")

# ============================================================
# CELDA 5: IMPORTAR LANGCHAIN Y CONFIGURAR TRACING
# ============================================================
# !pip install -q langchain langchain-community langchain-openai pandas openai tabulate requests==2.32.4

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.callbacks.base import BaseCallbackHandler

# --- TRACING: Callback personalizado para trazar tools ---
class ToolTracingHandler(BaseCallbackHandler):
    def __init__(self):
        self.historial = []

    def on_tool_start(self, serialized, input_str, **kwargs):
        nombre_tool = serialized.get("name", "desconocida")
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"\n{'='*60}")
        print(f"[TRACE {timestamp}] HERRAMIENTA INVOCADA: {nombre_tool}")
        print(f"{'='*60}")
        print(f"[INPUT] {input_str}")
        self.historial.append({
            "evento": "tool_start",
            "tool": nombre_tool,
            "input": input_str,
            "timestamp": timestamp
        })

    def on_tool_end(self, output, **kwargs):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[OUTPUT {timestamp}]")
        print(f"{str(output)[:500]}")
        print(f"{'='*60}\n")
        self.historial.append({
            "evento": "tool_end",
            "output": str(output)[:500],
            "timestamp": timestamp
        })

    def on_tool_error(self, error, **kwargs):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[ERROR {timestamp}] {error}")
        self.historial.append({
            "evento": "tool_error",
            "error": str(error),
            "timestamp": timestamp
        })

trace_handler = ToolTracingHandler()

# Configurar API Key de OpenRouter
# Registro: https://openrouter.ai/keys
try:
    from google.colab import userdata
    OPENROUTER_API_KEY = userdata.get("OPENROUTER_API_KEY")
except (ImportError, ValueError):
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY") or getpass.getpass("Ingresa tu OpenRouter API Key: ")

os.environ["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY

llm = ChatOpenAI(
    model="nvidia/nemotron-3-ultra-550b-a55b:free",
    openai_api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://colab.research.google.com",
        "X-Title": "Sistema Ventas Computadoras"
    },
    temperature=0,
    max_retries=5,
    request_timeout=120
)

# ============================================================
# CELDA 6: TOOL 1 - CONSULTAR CATALOGO (@tool decorator)
# ============================================================

@tool
def consultar_catalogo(query: str) -> str:
    """Consultar el catálogo de productos disponibles. Busca productos por nombre, categoría o marca. Input: nombre del producto, categoría o marca. Ejemplos: 'laptops', 'mouse logitech', 'monitores', 'tarjeta grafica'"""
    conn_local = sqlite3.connect("ventas_computadoras.db")
    cursor_local = conn_local.cursor()
    query_lower = query.lower().strip()

    if query_lower in ["todos", "todo", "catalogo", "productos"]:
        sql = "SELECT * FROM productos"
        cursor_local.execute(sql)
    else:
        sql = f"""SELECT * FROM productos
                  WHERE LOWER(nombre) LIKE '%{query_lower}%'
                     OR LOWER(categoria) LIKE '%{query_lower}%'
                     OR LOWER(marca) LIKE '%{query_lower}%'"""
        cursor_local.execute(sql)

    filas = cursor_local.fetchall()
    columnas = [desc[0] for desc in cursor_local.description]
    conn_local.close()

    if not filas:
        return f"No se encontraron productos para: {query}"

    df = pd.DataFrame(filas, columns=columnas)
    return df.to_string(index=False)

# ============================================================
# CELDA 7: TOOL 2 - CONSULTAR VENTAS (@tool decorator)
# ============================================================

@tool
def consultar_ventas(query: str) -> str:
    """Consultar el historial de ventas del sistema. Busca ventas por nombre de cliente, número de venta o lista las recientes. Input: nombre del cliente, número de venta o 'recientes'. Ejemplos: 'ventas de Carlos Lopez', 'venta #5', 'ventas recientes'"""
    conn_local = sqlite3.connect("ventas_computadoras.db")
    cursor_local = conn_local.cursor()
    query_lower = query.lower().strip()

    nombres_conocidos = ["carlos", "maria", "juan", "ana", "luis", "sofia",
        "pedro", "elena", "diego", "laura", "andres", "valeria",
        "fernando", "gabriela", "ricardo", "isabel", "jorge",
        "patricia", "alberto", "monica"]

    if any(nombre in query_lower for nombre in nombres_conocidos):
        palabras = query_lower.split()
        stopwords = {"ventas", "de", "del", "la", "las", "cliente",
                     "clientes", "mostrar", "consulta", "por", "para",
                     "y", "a", "el", "lo", "que"}
        nombre_busqueda = " ".join(
            p for p in palabras if p not in stopwords
        )
        sql = f"""SELECT v.id, c.nombre as cliente, v.fecha, v.total
                  FROM ventas v
                  JOIN clientes c ON v.cliente_id = c.id
                  WHERE LOWER(c.nombre) LIKE '%{nombre_busqueda}%'
                  ORDER BY v.fecha DESC"""
    else:
        nums = re.findall(r'\d+', query)
        if nums:
            sql = f"""SELECT v.id, c.nombre as cliente, v.fecha, v.total
                      FROM ventas v
                      JOIN clientes c ON v.cliente_id = c.id
                      WHERE v.id = {nums[0]}"""
        else:
            sql = """SELECT v.id, c.nombre as cliente, v.fecha, v.total
                     FROM ventas v
                     JOIN clientes c ON v.cliente_id = c.id
                     ORDER BY v.fecha DESC LIMIT 10"""

    cursor_local.execute(sql)
    filas = cursor_local.fetchall()
    columnas = [desc[0] for desc in cursor_local.description]
    conn_local.close()

    if not filas:
        return f"No se encontraron ventas para: {query}"

    df = pd.DataFrame(filas, columns=columnas)
    return df.to_string(index=False)

# ============================================================
# CELDA 8: TOOL 3 - CONSULTAR ESTADISTICAS (@tool decorator)
# ============================================================

@tool
def consultar_estadisticas(query: str) -> str:
    """Consultar estadísticas y métricas del negocio. Obtiene top productos, ingresos, ventas por categoría, clientes frecuentes. Input: tipo de estadística deseada. Ejemplos: 'top 5 productos mas vendidos', 'ingresos totales', 'ventas por categoria', 'clientes frecuentes', 'ventas por marca'"""
    conn_local = sqlite3.connect("ventas_computadoras.db")
    cursor_local = conn_local.cursor()
    query_lower = query.lower().strip()

    if "top" in query_lower or "mas vendido" in query_lower:
        nums = re.findall(r'\d+', query)
        limite = nums[0] if nums else 10
        sql = f"""SELECT p.nombre, p.categoria,
                         SUM(dv.cantidad) as total_vendido,
                         SUM(dv.cantidad * dv.precio_unitario) as ingreso_total
                  FROM detalle_ventas dv
                  JOIN productos p ON dv.producto_id = p.id
                  GROUP BY p.id
                  ORDER BY total_vendido DESC
                  LIMIT {limite}"""
    elif "ingreso" in query_lower or "ingresos" in query_lower:
        sql = """SELECT SUM(total) as ingresos_totales,
                        COUNT(*) as total_ventas,
                        ROUND(AVG(total), 2) as promedio_venta,
                        MAX(total) as venta_maxima
                 FROM ventas"""
    elif "categoria" in query_lower:
        sql = """SELECT p.categoria,
                        COUNT(DISTINCT v.id) as ventas,
                        SUM(dv.cantidad) as unidades_vendidas,
                        SUM(dv.cantidad * dv.precio_unitario) as ingreso
                 FROM detalle_ventas dv
                 JOIN productos p ON dv.producto_id = p.id
                 JOIN ventas v ON dv.venta_id = v.id
                 GROUP BY p.categoria
                 ORDER BY ingreso DESC"""
    elif "cliente" in query_lower or "frecuente" in query_lower:
        sql = """SELECT c.nombre,
                        COUNT(v.id) as compras,
                        SUM(v.total) as total_gastado,
                        ROUND(AVG(v.total), 2) as ticket_promedio
                 FROM clientes c
                 JOIN ventas v ON c.id = v.cliente_id
                 GROUP BY c.id
                 ORDER BY total_gastado DESC
                 LIMIT 10"""
    elif "marca" in query_lower:
        sql = """SELECT p.marca,
                        COUNT(DISTINCT v.id) as ventas,
                        SUM(dv.cantidad) as unidades_vendidas,
                        SUM(dv.cantidad * dv.precio_unitario) as ingreso
                 FROM detalle_ventas dv
                 JOIN productos p ON dv.producto_id = p.id
                 JOIN ventas v ON dv.venta_id = v.id
                 GROUP BY p.marca
                 ORDER BY ingreso DESC"""
    else:
        sql = """SELECT 'Total ingresos' as metrica, SUM(total) as valor FROM ventas
                 UNION ALL
                 SELECT 'Total ventas', COUNT(*) FROM ventas
                 UNION ALL
                 SELECT 'Total productos', COUNT(*) FROM productos
                 UNION ALL
                 SELECT 'Total clientes', COUNT(*) FROM clientes"""

    cursor_local.execute(sql)
    filas = cursor_local.fetchall()
    columnas = [desc[0] for desc in cursor_local.description]
    conn_local.close()

    if not filas:
        return f"No se encontraron estadisticas para: {query}"

    df = pd.DataFrame(filas, columns=columnas)
    return df.to_string(index=False)

# ============================================================
# CELDA 9: CREAR PROMPT Y AGENTE LANGCHAIN
# ============================================================

tools = [consultar_catalogo, consultar_ventas, consultar_estadisticas]

prompt = PromptTemplate.from_template("""Eres un asistente experto en ventas de computadoras.

Tienes estas herramientas:
1. consultar_catalogo: busca productos por nombre, categoria o marca
2. consultar_ventas: historial de ventas por cliente o numero de venta
3. consultar_estadisticas: metricas del negocio (top, ingresos, categorias)

Sigue este formato ESTRICTAMENTE:

Thought: lo que piensas hacer
Action: el nombre de la herramienta
Action Input: el parametro de la herramienta
Observation: el resultado de la herramienta
... (repite Thought/Action/Observation si necesitas mas pasos)
Thought: ahora se la respuesta final
Final Answer: respuesta en espanol para el usuario

Pregunta: {input}

{agent_scratchpad}""")

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=3,
    early_stopping_method="generate",
    callbacks=[trace_handler]
)

# ============================================================
# CELDA 10: PROBAR EL SISTEMA CON RETRY POR RATE LIMIT
# ============================================================

def invoke_with_retry(agent, pregunta, max_retries=5, base_delay=3):
    for intento in range(1, max_retries + 1):
        try:
            return agent.invoke({"input": pregunta})
        except Exception as e:
            error_str = str(e).lower()
            if "resourcelimit" in error_str or "resource_exhausted" in error_str or "429" in error_str or "rate limit" in error_str:
                delay = base_delay * (2 ** (intento - 1))
                print(f"  [RETRY {intento}/{max_retries}] Rate limit alcanzado, esperando {delay}s...")
                time.sleep(delay)
            else:
                print(f"  [ERROR] {e}")
                return None
    print(f"  [SKIP] Se agotaron los reintentos para: {pregunta}")
    return None

preguntas = [
    "Que laptops tienen en stock?",
    "Cual es el ingreso total de ventas?",
    "Quien es el cliente que mas ha comprado?",
]

for i, pregunta in enumerate(preguntas):
    if i > 0:
        print(f"\n  Esperando 3s antes de la siguiente consulta para evitar rate limit...")
        time.sleep(3)
    print(f"\n{'#'*60}")
    print(f"# PREGUNTA {i+1}/3: {pregunta}")
    print(f"{'#'*60}")
    resultado = invoke_with_retry(agent_executor, pregunta)
    if resultado:
        print(f"\n>>> RESPUESTA: {resultado['output']}")

conn.close()

print("\n" + "="*60)
print(" HISTORIAL COMPLETO DE TRACING ")
print("="*60)
for i, entry in enumerate(trace_handler.historial, 1):
    print(f"{i}. [{entry['timestamp']}] {entry['evento'].upper()}: ", end="")
    if entry['evento'] == 'tool_start':
        print(f"Tool={entry['tool']} | Input={entry['input'][:100]}")
    elif entry['evento'] == 'tool_end':
        print(f"Output={entry['output'][:100]}...")
    elif entry['evento'] == 'tool_error':
        print(f"Error={entry['error'][:100]}")

# ============================================================
# CELDA 11: MODO INTERACTIVO (OPCIONAL)
# ============================================================

def modo_interactivo():
    print("\n" + "="*60)
    print(" MODO INTERACTIVO - Sistema de Ventas de Computadoras ")
    print(" Escribe 'salir' para terminar")
    print("="*60)
    conn_local = sqlite3.connect("ventas_computadoras.db")

    while True:
        pregunta = input("\nTu pregunta: ")
        if pregunta.lower() in ["salir", "exit", "quit"]:
            break
        try:
            respuesta = agent_executor.invoke({"input": pregunta})
            print(f"\nRespuesta: {respuesta['output']}")
        except Exception as e:
            print(f"\nError: {e}")

    conn_local.close()
    print("Sistema finalizado.")

# Descomentar para ejecutar el modo interactivo:
# modo_interactivo()
