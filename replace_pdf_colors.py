import sys
import re

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace headers for Responsables
content = content.replace(
    "Paragraph('<b>Responsable</b>', st_celda),",
    "Paragraph('<font color=\"white\"><b>Responsable</b></font>', st_celda),"
).replace(
    "Paragraph('<b>Obras / Centros de Trabajo</b>', st_celda),",
    "Paragraph('<font color=\"white\"><b>Obras / Centros de Trabajo</b></font>', st_celda),"
).replace(
    "Paragraph('<para align=center><b>Autorizado (L)</b></para>', st_celda),",
    "Paragraph('<para align=center><font color=\"white\"><b>Autorizado (L)</b></font></para>', st_celda),"
).replace(
    "Paragraph('<para align=center><b>Consumido (L)</b></para>', st_celda),",
    "Paragraph('<para align=center><font color=\"white\"><b>Consumido (L)</b></font></para>', st_celda),"
).replace(
    "Paragraph('<para align=center><b>Diferencia (L)</b></para>', st_celda),",
    "Paragraph('<para align=center><font color=\"white\"><b>Diferencia (L)</b></font></para>', st_celda),"
)

# Replace Totals for Responsables
content = content.replace(
    "Paragraph('<b>TOTAL RESPONSABLES</b>', st_celda),",
    "Paragraph('<font color=\"white\"><b>TOTAL RESPONSABLES</b></font>', st_celda),"
).replace(
    "Paragraph(f'<para align=right><b>{tot_auto:,.2f} L</b></para>', st_celda),",
    "Paragraph(f'<para align=right><font color=\"white\"><b>{tot_auto:,.2f} L</b></font></para>', st_celda),"
).replace(
    "Paragraph(f'<para align=right><b>{tot_con:,.2f} L</b></para>', st_celda),",
    "Paragraph(f'<para align=right><font color=\"white\"><b>{tot_con:,.2f} L</b></font></para>', st_celda),"
)
# Note: diff_tot already has a font color (ROJO/VERDE) so we don't wrap it in white.

# Replace headers for Maquinaria
content = content.replace(
    "Paragraph('<b>Obra / Centro de Trabajo</b>', st_celda),",
    "Paragraph('<font color=\"white\"><b>Obra / Centro de Trabajo</b></font>', st_celda),"
).replace(
    "Paragraph('<b>Maquinaria / Equipo</b>', st_celda),",
    "Paragraph('<font color=\"white\"><b>Maquinaria / Equipo</b></font>', st_celda),"
)

# Replace background color for Maquinaria to PRIMARIO
content = content.replace(
    "('BACKGROUND', (0,0), (-1,0), COLOR_OSCURO),",
    "('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARIO),"
)

# Replace Totals for Maquinaria
content = content.replace(
    "Paragraph('<b>TOTAL MAQUINARIA</b>', st_celda),",
    "Paragraph('<font color=\"white\"><b>TOTAL MAQUINARIA</b></font>', st_celda),"
).replace(
    "Paragraph('<para align=right><b>—</b></para>', st_celda),",
    "Paragraph('<para align=right><font color=\"white\"><b>—</b></font></para>', st_celda),"
).replace(
    "Paragraph(f'<para align=right><b>{tot_maq_con:,.2f} L</b></para>', st_celda),",
    "Paragraph(f'<para align=right><font color=\"white\"><b>{tot_maq_con:,.2f} L</b></font></para>', st_celda),"
)

# Note: In my previous Python script, the dash might have been written as "-" or "—", let's handle both
content = content.replace(
    "Paragraph('<para align=right><b>-</b></para>', st_celda),",
    "Paragraph('<para align=right><font color=\"white\"><b>—</b></font></para>', st_celda),"
)

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced PDF text colors.")
