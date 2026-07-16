"""
Inicializa la base de datos SQLite con datos de ventas de computadoras.
Genera el dataset CSV y lo carga en la base de datos.
Ejecutar UNA SOLA VEZ antes de usar el MCP Agent o Streamlit.

Uso:
    python setup_db.py
"""

import sqlite3
import pandas as pd
import os
import random
from datetime import datetime, timedelta


def setup_database():
    random.seed(42)

    # --- PRODUCTOS ---
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

    # --- CLIENTES ---
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

    # --- VENTAS Y DETALLE ---
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

    # --- GUARDAR CSV ---
    os.makedirs("datos", exist_ok=True)

    df_productos = pd.DataFrame(productos,
        columns=["id", "nombre", "categoria", "marca", "precio", "stock"])
    df_clientes = pd.DataFrame(clientes,
        columns=["id", "nombre", "email", "telefono", "direccion"])
    df_ventas = pd.DataFrame(ventas,
        columns=["id", "cliente_id", "fecha", "total"])
    df_detalle = pd.DataFrame(detalle,
        columns=["id", "venta_id", "producto_id", "cantidad", "precio_unitario"])

    df_productos.to_csv("datos/productos.csv", index=False)
    df_clientes.to_csv("datos/clientes.csv", index=False)
    df_ventas.to_csv("datos/ventas.csv", index=False)
    df_detalle.to_csv("datos/detalle_ventas.csv", index=False)
    print("[OK] CSV guardados en 'datos/'")

    # --- CREAR SQLITE ---
    conn = sqlite3.connect("ventas_computadoras.db")
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY, nombre TEXT NOT NULL,
            categoria TEXT NOT NULL, marca TEXT NOT NULL,
            precio REAL NOT NULL, stock INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY, nombre TEXT NOT NULL,
            email TEXT NOT NULL, telefono TEXT NOT NULL,
            direccion TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY, cliente_id INTEGER NOT NULL,
            fecha TEXT NOT NULL, total REAL NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id INTEGER PRIMARY KEY, venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL, cantidad INTEGER NOT NULL,
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
    conn.close()
    print(f"[OK] Base de datos 'ventas_computadoras.db' creada")
    print(f"     - {len(productos)} productos")
    print(f"     - {len(clientes)} clientes")
    print(f"     - {len(ventas)} ventas")
    print(f"     - {len(detalle)} detalles")


if __name__ == "__main__":
    setup_database()
