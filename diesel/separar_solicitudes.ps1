$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$filePath = "c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"
$workbook = $excel.Workbooks.Open($filePath)

# Verificar o crear BD_SOLICITUDES
$sheetSol = $null
foreach ($sheet in $workbook.Worksheets) {
    if ($sheet.Name -eq "BD_SOLICITUDES") {
        $sheetSol = $sheet
        break
    }
}

if ($null -eq $sheetSol) {
    $sheetSol = $workbook.Worksheets.Add([System.Reflection.Missing]::Value, $workbook.Worksheets.Item($workbook.Worksheets.Count))
    $sheetSol.Name = "BD_SOLICITUDES"
} else {
    $sheetSol.Cells.Clear()
}

$sheetBD = $workbook.Worksheets.Item("BD_DIESEL")

# Copiar encabezados (A1:O1)
$sheetBD.Range("A1:O1").Copy($sheetSol.Range("A1")) | Out-Null

$maxRow = $sheetBD.Cells.Item($sheetBD.Rows.Count, "E").End(-4162).Row

$currentRow = 2
for ($r = $maxRow; $r -ge 2; $r--) {
    $movType = [string]$sheetBD.Cells.Item($r, 5).Value2
    if ($movType.ToUpper().Contains("SOLICITUD")) {
        # Copiar rango de valores
        $sheetBD.Range("A$r`:" + "O$r").Copy($sheetSol.Range("A$currentRow")) | Out-Null
        $sheetBD.Rows.Item($r).Delete() | Out-Null
        $currentRow++
    }
}

# Restaurar Fórmulas en BD_DIESEL
$sheetBD.Range("C2:C1000").Formula = '=IF(B2="","", "Semana "&WEEKNUM(B2,2))'
$sheetBD.Range("A2:A1000").Formula = '=IF(B2="","", IFERROR(VLOOKUP(E2,CATALOGOS!$J$2:$K$50,2,0),"XX") & "-" & IFERROR(VLOOKUP(F2,CATALOGOS!$A$2:$B$50,2,0),"XX") & "-" & WEEKNUM(B2,2) & "-" & TEXT(ROW()-1,"000"))'

# Fórmulas en BD_SOLICITUDES
$sheetSol.Range("C2:C1000").Formula = '=IF(B2="","", "Semana "&WEEKNUM(B2,2))'
$sheetSol.Range("A2:A1000").Formula = '=IF(B2="","", IFERROR(VLOOKUP(E2,CATALOGOS!$J$2:$K$50,2,0),"XX") & "-" & IFERROR(VLOOKUP(F2,CATALOGOS!$A$2:$B$50,2,0),"XX") & "-" & WEEKNUM(B2,2) & "-" & TEXT(ROW()-1,"000"))'

# Fórmulas en BD_FACTURAS
$sheetFac = $workbook.Worksheets.Item("BD_FACTURAS")
$sheetFac.Range("D2:D1000").Formula = '=IF(C2="","", "Semana "&WEEKNUM(C2,2))'
$sheetFac.Range("A2:A1000").Formula = '=IF(C2="","", "FA" & "-" & IFERROR(VLOOKUP(F2,CATALOGOS!$A$2:$B$50,2,0),"XX") & "-" & WEEKNUM(C2,2) & "-" & TEXT(ROW()-1,"000"))'

$sheetSol.UsedRange.Columns.AutoFit() | Out-Null

$workbook.Save()
$workbook.Close()
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "Separacion de solicitudes completada exitosamente."
