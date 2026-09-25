from app_admin import app
import json

client = app.test_client()

with client.session_transaction() as sess:
    sess['user_id'] = 1
    sess['username'] = 'admin'
    sess['role'] = 'ADMIN'

resp = client.get('/api/admin/resumen/gasolina?semana=33')
data = resp.get_json()

print("Status code:", resp.status_code)
print("Success:", data.get('success'))
print("Semana:", data.get('semana'))
print("Totales:")
print("  Total personas:", data['totales']['total_personas'])
print("  Total excedidos:", data['totales']['total_excedidos'])
print("  Presupuesto total:", data['totales']['presupuesto_total'])
print("  Consumo total:", data['totales']['consumo_total'])
print("  Excedente total:", data['totales']['excedente_total'])

print(f"\nExcedidos ({len(data['excedidos'])}):")
for ex in data['excedidos']:
    print(f"  {ex['responsable']} | {ex['centro_trabajo']} | {ex['placas']} | Auth: ${ex['autorizado']:,.2f} | Cons: ${ex['consumido']:,.2f} | Exc: +${ex['monto_excedido']:,.2f} (+{ex['porcentaje_exceso']}%) | Cargas: {ex['num_cargas']}")

print("\nEstadísticas - Días de la semana:")
for d in data['estadisticas']['dias_semana']:
    print(f"  {d['dia_nombre']}: ${d['total_importe']:,.2f} ({d['total_litros']:,.2f} L)")

print("\nEstadísticas - Estaciones Mix:")
for es in data['estadisticas']['estaciones_mix']:
    print(f"  {es['gasolinera']}: ${es['total_importe']:,.2f} ({es['total_litros']:,.2f} L) - {es['porcentaje_participacion']}%")

print("\nEstadísticas - Promedios Centros:")
for p in data['estadisticas']['promedios_centros']:
    print(f"  {p['obra']}: {p['litros_diarios_prom']} L/día | ${p['costo_diario_prom']}/día | Esp: ${p['consumo_esperado']:,.2f} | Real: ${p['consumo_real']:,.2f} | Var: ${p['variacion']:,.2f} | Dev: {p['desviacion_pct']}%")
