import strawberry
from typing import List, Optional
from sqlalchemy import text
from .db import get_session
from contextlib import contextmanager

@contextmanager
def session_scope():
    gen = get_session()
    session = next(gen)
    try:
        yield session
    finally:
        try:
            next(gen)
        except StopIteration:
            pass

@strawberry.type
class BarEspecialidad:
    especialidad: str
    total: int

@strawberry.type
class SerieCitas:
    period: str
    total: int

@strawberry.type
class HeatmapBin:
    dow: int
    hour: int
    total: int

@strawberry.type
class KpiCrecimiento:
    current_month: str
    previous_month: str
    current_total: int
    previous_total: int
    growth_percent: float

@strawberry.type
class KpiAsistencia:
    percent: float
    attended: int
    total: int

@strawberry.type
class KpiOcupacion:
    percent: float
    ocupados: int
    total: int

@strawberry.type
class KpiCancelacion:
    percent: float
    canceladas: int
    total: int

@strawberry.type
class Query:
    @strawberry.field
    def citas_por_especialidad(self) -> List[BarEspecialidad]:
        sql = text(
            """
            SELECT e.nombre AS especialidad, COUNT(*)::int AS total
            FROM cita c
            JOIN especialidad e ON e.id = c.especialidad_id
            GROUP BY e.nombre
            ORDER BY total DESC
            """
        )
        with session_scope() as s:
            rows = s.execute(sql).all()
        return [BarEspecialidad(especialidad=r[0], total=r[1]) for r in rows]

    @strawberry.field
    def citas_serie(self, granularidad: str = "month") -> List[SerieCitas]:
        gran = granularidad.lower()
        if gran not in ("week", "month"):
            gran = "month"
        trunc = "week" if gran == "week" else "month"
        sql = text(
            f"""
            SELECT to_char(date_trunc('{trunc}', h.fecha), 'YYYY-MM-DD') AS period, COUNT(*)::int AS total
            FROM cita c
            JOIN horarios h ON h.id = c.horario_id
            GROUP BY 1
            ORDER BY 1
            """
        )
        with session_scope() as s:
            rows = s.execute(sql).all()
        return [SerieCitas(period=r[0], total=r[1]) for r in rows]

    @strawberry.field
    def kpi_asistencia(self) -> KpiAsistencia:
        sql = text(
            """
            SELECT
              COUNT(*)::int AS total,
              SUM(CASE WHEN h.fecha < CURRENT_DATE THEN 1 ELSE 0 END)::int AS attended
            FROM cita c
            JOIN horarios h ON h.id = c.horario_id
            """
        )
        with session_scope() as s:
            row = s.execute(sql).fetchone()
        total = int(row[0]) if row and row[0] is not None else 0
        attended = int(row[1]) if row and row[1] is not None else 0
        percent = 0.0 if total == 0 else round(attended / total * 100.0, 2)
        return KpiAsistencia(percent=percent, attended=attended, total=total)

    @strawberry.field
    def heatmap_horarios(self) -> List[HeatmapBin]:
        sql = text(
            """
            SELECT EXTRACT(DOW FROM h.fecha)::int AS dow,
                   EXTRACT(HOUR FROM h.time_slot)::int AS hour,
                   COUNT(*)::int AS total
            FROM cita c
            JOIN horarios h ON h.id = c.horario_id
            GROUP BY 1,2
            ORDER BY 1,2
            """
        )
        with session_scope() as s:
            rows = s.execute(sql).all()
        return [HeatmapBin(dow=r[0], hour=r[1], total=r[2]) for r in rows]

    @strawberry.field
    def citas_por_mes(self) -> List[SerieCitas]:
        sql = text(
            """
            SELECT to_char(date_trunc('month', h.fecha), 'YYYY-MM') AS period, COUNT(*)::int AS total
            FROM cita c
            JOIN horarios h ON h.id = c.horario_id
            GROUP BY 1
            ORDER BY 1
            """
        )
        with session_scope() as s:
            rows = s.execute(sql).all()
        return [SerieCitas(period=r[0], total=r[1]) for r in rows]

    @strawberry.field
    def citas_por_dia(self) -> List[SerieCitas]:
        sql = text(
            """
            SELECT to_char(h.fecha, 'YYYY-MM-DD') AS period, COUNT(*)::int AS total
            FROM cita c
            JOIN horarios h ON h.id = c.horario_id
            GROUP BY 1
            ORDER BY 1
            """
        )
        with session_scope() as s:
            rows = s.execute(sql).all()
        return [SerieCitas(period=r[0], total=r[1]) for r in rows]

    @strawberry.field
    def kpi_crecimiento_citas(self) -> Optional[KpiCrecimiento]:
        sql = text(
            """
            WITH monthly AS (
                SELECT date_trunc('month', h.fecha) AS m, COUNT(*)::int AS total
                FROM cita c
                JOIN horarios h ON h.id = c.horario_id
                GROUP BY 1
            ), latest AS (
                SELECT m, total, ROW_NUMBER() OVER (ORDER BY m DESC) AS rn
                FROM monthly
            )
            SELECT to_char(curr.m, 'YYYY-MM') AS current_m,
                   to_char(prev.m, 'YYYY-MM') AS previous_m,
                   curr.total AS current_total,
                   prev.total AS previous_total
            FROM latest curr
            JOIN latest prev ON prev.rn = curr.rn + 1
            WHERE curr.rn = 1
            """
        )
        with session_scope() as s:
            row = s.execute(sql).fetchone()
        if not row:
            return None
        current_total = int(row[2]) if row[2] is not None else 0
        previous_total = int(row[3]) if row[3] is not None else 0
        growth_percent = 0.0
        if previous_total > 0:
            growth_percent = (current_total - previous_total) / previous_total * 100.0
        return KpiCrecimiento(
            current_month=row[0],
            previous_month=row[1],
            current_total=current_total,
            previous_total=previous_total,
            growth_percent=round(growth_percent, 2),
        )

    @strawberry.field
    def usuarios_crecimiento(self) -> List[SerieCitas]:
        sql = text(
            """
            WITH first_use AS (
                SELECT c.usuario_id AS uid, MIN(h.fecha) AS first_date
                FROM cita c
                JOIN horarios h ON h.id = c.horario_id
                GROUP BY c.usuario_id
            )
            SELECT to_char(date_trunc('month', first_date), 'YYYY-MM') AS period,
                   COUNT(*)::int AS total
            FROM first_use
            GROUP BY 1
            ORDER BY 1
            """
        )
        with session_scope() as s:
            rows = s.execute(sql).all()
        return [SerieCitas(period=r[0], total=r[1]) for r in rows]

    @strawberry.field
    def kpi_ocupacion_horarios(self) -> KpiOcupacion:
        """
        KPI: Tasa de Ocupación de Horarios
        Calcula el % de horarios ocupados (con citas) vs total de horarios
        """
        sql = text(
            """
            SELECT 
              COUNT(DISTINCT h.id)::int AS total_horarios,
              COUNT(DISTINCT c.horario_id)::int AS horarios_ocupados
            FROM horarios h
            LEFT JOIN cita c ON c.horario_id = h.id
            WHERE h.fecha >= CURRENT_DATE - INTERVAL '30 days'
            """
        )
        with session_scope() as s:
            row = s.execute(sql).fetchone()
        total = int(row[0]) if row and row[0] is not None else 0
        ocupados = int(row[1]) if row and row[1] is not None else 0
        percent = 0.0 if total == 0 else round(ocupados / total * 100.0, 2)
        return KpiOcupacion(percent=percent, ocupados=ocupados, total=total)

    @strawberry.field
    def kpi_tasa_cancelacion(self) -> KpiCancelacion:
        """
        KPI: Tasa de Cancelación
        Calcula el % de citas canceladas (horarios que volvieron a estar disponibles)
        Aproximación: horarios con fecha pasada que están disponibles = cancelados
        """
        sql = text(
            """
            SELECT 
              COUNT(*)::int AS total_horarios_pasados,
              SUM(CASE WHEN h.disponibilidad = true THEN 1 ELSE 0 END)::int AS cancelados
            FROM horarios h
            WHERE h.fecha < CURRENT_DATE 
              AND h.fecha >= CURRENT_DATE - INTERVAL '90 days'
            """
        )
        with session_scope() as s:
            row = s.execute(sql).fetchone()
        total = int(row[0]) if row and row[0] is not None else 0
        canceladas = int(row[1]) if row and row[1] is not None else 0
        percent = 0.0 if total == 0 else round(canceladas / total * 100.0, 2)
        return KpiCancelacion(percent=percent, canceladas=canceladas, total=total)

schema = strawberry.Schema(query=Query)
