import os
import glob
import psycopg2

def main():
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor()
    
    # Process both tables
    for schema in ['diesel', 'gasolina']:
        print(f"--- Procesando {schema.upper()} ---")
        cur.execute(f"SELECT id, uuid_cfdi, folio_factura FROM {schema}.facturas WHERE archivo_pdf IS NULL")
        rows = cur.fetchall()
        print(f"Encontradas {len(rows)} facturas sin PDF en la base de datos.")
        
        pdf_folder = f"c:/Users/JOSE/Desktop/Proyecto fenix/facturas/{schema.capitalize()}"
        pdf_files = glob.glob(f"{pdf_folder}/**/*.pdf", recursive=True)
        
        print(f"Encontrados {len(pdf_files)} PDFs en {pdf_folder}")
        
        updated_count = 0
        
        for row in rows:
            f_id, uuid_cfdi, folio_factura = row
            uuid_cfdi = uuid_cfdi.lower() if uuid_cfdi else ''
            folio_factura = folio_factura.lower() if folio_factura else ''
            
            matched_pdf = None
            for pdf_path in pdf_files:
                basename = os.path.basename(pdf_path).lower()
                
                # Check by UUID
                if uuid_cfdi and uuid_cfdi in basename:
                    matched_pdf = pdf_path
                    break
                
                # Check by Folio
                if folio_factura and len(folio_factura) > 2 and folio_factura in basename:
                    matched_pdf = pdf_path
                    break
            
            if matched_pdf:
                with open(matched_pdf, 'rb') as f:
                    pdf_bytes = f.read()
                
                cur.execute(f"UPDATE {schema}.facturas SET archivo_pdf = %s WHERE id = %s", (pdf_bytes, f_id))
                updated_count += 1
        
        conn.commit()
        print(f"Actualizadas {updated_count} facturas con su PDF en {schema}.")
        
    cur.close()
    conn.close()
    print("Listo!")

if __name__ == '__main__':
    main()
