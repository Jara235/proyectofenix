import psycopg2
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
conn.autocommit = True
cur = conn.cursor()

# 1. Tabla de Complementos de Pago
cur.execute("""
CREATE TABLE IF NOT EXISTS diesel.complementos_pago (
    id SERIAL PRIMARY KEY,
    folio_complemento VARCHAR(100),
    fecha_pago DATE,
    proveedor VARCHAR(255),
    monto_total NUMERIC(12,2),
    archivo_pdf BYTEA,
    archivo_xml BYTEA,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 2. Relacion Pagos -> Facturas
cur.execute("""
CREATE TABLE IF NOT EXISTS diesel.pagos_facturas (
    id SERIAL PRIMARY KEY,
    complemento_id INTEGER REFERENCES diesel.complementos_pago(id) ON DELETE CASCADE,
    factura_id INTEGER REFERENCES diesel.facturas(id) ON DELETE CASCADE,
    monto_aplicado NUMERIC(12,2)
);
""")

# 3. Add estatus_pago to diesel.facturas if not exists
try:
    cur.execute("ALTER TABLE diesel.facturas ADD COLUMN estatus_pago VARCHAR(50) DEFAULT 'PENDIENTE'")
except Exception as e:
    print("Column already exists or error:", e)

print("Tables created successfully.")
conn.close()
