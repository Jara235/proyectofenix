import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

for sem in ['SEMANA 32', 'SEMANA 31', 'SEMANA 30']:
    print(f"\n=== {sem} TAGS SIN AUTORIZACION CON CONSUMO ===")
    cur.execute("""
        SELECT m.empresa, m.responsable, m.tag, m.no_economico, m.placas, 
               COALESCE(a.monto_autorizado, 0) as autorizado,
               SUM(ABS(m.importe)) as consumo,
               COUNT(*) as pasadas
        FROM tags.movimientos m
        LEFT JOIN tags.autorizaciones a ON (
            m.tag = a.tag 
            OR (m.tag IS NOT NULL AND a.tag IS NOT NULL AND LENGTH(a.tag) >= 6 AND (m.tag ILIKE '%%' || a.tag || '%%' OR a.tag ILIKE '%%' || m.tag || '%%'))
        )
        WHERE (m.semana = %s OR m.semana = %s)
          AND (a.monto_autorizado IS NULL OR a.monto_autorizado = 0)
          AND m.responsable NOT IN ('JOSE TRUJANO', 'ING. PEPE', 'ING PEPE', 'JOSE TRUJANO (JEEP)', 'JORGE TRUJANO')
          AND m.tag NOT IN ('IMDM28600382', 'IMDM28600315', 'IMDM30874314', 'IMDM28600323', 'IMDM28600327')
        GROUP BY m.empresa, m.responsable, m.tag, m.no_economico, m.placas, a.monto_autorizado
        ORDER BY m.empresa, m.responsable;
    """, (sem, sem.replace('SEMANA ', '')))
    for r in cur.fetchall():
        print(f"[{r['empresa']}] {r['responsable']} | Tag: {r['tag']} | Placas: {r['placas']} | Consumo: ${r['consumo']:,.2f} ({r['pasadas']} pasadas)")

conn.close()
