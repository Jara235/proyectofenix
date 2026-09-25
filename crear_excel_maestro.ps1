$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$workbook = $excel.Workbooks.Add()

# Renombrar hoja 1
$sheet1 = $workbook.Worksheets.Item(1)
$sheet1.Name = "BD_DIESEL"

# Encabezados de BD_DIESEL
$sheet1.Cells.Item(1,1) = "FOLIO"
$sheet1.Cells.Item(1,2) = "FECHA"
$sheet1.Cells.Item(1,3) = "SEMANA"
$sheet1.Cells.Item(1,4) = "TIPO_MOVIMIENTO"
$sheet1.Cells.Item(1,5) = "OBRA_DESTINO"
$sheet1.Cells.Item(1,6) = "EQUIPO_ECONOMICO"
$sheet1.Cells.Item(1,7) = "LITROS"
$sheet1.Cells.Item(1,8) = "COSTO_POR_LITRO"
$sheet1.Cells.Item(1,9) = "IMPORTE_TOTAL"
$sheet1.Cells.Item(1,10) = "RESPONSABLE"
$sheet1.Cells.Item(1,11) = "OPERADOR"
$sheet1.Cells.Item(1,12) = "ESTATUS_CONCILIACION"
$sheet1.Cells.Item(1,13) = "OBSERVACIONES"

# Dar formato a encabezados
$range1 = $sheet1.Range("A1:M1")
$range1.Font.Bold = $true
$range1.Interior.ColorIndex = 15 # Gris claro
$sheet1.UsedRange.Columns.AutoFit() | Out-Null

# Crear hoja 2 (Catálogos)
$sheet2 = $workbook.Worksheets.Add()
$sheet2.Name = "CATALOGOS"

# Encabezados de CATALOGOS
$sheet2.Cells.Item(1,1) = "OBRAS"
$sheet2.Cells.Item(1,2) = "EQUIPOS"
$sheet2.Cells.Item(1,3) = "RESPONSABLES"
$sheet2.Cells.Item(1,4) = "OPERADORES"
$sheet2.Cells.Item(1,5) = "TIPO_MOVIMIENTO"

$range2 = $sheet2.Range("A1:E1")
$range2.Font.Bold = $true
$range2.Interior.ColorIndex = 15
$sheet2.UsedRange.Columns.AutoFit() | Out-Null

# Crear hoja 3 (Tablas Dinamicas - vacía para que el usuario la arme)
$sheet3 = $workbook.Worksheets.Add()
$sheet3.Name = "TABLAS_DINAMICAS"
$sheet3.Cells.Item(1,1) = "AQUÍ INSERTARÁS TUS TABLAS DINÁMICAS"
$sheet3.Range("A1:A1").Font.Bold = $true

# Guardar archivo
$filePath = "c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"
if (Test-Path $filePath) {
    Remove-Item $filePath -Force
}
$workbook.SaveAs($filePath)
$workbook.Close()
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
