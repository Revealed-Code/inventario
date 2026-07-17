# main.py
import os
import urllib.parse
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, field_validator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

app = FastAPI(title="Centro de Acopio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURACIÓN DE BASE DE DATOS (POSTGRESQL DESDE VARIABLE DE ENTORNO) ---
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    DATABASE_URL = "sqlite:///./local_inventario.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- DATOS DE INICIALIZACIÓN AUTOMÁTICA ---
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
    {"codigo": "MED-011", "nombre": "Acetaminofén pediátrico", "presentacion": "unidades", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-012", "nombre": "Acetaminofén", "presentacion": "unidades", "categoria": "MEDICAMENTOS"},
    {"codigo": "IME-013", "nombre": "Tapabocas gris", "presentacion": "unidades", "categoria": "INSUMOS MEDICOS"},
    {"codigo": "IME-014", "nombre": "Tapabocas blanco", "presentacion": "unidades", "categoria": "INSUMOS MEDICOS"},
    {"codigo": "MED-014", "nombre": "Metformina", "presentacion": "Cajas 500 mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-015", "nombre": "Diclofenac sódico", "presentacion": "Caja 50 mg ", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-016", "nombre": "Loratadina", "presentacion": "Caja 10 mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-017", "nombre": "Olmesartán Medoxomil", "presentacion": "Caja 20 mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-018", "nombre": "Bisoprolol Fumarato", "presentacion": "Caja, 5 mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-019", "nombre": "Imazol", "presentacion": "Caja, 100 mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-020", "nombre": "Candesartán", "presentacion": "Caja, 16 mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-021", "nombre": "Lodestar HCT", "presentacion": "Caja 50 mg ", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-022", "nombre": "Amlodipina", "presentacion": "Caja 5mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-023", "nombre": "Febronol", "presentacion": "Caja Supositorios", "categoria": "MEDICAMENTOS"},
    {"codigo": "MED-024", "nombre": "Clorfenamina", "presentacion": "Caja 4 mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "HIG-012", "nombre": "Repelente insectos", "presentacion": "Envase roll on", "categoria": "HIGIENE PERSONAL"},
    {"codigo": "MED-025", "nombre": "Romprazol", "presentacion": "10 mg", "categoria": "MEDICAMENTOS"},
    {"codigo": "ALI-001", "nombre": "Harina de maíz", "presentacion": "1 k", "categoria": "ALIMENTOS"},
    {"codigo": "ALI-002", "nombre": "Pasta", "presentacion": "1 k", "categoria": "ALIMENTOS"},
    {"codigo": "ALI-003", "nombre": "Arroz", "presentacion": "1 k", "categoria": "ALIMENTOS"},
    {"codigo": "ALI-004", "nombre": "Avena en hojuelas", "presentacion": "800 g", "categoria": "ALIMENTOS"},
    {"codigo": "ALI-005", "nombre": "Atún", "presentacion": "Lata 170 g", "categoria": "ALIMENTOS"},
    {"codigo": "ALI-006", "nombre": "Sardinas", "presentacion": "Lata 170 gr", "categoria": "ALIMENTOS"},
    {"codigo": "ALI-007", "nombre": "Leche líquida", "presentacion": "1 l", "categoria": "ALIMENTOS"},
    {"codigo": "BEB-001", "nombre": "Bebida refrescante", "presentacion": "400 ML", "categoria": "BEBIDAS"},
    {"codigo": "ALI-008", "nombre": "Compotas", "presentacion": "186 gr", "categoria": "ALIMENTOS"},
    {"codigo": "ALI-009", "nombre": "Galletas dulces (tipo oreo)", "presentacion": "paquete", "categoria": "ALIMENTOS"},
    {"codigo": "REC-001", "nombre": "Combo para colorear", "presentacion": "paquete pequeño", "categoria": "RECREACION"},
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

def init_db():
    is_sqlite = DATABASE_URL.startswith("sqlite")
    serial_type = "INTEGER PRIMARY KEY AUTOINCREMENT" if is_sqlite else "SERIAL PRIMARY KEY"

    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS productos (
            codigo VARCHAR(50) PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            presentacion VARCHAR(100),
            categoria VARCHAR(100) NOT NULL
        )
        """))
        conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS entradas (
            id {serial_type},
            fecha VARCHAR(20) NOT NULL,
            codigo VARCHAR(50) NOT NULL,
            cantidad INTEGER NOT NULL,
            donante VARCHAR(255),
            registrado_por VARCHAR(255)
        )
        """))
        conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS salidas (
            id {serial_type},
            fecha VARCHAR(20) NOT NULL,
            codigo VARCHAR(50) NOT NULL,
            cantidad INTEGER NOT NULL,
            destinatario VARCHAR(255),
            autorizado_por VARCHAR(255)
        )
        """))
        conn.commit()

        result = conn.execute(text("SELECT COUNT(*) FROM productos")).fetchone()
        if result[0] == 0:
            for prod in PRODUCTOS_INICIALES:
                conn.execute(
                    text("INSERT INTO productos (codigo, nombre, presentacion, categoria) VALUES (:codigo, :nombre, :presentacion, :categoria)"),
                    {"codigo": prod["codigo"], "nombre": prod["nombre"], "presentacion": prod["presentacion"], "categoria": prod["categoria"].upper()}
                )
            conn.commit()

init_db()

# --- MODELOS DE VALIDACIÓN ---
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
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/productos")
def listar_productos(db=Depends(get_db)):
    result = db.execute(text("SELECT * FROM productos ORDER BY codigo")).fetchall()
    return [dict(row._mapping) for row in result]

@app.post("/api/productos")
def crear_producto(producto: ProductoBase, db=Depends(get_db)):
    try:
        db.execute(
            text("INSERT INTO productos (codigo, nombre, presentacion, categoria) VALUES (:codigo, :nombre, :presentacion, :categoria)"),
            {"codigo": producto.codigo, "nombre": producto.nombre, "presentacion": producto.presentacion, "categoria": producto.categoria}
        )
        db.commit()
        return producto
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="El código de producto ya existe.")
    
@app.post("/api/entradas")
def registrar_entrada(mov: MovimientoBase, db=Depends(get_db)):
    db.execute(
        text("INSERT INTO entradas (fecha, codigo, cantidad, donante, registrado_por) VALUES (:fecha, :codigo, :cantidad, :donante, :registrado_por)"),
        {"fecha": mov.fecha, "codigo": mov.codigo, "cantidad": mov.cantidad, "donante": mov.persona_contacto, "registrado_por": mov.responsable}
    )
    db.commit()
    return {"status": "ok"}

@app.post("/api/salidas")
def registrar_salida(mov: MovimientoBase, db=Depends(get_db)):
    total_entradas = db.execute(text("SELECT SUM(cantidad) FROM entradas WHERE codigo = :codigo"), {"codigo": mov.codigo}).fetchone()[0] or 0
    total_salidas = db.execute(text("SELECT SUM(cantidad) FROM salidas WHERE codigo = :codigo"), {"codigo": mov.codigo}).fetchone()[0] or 0
    stock_actual = total_entradas - total_salidas

    if mov.cantidad > stock_actual:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente. Disponible: {stock_actual}")

    db.execute(
        text("INSERT INTO salidas (fecha, codigo, cantidad, destinatario, autorizado_por) VALUES (:fecha, :codigo, :cantidad, :destinatario, :autorizado_por)"),
        {"fecha": mov.fecha, "codigo": mov.codigo, "cantidad": mov.cantidad, "destinatario": mov.persona_contacto, "autorizado_por": mov.responsable}
    )
    db.commit()
    return {"status": "ok"}

@app.get("/api/movimientos")
def listar_todos_los_movimientos(db=Depends(get_db)):
    entradas = db.execute(text("""
        SELECT fecha, codigo, cantidad, donante as persona_contacto, registrado_por as responsable, 'ENTRADA' as tipo 
        FROM entradas
    """)).fetchall()
    
    salidas = db.execute(text("""
        SELECT fecha, codigo, cantidad, destinatario as persona_contacto, autorizado_por as responsable, 'SALIDA' as tipo 
        FROM salidas
    """)).fetchall()
    
    todos = [dict(row._mapping) for row in entradas] + [dict(row._mapping) for row in salidas]
    
    try:
        todos.sort(key=lambda x: x['fecha'], reverse=True)
    except Exception:
        pass
        
    return todos

@app.get("/api/inventario")
def obtener_inventario(db=Depends(get_db)):
    query = text("""
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
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]

@app.get("/api/historial/{codigo}")
def historial_articulo(codigo: str, db=Depends(get_db)):
    codigo_upper = codigo.strip().upper()
    entradas = db.execute(text("SELECT fecha, cantidad, donante as contacto, registrado_por as responsable, 'ENTRADA' as tipo FROM entradas WHERE codigo = :codigo"), {"codigo": codigo_upper}).fetchall()
    salidas = db.execute(text("SELECT fecha, cantidad, destinatario as contacto, autorizado_por as responsable, 'SALIDA' as tipo FROM salidas WHERE codigo = :codigo"), {"codigo": codigo_upper}).fetchall()
    
    movimientos = [dict(row._mapping) for row in entradas] + [dict(row._mapping) for row in salidas]
    movimientos.sort(key=lambda x: x['fecha'], reverse=True)
    return movimientos

@app.delete("/api/productos/{codigo}")
def eliminar_producto(codigo: str, db=Depends(get_db)):
    codigo_upper = codigo.strip().upper()
    
    # Comprobar si existe el producto
    producto = db.execute(text("SELECT codigo FROM productos WHERE codigo = :codigo"), {"codigo": codigo_upper}).fetchone()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Comprobar movimientos asociados
    en_entradas = db.execute(text("SELECT COUNT(*) FROM entradas WHERE codigo = :codigo"), {"codigo": codigo_upper}).fetchone()[0]
    en_salidas = db.execute(text("SELECT COUNT(*) FROM salidas WHERE codigo = :codigo"), {"codigo": codigo_upper}).fetchone()[0]
    
    if en_entradas > 0 or en_salidas > 0:
        raise HTTPException(
            status_code=400, 
            detail="No se puede eliminar un producto que ya tiene entradas o salidas registradas."
        )
    
    db.execute(text("DELETE FROM productos WHERE codigo = :codigo"), {"codigo": codigo_upper})
    db.commit()
    return {"message": f"Producto {codigo} eliminado exitosamente"}
