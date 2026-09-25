$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$filePath = "c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"
$workbook = $excel.Workbooks.Open($filePath)

# Fórmulas en BD_DIESEL
$sheetBD = $workbook.Worksheets.Item("BD_DIESEL")
$sheetBD.Range("C2:C1000").Formula = '=IF(B2="","", "Semana "&WEEKNUM(B2,2))'
$sheetBD.Range("A2:A1000").Formula = '=IF(B2="","", IFERROR(VLOOKUP(E2,CATALOGOS!$J$2:$K$50,2,0),"XX") & "-" & IFERROR(VLOOKUP(F2,CATALOGOS!$A$2:$B$50,2,0),"XX") & "-" & WEEKNUM(B2,2) & "-" & TEXT(ROW()-1,"000"))'

# Fórmulas en BD_SOLICITUDES
$sheetSol = $workbook.Worksheets.Item("BD_SOLICITUDES")
$sheetSol.Range("C2:C1000").Formula = '=IF(B2="","", "Semana "&WEEKNUM(B2,2))'
$sheetSol.Range("A2:A1000").Formula = '=IF(B2="","", "SO" & "-" & IFERROR(VLOOKUP(F2,CATALOGOS!$A$2:$B$50,2,0),"XX") & "-" & WEEKNUM(B2,2) & "-" & TEXT(ROW()-1,"000"))'

# Fórmulas en BD_FACTURAS
$sheetFac = $workbook.Worksheets.Item("BD_FACTURAS")
$sheetFac.Range("D2:D1000").Formula = '=IF(C2="","", "Semana "&WEEKNUM(C2,2))'
$sheetFac.Range("A2:A1000").Formula = '=IF(C2="","", "FA" & "-" & IFERROR(VLOOKUP(F2,CATALOGOS!$A$2:$B$50,2,0),"XX") & "-" & WEEKNUM(C2,2) & "-" & TEXT(ROW()-1,"000"))'

$workbook.Save()
$workbook.Close()
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "Formulas inyectadas en las 3 hojas."
