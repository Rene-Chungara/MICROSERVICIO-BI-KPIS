"""
Script para probar conexión a PostgreSQL en diferentes puertos
"""
import psycopg2

print("="*60)
print("PROBANDO CONEXIÓN A POSTGRESQL EN DIFERENTES PUERTOS")
print("="*60)

DB_NAME = "historialclinico"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

# Puertos comunes de PostgreSQL
puertos = [5432, 5433, 5434, 5435]

for puerto in puertos:
    print(f"\n🔍 Probando puerto {puerto}...")
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=puerto,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=3
        )
        print(f"   ✅ CONEXIÓN EXITOSA en puerto {puerto}")
        
        # Verificar versión
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"   {version.split(',')[0]}")
        
        # Verificar si tiene datos
        try:
            cur.execute("SELECT COUNT(*) FROM cita")
            citas = cur.fetchone()[0]
            print(f"   Citas en BD: {citas}")
        except:
            print(f"   Tabla 'cita' no existe")
        
        cur.close()
        conn.close()
        
        print(f"\n✨ PUERTO CORRECTO: {puerto}")
        print(f"   Actualiza db.py con: DB_PORT = \"{puerto}\"")
        break
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if "no existe" in error_msg or "does not exist" in error_msg:
            print(f"   Puerto {puerto} activo pero BD 'historialclinico' no existe")
            print(f"   Crear BD: CREATE DATABASE historialclinico;")
        elif "timeout" in error_msg or "refused" in error_msg:
            print(f"   Puerto {puerto} no responde")
        else:
            print(f"   Error: {error_msg[:100]}")
    except Exception as e:
        print(f"   Error inesperado: {e}")

print(f"\n{'='*60}")
print("PRUEBA COMPLETADA")
print(f"{'='*60}\n")
