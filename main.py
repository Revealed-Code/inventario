# main.py
import os
import sqlite3
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, field_validator

app = FastAPI(title="Centro de Acopio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Guardamos la base de datos en un volumen persistente de Railway o localmente
DATABASE = "/data/inventario.db" if os.path.exists("/data") else "inventario.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# --- DATOS DE INICIALIZACIÓN AUTOMÁTICA (TU EXCEL) ---
PRODUCTOS_INICIALES = [
    {"codigo": "MED-001", "nombre": "Solución", "presentacion": "unidades", "categoria": "MEDICAMENTOS"},
    {"codigo": "IME-001", "nombre": "Sondas", "presentacion": "unidades", "categoria": "INSUMOS MEDICOS"},
    {"codigo": "MED-002", "nombre": "Diclofenac potásico", "presentacion": "cajas", "categoria": "MEDICAMENTOS"},
    {"codigo": "IME-002", "nombre": "Bombas de anestesia", "presentacion": "unidades", "categoria": "INSUMOS MEDICOS"},
    {"codigo": "MED-003", "nombre": "Yodo", "presentacion": "unidades", "categoria": "MEDICAMENTOS"},
    {"codigo": "IME-003", "nombre": "Algodón, motas", "presentacion": "bolsas ", "categoria": "INSUMOS MEDICOS"},
    {"codigo": "IME-004", "nombre": "Buretas", "presentacion": "unidades", "categoria": "INSUMOS MEDICOS"},
    {"codigo": "IME-005", "nombre": "Catéter", "presentacion": "24 g", "categoria": "INSUMOS MEDICOS"},
    {"codigo": "IME-006", "nombre": "Catéter", "presentacion": "20 g", "categoria": "INSUMOS MEDICOS"},
    {"codigo": "IME-007", "nombre": "Catéter", "presentacion": "22 g", "categoria": "INSUMOS MEDICOS"},
    {"codigo": "IME-008", "nombre": "Catéter", "presentacion": "18 g", "categoria": "INSUMOS MEDICOS"},
    {"codigo": "IME-009", "nombre": "Jeringas", "presentacion": "10 ml", "categoria": "INSUMOS MEDICOS"},
    {"codigo": "IME-010", "nombre": "Jeringas", "presentacion": "20 ml", "categoria": "INSUMOS MEDICOS"},
    {"codigo": "IME-011", "nombre": "Gasas", "presentacion": "unidades", "categoria": "INSUMOS MEDICOS"},
    {"codigo": "MED-004", "nombre": "Alcohol ", "presentacion": "100 cm3", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-005", "nombre": "Alcohol ", "presentacion": "120 cm3", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-006", "nombre": "Alcohol ", "presentacion": "240 cm3", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-007", "nombre": "Alcohol ", "presentacion": "500 cm3", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-008", "nombre": "Agua oxigenada", "presentacion": "500 cm3", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-009", "nombre": "Agua oxigenada", "presentacion": "1000 cm3", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-010", "nombre": "Agua oxigenada", "presentacion": "galón", "categoria": "MEDICAMENTOS"},
    {"codigo": "IME-012", "nombre": "Adhesivo", "presentacion": "unidades", "categoria": "INSUMOS MEDICOS"},
    {"codigo": "MED-011", "nombre": "Acetaminofen pediátrico", "presentacion": "unidades", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-012", "nombre": "Acetaminofen", "presentacion": "unidades", "categoria": "MEDICAMENTOS"},
    {"codigo": "IME-013", "nombre": "Tapabocas gris", "presentacion": "unidades", "categoria": "INSUMOS MEDICOS"},
    {"codigo": "IME-014", "nombre": "Tapabocas blanco", "presentacion": "unidades", "categoria": "INSUMOS MEDICOS"},
    {"codigo": "MED-014", "nombre": "Metformina", "presentacion": "Cajas 500 mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-015", "nombre": "Diclofenac sódico", "presentacion": "Caja 50 mg ", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-016", "nombre": "Loratadina", "presentacion": "Caja 10 mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-017", "nombre": "Olmesartán Medoxomil", "presentacion": "Caja 20 mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-018", "nombre": "Bisoprolol Fumarato", "presentacion": "Caja, 5 mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-019", "nombre": "Imazol", "presentacion": "Caja, 100 mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-020", "nombre": "Candesartan", "presentacion": "Caja, 16 mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-021", "nombre": "Lodestar HCT", "presentacion": "Caja 50 mg ", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-022", "nombre": "Amlodipina", "presentacion": "Caja 5mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED.023", "nombre": "Febronol", "presentacion": "Caja Supositorios", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED 024", "nombre": "Clorfenamina", "presentacion": "Caja 4 mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "HIG-012", "nombre": "Repelente insectos", "presentacion": "Envase roll on", "categoria": "HIGIENE PERSONAL"},
    {"codigo": "MED-025", "nombre": "Romprazol", "presentacion": "10 mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "ALI-001", "nombre": "Harina de maiz", "presentacion": "1 k", "categoria": "ALIMENTOS"},
    {"codigo": "ALI-002", "nombre": "Pasta", "presentacion": "1 k", "categoria": "ALIMENTOS"},
    {"codigo": "ALI-003", "nombre": "Arroz", "presentacion": "1 k", "categoria": "ALIMENTOS"},
    {"codigo": "ALI-004", "nombre": "Avena en hojuelas", "presentacion": "800 g", "categoria": "ALIMENTOS"},
    {"codigo": "ALI-005", "nombre": "Atún", "presentacion": "Lata 170 g", "categoria": "ALIMENTOS"},
    {"codigo": "ALI-006", "nombre": "Sardinas", "presentacion": "Lata 170 gr", "categoria": "ALIMENTOS"},
    {"codigo": "ALI-007", "nombre": "Leche líquida", "presentacion": "1 l", "categoria": "ALIMENTOS"},
    {"codigo": "BEB-001", "nombre": "Bebida refrescante", "presentacion": "400 ML", "categoria": "BEBIDAS"},
    {"codigo": "ALI-008", "nombre": "Compotas", "presentacion": "186 gr", "categoria": "ALIMENTOS"},
    {"codigo": "ALI-009", "nombre": "Galletas dulces (tipo oreo)", "presentacion": "paquete", "categoria": "ALIMENTOS"},
    {"codigo": "REC-001", "nombre": "Combo para colorear", "presentacion": "paquete pequeño", "categoria": "RECREACIÓN"},
    {"codigo": "ALI-010", "nombre": "Aceite vegetal", "presentacion": "1 l", "categoria": "ALIMENTOS"},
    {"codigo": "HIG-001", "nombre": "Crema dental", "presentacion": "unidad 100g", "categoria": "HIGIENE PERSONAL"},
    {"codigo": "ALI-011", "nombre": "Azúcar", "presentacion": "1 k", "categoria": "ALIMENTOS"},
    {"codigo": "BEB-002", "nombre": "Jugo de naranja", "presentacion": "1 l", "categoria": "BEBIDAS"},
    {"codigo": "BEB-003", "nombre": "Agua mineral", "presentacion": "5 l", "categoria": "BEBIDAS"},
    {"codigo": "HIG-002", "nombre": "Jabón de tocador", "presentacion": "unidad 80g", "categoria": "HIGIENE PERSONAL"},
    {"codigo": "HIG-003", "nombre": "Champú", "presentacion": "envase 400ml", "categoria": "HIGIENE PERSONAL"},
    {"codigo": "HIG-004", "nombre": "Desodorante", "presentacion": "unidad roll-on", "categoria": "HIGIENE PERSONAL"},
    {"codigo": "HIG-005", "nombre": "Toallas sanitarias", "presentacion": "paquete 8 unid", "categoria": "HIGIENE PERSONAL"},
    {"codigo": "HIG-006", "nombre": "Cepillo de dientes", "presentacion": "unidad", "categoria": "HIGIENE PERSONAL"},
    {"codigo": "HIG-007", "nombre": "Crema de afeitar", "presentacion": "tubo 150g", "categoria": "HIGIENE PERSONAL"},
    {"codigo": "HIG-008", "nombre": "Papel Higiénico", "presentacion": "paquetes 4 unid", "categoria": "HIGIENE PERSONAL"},
    {"codigo": "HIG-009", "nombre": "Pañales niños talla G", "presentacion": "unidades", "categoria": "HIGIENE PERSONAL"},
    {"codigo": "HIG-010", "nombre": "Pañales niños talla M", "presentacion": "unidades", "categoria": "HIGIENE PERSONAL"},
    {"codigo": "HIG-011", "nombre": "Pañales niños talla XG", "presentacion": "unidades", "categoria": "HIGIENE PERSONAL"},
    {"codigo": "ANI-001", "nombre": "Comida perros adultos, perrarina", "presentacion": "paquete 10 k", "categoria": "ANIMALES"},
    {"codigo": "ALI-012", "nombre": "Café en polvo", "presentacion": "500 g", "categoria": "ALIMENTOS"},
    {"codigo": "ALI-013", "nombre": "Margarina", "presentacion": "250 g", "categoria": "ALIMENTOS"},
    {"codigo": "UTE-001", "nombre": "Potes chinos vacíos con tapa", "presentacion": "200 g", "categoria": "UTENSILIOS"},
    {"codigo": "UTE-002", "nombre": "Cucharas plásticas", "presentacion": "unidades", "categoria": "UTENSILIOS"},
    {"codigo": "MED-013", "nombre": "Metformina", "presentacion": "Cajas 500 mg", "categoria": "MEDICAMENTOS"}
]

# Inicializar y autopoblar la base de datos si está vacía
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        codigo TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        presentacion TEXT,
        categoria TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS entradas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        codigo TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        donante TEXT,
        registrado_por TEXT,
        FOREIGN KEY (codigo) REFERENCES productos(codigo)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS salidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        codigo TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        destinatario TEXT,
        autorizado_por TEXT,
        FOREIGN KEY (codigo) REFERENCES productos(codigo)
    )
    """)
    
    # Comprobar si ya hay productos registrados
    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        for prod in PRODUCTOS_INICIALES:
            cursor.execute(
                "INSERT INTO productos (codigo, nombre, presentacion, categoria) VALUES (?, ?, ?, ?)",
                (prod["codigo"], prod["nombre"], prod["presentacion"], prod["categoria"].upper())
            )
        conn.commit()
    conn.close()

init_db()

# --- MODELOS DE DATOS ---
class ProductoBase(BaseModel):
    codigo: str
    nombre: str
    presentacion: str
    categoria: str

    @field_validator('codigo', 'categoria')
    @classmethod
    def to_uppercase(cls, v: str) -> str:
        return v.strip().upper()

class MovimientoBase(BaseModel):
    fecha: str
    codigo: str
    cantidad: int
    persona_contacto: Optional[str] = None
    responsable: Optional[str] = None

    @field_validator('codigo')
    @classmethod
    def code_to_upper(cls, v: str) -> str:
        return v.strip().upper()

# --- ENDPOINTS API ---
@app.get("/", response_class=HTMLResponse)
def leer_interfaz():
    # Lee y sirve el archivo index.html automáticamente al abrir la URL pública
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/productos", response_model=List[ProductoBase])
def listar_productos(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM productos ORDER BY codigo")
    return [dict(row) for row in cursor.fetchall()]

@app.post("/api/productos", response_model=ProductoBase)
def crear_producto(producto: ProductoBase, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO productos (codigo, nombre, presentacion, categoria) VALUES (?, ?, ?, ?)",
            (producto.codigo, producto.nombre, producto.presentacion, producto.categoria)
        )
        db.commit()
        return producto
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="El código de producto ya existe.")

@app.post("/api/entradas")
def registrar_entrada(mov: MovimientoBase, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO entradas (fecha, codigo, cantidad, donante, registrado_por) VALUES (?, ?, ?, ?, ?)",
        (mov.fecha, mov.codigo, mov.cantidad, mov.persona_contacto, mov.responsable)
    )
    db.commit()
    return {"status": "ok"}

@app.post("/api/salidas")
def registrar_salida(mov: MovimientoBase, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    # Calcular existencias reales de ese producto antes de despachar
    cursor.execute("SELECT SUM(cantidad) FROM entradas WHERE codigo = ?", (mov.codigo,))
    total_entradas = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(cantidad) FROM salidas WHERE codigo = ?", (mov.codigo,))
    total_salidas = cursor.fetchone()[0] or 0
    stock_actual = total_entradas - total_salidas

    if mov.cantidad > stock_actual:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente. Disponible: {stock_actual}")

    cursor.execute(
        "INSERT INTO salidas (fecha, codigo, cantidad, destinatario, autorizado_por) VALUES (?, ?, ?, ?, ?)",
        (mov.fecha, mov.codigo, mov.cantidad, mov.persona_contacto, mov.responsable)
    )
    db.commit()
    return {"status": "ok"}

@app.get("/api/inventario")
def obtener_inventario(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
        SELECT 
            p.codigo, p.nombre, p.presentacion, p.categoria,
            COALESCE(e.total_entradas, 0) as total_entradas,
            COALESCE(s.total_salidas, 0) as total_salidas,
            (COALESCE(e.total_entradas, 0) - COALESCE(s.total_salidas, 0)) as stock_disponible
        FROM productos p
        LEFT JOIN (
            SELECT codigo, SUM(cantidad) as total_entradas FROM entradas GROUP BY codigo
        ) e ON p.codigo = e.codigo
        LEFT JOIN (
            SELECT codigo, SUM(cantidad) as total_salidas FROM salidas GROUP BY codigo
        ) s ON p.codigo = s.codigo
        ORDER BY p.codigo
    """)
    return [dict(row) for row in cursor.fetchall()]

@app.get("/api/historial/{codigo}")
def historial_articulo(codigo: str, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    codigo_upper = codigo.strip().upper()
    cursor.execute("SELECT fecha, cantidad, donante as contacto, registrado_por as responsable, 'ENTRADA' as tipo FROM entradas WHERE codigo = ?", (codigo_upper,))
    entradas = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT fecha, cantidad, destinatario as contacto, autorizado_por as responsable, 'SALIDA' as tipo FROM salidas WHERE codigo = ?", (codigo_upper,))
    salidas = [dict(row) for row in cursor.fetchall()]
    
    movimientos = entradas + salidas
    movimientos.sort(key=lambda x: x['fecha'], reverse=True)
    return movimientos