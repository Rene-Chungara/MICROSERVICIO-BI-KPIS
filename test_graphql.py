"""
Script de prueba para verificar todas las queries GraphQL del microservicio BI/KPIs
Ejecutar: python test_graphql.py
"""
import requests
import json

GRAPHQL_URL = "http://localhost:8001/graphql"

def test_query(name, query):
    """Ejecuta una query GraphQL y muestra el resultado"""
    print(f"\n{'='*60}")
    print(f"Probando: {name}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            GRAPHQL_URL,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if "errors" in data:
                print(f"❌ Error en query:")
                print(json.dumps(data["errors"], indent=2))
            else:
                print(f"✅ Éxito:")
                print(json.dumps(data["data"], indent=2))
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Excepción: {e}")

def main():
    print("="*60)
    print("VERIFICACIÓN DE QUERIES GRAPHQL - MICROSERVICIO BI/KPIS")
    print("="*60)
    
    # Health check
    print("\n🔍 Verificando health endpoint...")
    try:
        response = requests.get("http://localhost:8001/health")
        if response.status_code == 200:
            print(f"✅ Health check OK: {response.json()}")
        else:
            print(f"❌ Health check falló: {response.status_code}")
    except Exception as e:
        print(f"❌ No se pudo conectar al microservicio: {e}")
        print("\n⚠️  Asegúrate de que el microservicio esté corriendo:")
        print("   cd MICROSERVICIO-BI-KPIS")
        print("   python run.py")
        return
    
    # Test 1: Citas por especialidad
    test_query(
        "Citas por Especialidad",
        """
        query {
          citasPorEspecialidad {
            especialidad
            total
          }
        }
        """
    )
    
    # Test 2: Serie temporal por semana
    test_query(
        "Serie Temporal - Semana",
        """
        query {
          citasSerie(granularidad: "week") {
            period
            total
          }
        }
        """
    )
    
    # Test 3: Serie temporal por mes
    test_query(
        "Serie Temporal - Mes",
        """
        query {
          citasSerie(granularidad: "month") {
            period
            total
          }
        }
        """
    )
    
    # Test 4: Heatmap de horarios
    test_query(
        "Heatmap de Horarios",
        """
        query {
          heatmapHorarios {
            dow
            hour
            total
          }
        }
        """
    )
    
    # Test 5: Citas por mes
    test_query(
        "Citas por Mes",
        """
        query {
          citasPorMes {
            period
            total
          }
        }
        """
    )
    
    # Test 6: Citas por día
    test_query(
        "Citas por Día",
        """
        query {
          citasPorDia {
            period
            total
          }
        }
        """
    )
    
    # Test 7: KPI de crecimiento de citas
    test_query(
        "KPI Crecimiento de Citas",
        """
        query {
          kpiCrecimientoCitas {
            currentMonth
            previousMonth
            currentTotal
            previousTotal
            growthPercent
          }
        }
        """
    )
    
    # Test 8: KPI de asistencia
    test_query(
        "KPI de Asistencia",
        """
        query {
          kpiAsistencia {
            percent
            attended
            total
          }
        }
        """
    )
    
    # Test 9: Crecimiento de usuarios
    test_query(
        "Crecimiento de Usuarios",
        """
        query {
          usuariosCrecimiento {
            period
            total
          }
        }
        """
    )
    
    print(f"\n{'='*60}")
    print("VERIFICACIÓN COMPLETADA")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
