import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

# 1. Agregar columna saldo_inicial_vales si no existe
try:
    cur.execute("""
        ALTER TABLE diesel.control_vales_jalisco 
        ADD COLUMN IF NOT EXISTS saldo_inicial_vales NUMERIC(12,2) DEFAULT 0
    """)
    conn.commit()
    print("Columna saldo_inicial_vales agregada (o ya existia)")
except Exception as e:
    print(f"Error columna: {e}")
    conn.rollback()

# 2. Insertar/actualizar saldo inicial por semana + ajustes para semanas 22 y 25
datos = [
    # (semana, saldo_inicial_vales, ajuste_semanal)
    (22, 15012.00,   0.00),
    (23, 30294.00,   25056.00),
    (24, 37716.00,   31320.00),
    (25, 31300.00,   0.00),
    (26, 41030.00,   40500.00),
    (27, 75374.50,   73497.50),
    (28, 76181.00,   62396.50),
]

for semana, saldo_ini, ajuste in datos:
    cur.execute("""
        INSERT INTO diesel.control_vales_jalisco (semana, ajuste_semanal, saldo_inicial_vales)
        VALUES (%s, %s, %s)
        ON CONFLICT (semana) DO UPDATE 
        SET saldo_inicial_vales = EXCLUDED.saldo_inicial_vales,
            ajuste_semanal = EXCLUDED.ajuste_semanal
    """, (semana, ajuste, saldo_ini))
    print(f"  Semana {semana}: saldo_ini=  ajuste=")

conn.commit()

# 3. Verificar lo guardado
cur.execute("SELECT semana, saldo_inicial_vales, ajuste_semanal FROM diesel.control_vales_jalisco ORDER BY semana")
print("\n=== DATOS GUARDADOS ===")
for r in cur.fetchall():
    print(dict(r))

cur.close()
conn.close()
print("\nOK - Todo guardado")
