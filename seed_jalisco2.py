import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

datos = [
    (22, 15012.00,   0.00),
    (23, 30294.00,   25056.00),
    (24, 37716.00,   31320.00),
    (25, 31300.00,   0.00),
    (26, 41030.00,   40500.00),
    (27, 75374.50,   73497.50),
    (28, 76181.00,   62396.50),
]

for semana, saldo_ini, ajuste in datos:
    # Try UPDATE first, then INSERT if not exists
    cur.execute("""
        UPDATE diesel.control_vales_jalisco 
        SET saldo_inicial_vales = %s, ajuste_semanal = %s
        WHERE semana = %s AND tipo_combustible = 'DIESEL'
    """, (saldo_ini, ajuste, semana))
    
    if cur.rowcount == 0:
        # No existe, hacer INSERT
        cur.execute("""
            INSERT INTO diesel.control_vales_jalisco (semana, ajuste_semanal, saldo_inicial_vales, tipo_combustible)
            VALUES (%s, %s, %s, 'DIESEL')
        """, (semana, ajuste, saldo_ini))
    
    print(f"  Semana {semana}: saldo_ini=\  ajuste=\  -> {'updated' if cur.rowcount > 0 else 'inserted'}")

conn.commit()

# Verificar
cur.execute("SELECT semana, saldo_inicial_vales, ajuste_semanal FROM diesel.control_vales_jalisco ORDER BY semana")
print("\n=== GUARDADO EN BD ===")
for r in cur.fetchall():
    s = r['semana']
    si = float(r['saldo_inicial_vales'] or 0)
    aj = float(r['ajuste_semanal'] or 0)
    print(f"  Semana {s}: saldo_ini=\  ajuste=\")

cur.close()
conn.close()
print("\nOK")
