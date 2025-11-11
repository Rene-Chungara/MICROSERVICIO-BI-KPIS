"""
Script para diagnosticar problemas de conexión a PostgreSQL
"""
import psycopg2
from sqlalchemy import create_engine, text

print("="*60)
print("DIAGNÓSTICO DE CONEXIÓN A POSTGRESQL")
print("="*60)

# Configuración (misma que Backend Java)
DB_HOST = "localhost"
DB_PORT = "5433"  # Backend Java usa 5433
DB_NAME = "historialclinico"
DB_USER = "postgres"
DB_PASSWORD = "password"  # Backend Java usa "password"

print(f"\n📋 Configuración:")
print(f"   Host: {DB_HOST}")
print(f"   Puerto: {DB_PORT}")
print(f"   Base de datos: {DB_NAME}")
print(f"   Usuario: {DB_USER}")
print(f"   Contraseña: {'*' * len(DB_PASSWORD)}")

# Test 1: Conexión directa con psycopg2
print(f"\n{'='*60}")
print("TEST 1: Conexión directa con psycopg2")
print(f"{'='*60}")
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    print("✅ Conexión exitosa con psycopg2")
    
    # Verificar versión de PostgreSQL
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()[0]
    print(f"   PostgreSQL: {version.split(',')[0]}")
    
    cur.close()
    conn.close()
except psycopg2.OperationalError as e:
    print(f"❌ Error de conexión con psycopg2:")
    print(f"   {str(e)}")
    print("\n💡 Posibles causas:")
    print("   1. PostgreSQL no está corriendo")
    print("   2. La base de datos 'historialclinico' no existe")
    print("   3. Usuario/contraseña incorrectos")
    print("   4. PostgreSQL no acepta conexiones en localhost:5432")
    print("\n🔧 Soluciones:")
    print("   - Verificar servicio: Get-Service -Name postgresql*")
    print("   - Iniciar servicio: Start-Service postgresql-x64-XX")
    print("   - Crear BD: CREATE DATABASE historialclinico;")
except Exception as e:
    print(f"❌ Error inesperado: {e}")

# Test 2: Conexión con SQLAlchemy
print(f"\n{'='*60}")
print("TEST 2: Conexión con SQLAlchemy")
print(f"{'='*60}")
try:
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Conexión exitosa con SQLAlchemy")
        
        # Verificar tablas existentes
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        tables = [row[0] for row in result]
        
        if tables:
            print(f"\n📊 Tablas encontradas ({len(tables)}):")
            for table in tables:
                print(f"   - {table}")
        else:
            print("\n⚠️  No se encontraron tablas en la base de datos")
            print("   Ejecuta el Backend Java para crear las tablas")
        
except Exception as e:
    print(f"❌ Error con SQLAlchemy: {e}")

# Test 3: Verificar datos de prueba
print(f"\n{'='*60}")
print("TEST 3: Verificar datos en tablas clave")
print(f"{'='*60}")
try:
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    
    with engine.connect() as conn:
        # Verificar citas
        result = conn.execute(text("SELECT COUNT(*) FROM cita"))
        citas_count = result.fetchone()[0]
        print(f"   Citas: {citas_count}")
        
        # Verificar especialidades
        result = conn.execute(text("SELECT COUNT(*) FROM especialidad"))
        esp_count = result.fetchone()[0]
        print(f"   Especialidades: {esp_count}")
        
        # Verificar horarios
        result = conn.execute(text("SELECT COUNT(*) FROM horarios"))
        hor_count = result.fetchone()[0]
        print(f"   Horarios: {hor_count}")
        
        # Verificar usuarios
        result = conn.execute(text("SELECT COUNT(*) FROM usuarios"))
        usr_count = result.fetchone()[0]
        print(f"   Usuarios: {usr_count}")
        
        if citas_count == 0:
            print("\n⚠️  No hay datos de citas en la base de datos")
            print("   Los gráficos estarán vacíos")
            print("   Agrega datos de prueba desde el Frontend")
        else:
            print(f"\n✅ Base de datos tiene {citas_count} citas para visualizar")
        
except Exception as e:
    print(f"❌ Error al verificar datos: {e}")

print(f"\n{'='*60}")
print("DIAGNÓSTICO COMPLETADO")
print(f"{'='*60}\n")
