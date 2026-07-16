"""
MCP Agent con Memoria - Sistema de Ventas de Computadoras
=========================================================
Agente con memoria conversacional que orquesta las 3 tools
para consultar el sistema de ventas.
"""

import sqlite3
import pandas as pd
import os
import json
import re
import getpass
import time
from datetime import datetime, timedelta
from typing import Optional

try:
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain.prompts import PromptTemplate
    from langchain.callbacks.base import BaseCallbackHandler
except ImportError:
    from langchain_classic.agents import AgentExecutor, create_react_agent
    from langchain_classic.prompts import PromptTemplate
    from langchain_classic.callbacks.base import BaseCallbackHandler

from langchain_openai import ChatOpenAI
from langchain.tools import tool


# ============================================================
# TRACING
# ============================================================

class ToolTracingHandler(BaseCallbackHandler):
    def __init__(self):
        self.historial = []

    def on_tool_start(self, serialized, input_str, **kwargs):
        nombre_tool = serialized.get("name", "desconocida")
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"\n{'='*60}")
        print(f"[TRACE {timestamp}] TOOL INVOCADA: {nombre_tool}")
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


# ============================================================
# TOOLS
# ============================================================

@tool
def consultar_catalogo(query: str) -> str:
    """Consultar el catalogo de productos disponibles. Busca productos por nombre, categoria o marca. Input: nombre del producto, categoria o marca. Ejemplos: 'laptops', 'mouse logitech', 'monitores', 'tarjeta grafica'"""
    conn_local = sqlite3.connect("ventas_computadoras.db")
    cursor_local = conn_local.cursor()
    query_lower = query.lower().strip()

    if query_lower in ["todos", "todo", "catalogo", "productos"]:
        sql = "SELECT * FROM productos"
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


@tool
def consultar_ventas(query: str) -> str:
    """Consultar el historial de ventas del sistema. Busca ventas por nombre de cliente, numero de venta o lista las recientes. Input: nombre del cliente, numero de venta o 'recientes'. Ejemplos: 'ventas de Carlos Lopez', 'venta #5', 'ventas recientes'"""
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
        nombre_busqueda = " ".join(p for p in palabras if p not in stopwords)
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


@tool
def consultar_estadisticas(query: str) -> str:
    """Consultar estadisticas y metricas del negocio. Obtiene top productos, ingresos, ventas por categoria, clientes frecuentes. Input: tipo de estadistica deseada. Ejemplos: 'top 5 productos mas vendidos', 'ingresos totales', 'ventas por categoria', 'clientes frecuentes', 'ventas por marca'"""
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
# MCP AGENT
# ============================================================

class MCPAgent:
    """
    Agente MCP con memoria conversacional.
    Orquesta las 3 tools y recuerda el historial de la conversacion.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "nvidia/nemotron-3-ultra-550b-a55b:free",
        temperature: float = 0,
        memory_window: int = 6,
        verbose: bool = False,
        max_iterations: int = 8
    ):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY") or getpass.getpass("OpenRouter API Key: ")
        os.environ["OPENROUTER_API_KEY"] = self.api_key

        self.llm = ChatOpenAI(
            model=model,
            openai_api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/mcp-ventas",
                "X-Title": "MCP Ventas Computadoras"
            },
            temperature=temperature,
            max_retries=5,
            request_timeout=120
        )

        self.trace_handler = ToolTracingHandler()
        self.chat_history = []
        self.memory_window = memory_window

        self.tools = [consultar_catalogo, consultar_ventas, consultar_estadisticas]

        self.prompt_str = """Eres un asistente experto en ventas de computadoras.

Tienes estas herramientas disponibles:
{tools}

Nombres de las herramientas: {tool_names}

Historial de la conversacion:
{chat_history}

Instrucciones:
1. Usa UNA SOLA herramienta por vez para responder
2. Apenas tengas los datos, da la respuesta final
3. NO repitas herramientas si ya tienes la informacion

Formato:

Thought: lo que piensas hacer
Action: el nombre de la herramienta
Action Input: el parametro de la herramienta
Observation: el resultado de la herramienta
Thought: ahora se la respuesta final
Final Answer: respuesta en espanol para el usuario

Pregunta: {input}

{agent_scratchpad}"""

        self.prompt = PromptTemplate(
            template=self.prompt_str,
            input_variables=["agent_scratchpad", "chat_history", "input", "tool_names", "tools"]
        )

        agent = create_react_agent(self.llm, self.tools, self.prompt)

        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=verbose,
            handle_parsing_errors=True,
            max_iterations=max_iterations,
            callbacks=[self.trace_handler] if verbose else None
        )

    def ask(self, query: str, retries: int = 3) -> str:
        """Envia una pregunta al agente y retorna la respuesta."""
        historial = self._formatear_historial()
        kwargs = {
            "input": query,
            "chat_history": historial
        }

        for intento in range(1, retries + 1):
            try:
                resultado = self.executor.invoke(kwargs)
                respuesta = resultado["output"]
                self.chat_history.append({"role": "user", "content": query})
                self.chat_history.append({"role": "assistant", "content": respuesta})
                if len(self.chat_history) > self.memory_window * 2:
                    self.chat_history = self.chat_history[-(self.memory_window * 2):]
                return respuesta
            except Exception as e:
                error_str = str(e).lower()
                print(f"  [ERROR {intento}/{retries}] {e}")
                if any(x in error_str for x in ["resourcelimit", "resource_exhausted", "429", "rate limit",
                                                  "unavailable", "too many", "quota", "timeout", "deadline"]):
                    delay = 3 * (2 ** (intento - 1))
                    print(f"  [RETRY {intento}/{retries}] Reintentando en {delay}s...")
                    time.sleep(delay)
                elif intento < retries:
                    print(f"  [RETRY {intento}/{retries}] Reintentando...")
                    time.sleep(2)
                else:
                    return f"Error: {e}"

        return "Error: No se pudo obtener respuesta."

    def _formatear_historial(self) -> str:
        if not self.chat_history:
            return "No hay conversacion previa."
        partes = []
        for msg in self.chat_history[-self.memory_window * 2:]:
            rol = "Usuario" if msg["role"] == "user" else "Asistente"
            partes.append(f"{rol}: {msg['content'][:200]}")
        return "\n".join(partes)

    def clear_memory(self):
        """Limpia la memoria conversacional."""
        self.chat_history.clear()
        self.trace_handler.historial.clear()

    def get_conversation_summary(self) -> str:
        """Retorna el resumen de la conversacion actual."""
        return self._formatear_historial()

    def get_trace_history(self) -> list:
        """Retorna el historial de tracing de herramientas."""
        return self.trace_handler.historial


# ============================================================
# PUNTO DE ENTRADA (linea de comandos)
# ============================================================

def main():
    print("=" * 60)
    print(" MCP AGENT - Sistema de Ventas de Computadoras ")
    print("=" * 60)
    print("Cargando agente con memoria...")

    agent = MCPAgent(verbose=True)

    print("\nAgente listo. Escribe 'salir' para terminar, 'memoria' para ver historial.\n")

    while True:
        try:
            query = input("\n>>> Tu pregunta: ").strip()
            if query.lower() in ["salir", "exit", "quit"]:
                break
            if query.lower() == "memoria":
                print("\n--- HISTORIAL DE CONVERSACION ---")
                print(agent.get_conversation_summary())
                continue
            if query.lower() == "trazas":
                print("\n--- TRAZAS DE HERRAMIENTAS ---")
                for t in agent.get_trace_history():
                    print(f"[{t['timestamp']}] {t['evento']}: {t.get('tool', '')} | {t.get('input', t.get('output', t.get('error', '')))[:100]}")
                continue

            respuesta = agent.ask(query)
            print(f"\nRespuesta: {respuesta}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")

    print("\nSistema finalizado.")


if __name__ == "__main__":
    main()
