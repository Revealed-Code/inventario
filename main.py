import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno (útil para desarrollo local)
load_dotenv()

# Inicializar FastAPI
app = FastAPI(
    title="Centro de Acopio API",
    description="Backend para el Control de Inventario Permanente integrado con Supabase",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde tu frontend en Render o local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción puedes especificar el dominio exacto de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURACIÓN DE SUPABASE ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Faltan las variables de entorno SUPABASE_URL o SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- MODELOS DE DATOS (PYDANTIC) ---
class ProductoSchema(BaseModel):
    codigo: str
    nombre: str
    presentacion: str | None = None
    categoria: str

class MovimientoSchema(BaseModel):
    fecha: str
    codigo: str
    cantidad: int
    persona_contacto: str | None = None
    responsable: str | None = None


# --- ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "online", "message": "API de Centro de Acopio activa y funcionando"}


# 1. OBTENER INVENTARIO CONSOLIDADO
@app.get("/api/inventario")
def obtener_inventario():
    try:
        # Consulta la vista consolidada o tabla que calcula el stock en Supabase
        response = supabase.table("inventario").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar inventario: {str(e)}")


# 2. OBTENER CATÁLOGO DE PRODUCTOS
@app.get("/api/productos")
def obtener_productos():
    try:
        response = supabase.table("productos").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar productos: {str(e)}")


# 3. REGISTRAR UN NUEVO PRODUCTO (Mantenimiento / Admin)
@app.post("/api/productos")
def crear_producto(producto: ProductoSchema):
    try:
        data = {
            "codigo": producto.codigo.upper(),
            "nombre": producto.nombre,
            "presentacion": producto.presentacion,
            "categoria": producto.categoria.upper()
        }
        response = supabase.table("productos").insert(data).execute()
        return {"message": "Producto creado con éxito", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al crear producto: {str(e)}")


# 4. REGISTRAR ENTRADA
@app.post("/api/entradas")
def registrar_entrada(movimiento: MovimientoSchema):
    try:
        data = {
            "fecha": movimiento.fecha,
            "codigo": movimiento.codigo.upper(),
            "cantidad": movimiento.cantidad,
            "persona_contacto": movimiento.persona_contacto or "ANÓNIMO",
            "responsable": movimiento.responsable or "SISTEMA"
        }
        response = supabase.table("entradas").insert(data).execute()
        return {"message": "Entrada registrada correctamente", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al registrar entrada: {str(e)}")


# 5. REGISTRAR SALIDA
@app.post("/api/salidas")
def registrar_salida(movimiento: MovimientoSchema):
    try:
        # Nota: La validación de stock físico disponible ya la hace el Frontend,
        # pero es una buena práctica validarla también aquí en el backend si es necesario.
        data = {
            "fecha": movimiento.fecha,
            "codigo": movimiento.codigo.upper(),
            "cantidad": movimiento.cantidad,
            "persona_contacto": movimiento.persona_contacto or "ANÓNIMO",
            "responsable": movimiento.responsable or "SISTEMA"
        }
        response = supabase.table("salidas").insert(data).execute()
        return {"message": "Salida registrada correctamente", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al registrar salida: {str(e)}")


# 6. OBTENER ENTRADAS INDIVIDUALES
@app.get("/api/entradas")
def obtener_entradas():
    try:
        response = supabase.table("entradas").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener entradas: {str(e)}")


# 7. OBTENER SALIDAS INDIVIDUALES
@app.get("/api/salidas")
def obtener_salidas():
    try:
        response = supabase.table("salidas").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener salidas: {str(e)}")


# =========================================================================
# 8. NUEVO ENDPOINT CONSOLIDADO PARA HISTORIAL (Resuelve el Error 404)
# =========================================================================
@app.get("/api/movimientos")
def obtener_movimientos():
    try:
        # Obtener entradas y salidas en paralelo
        entradas_res = supabase.table("entradas").select("*").execute()
        salidas_res = supabase.table("salidas").select("*").execute()
        
        entradas = entradas_res.data if hasattr(entradas_res, 'data') else entradas_res
        salidas = salidas_res.data if hasattr(salidas_res, 'data') else salidas_res
        
        # Etiquetar cada fila para que el frontend distinga la operación
        for e in entradas:
            e["tipo"] = "ENTRADA"
        for s in salidas:
            s["tipo"] = "SALIDA"
            
        # Combinar registros
        todos_los_movimientos = entradas + salidas
        
        # Opcional: Intentar ordenar por un campo id o fecha secuencial si existen
        # En Supabase, si tienes la columna 'created_at' o un 'id' autoincremental:
        todos_los_movimientos.sort(key=lambda x: x.get("id", 0))
        
        return todos_los_movimientos
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al compilar el historial unificado: {str(e)}"
        )
