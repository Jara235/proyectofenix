$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$filePath = "c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"
$workbook = $excel.Workbooks.Open($filePath)

# 1. BD_DIESEL
$sheetBD = $workbook.Worksheets.Item("BD_DIESEL")
# SEMANA (Col C)
$sheetBD.Range("C2:C1000").Formula = '=IF(B2="","", "Semana "&WEEKNUM(B2,2))'
# FOLIO_CONCILIACION (Col A)
$sheetBD.Range("A2:A1000").Formula = '=IF(B2="","", IFERROR(VLOOKUP(E2,CATALOGOS!$E$2:$F$50,2,0),"XX") & "-" & IFERROR(VLOOKUP(F2,CATALOGOS!$A$2:$B$50,2,0),"XX") & "-" & WEEKNUM(B2,2) & "-" & TEXT(ROW()-1,"000"))'

# 2. BD_FACTURAS
$sheetFac = $workbook.Worksheets.Item("BD_FACTURAS")
# SEMANA (Col D)
$sheetFac.Range("D2:D1000").Formula = '=IF(C2="","", "Semana "&WEEKNUM(C2,2))'
# FOLIO_CONCILIACION (Col A)
$sheetFac.Range("A2:A1000").Formula = '=IF(C2="","", "FA" & "-" & IFERROR(VLOOKUP(F2,CATALOGOS!$A$2:$B$50,2,0),"XX") & "-" & WEEKNUM(C2,2) & "-" & TEXT(ROW()-1,"000"))'

$workbook.Save()
$workbook.Close()
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
