$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$filePath = "c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"
$workbook = $excel.Workbooks.Open($filePath)

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
$sheetBD.Range("A1:O1").Copy($sheetSol.Range("A1")) | Out-Null

$currentRow = 2
for ($r = 2; $r -le 1000; $r++) {
    $movType = [string]$sheetBD.Cells.Item($r, 5).Value2
    if ($movType.ToUpper().Contains("SOLICITUD")) {
        $sheetBD.Range("A$r`:" + "O$r").Copy($sheetSol.Range("A$currentRow")) | Out-Null
        $sheetBD.Range("A$r`:" + "O$r").ClearContents() | Out-Null
        $currentRow++
    }
}

# Apply sort to push empty cleared rows to bottom in BD_DIESEL
$range = $sheetBD.Range("A2:O1000")
$range.Sort($sheetBD.Range("B2"), 1) # Sort by Date (B2) Ascending

# Reapply formulas to all 3 sheets
$sheetBD.Range("C2:C1000").Formula = '=IF(B2="","", "Semana "&WEEKNUM(B2,2))'
$sheetBD.Range("A2:A1000").Formula = '=IF(B2="","", IFERROR(VLOOKUP(E2,CATALOGOS!$J$2:$K$50,2,0),"XX") & "-" & IFERROR(VLOOKUP(F2,CATALOGOS!$A$2:$B$50,2,0),"XX") & "-" & WEEKNUM(B2,2) & "-" & TEXT(ROW()-1,"000"))'

$sheetSol.Range("C2:C1000").Formula = '=IF(B2="","", "Semana "&WEEKNUM(B2,2))'
$sheetSol.Range("A2:A1000").Formula = '=IF(B2="","", "SO" & "-" & IFERROR(VLOOKUP(F2,CATALOGOS!$A$2:$B$50,2,0),"XX") & "-" & WEEKNUM(B2,2) & "-" & TEXT(ROW()-1,"000"))'

$sheetFac = $workbook.Worksheets.Item("BD_FACTURAS")
$sheetFac.Range("D2:D1000").Formula = '=IF(C2="","", "Semana "&WEEKNUM(C2,2))'
$sheetFac.Range("A2:A1000").Formula = '=IF(C2="","", "FA" & "-" & IFERROR(VLOOKUP(F2,CATALOGOS!$A$2:$B$50,2,0),"XX") & "-" & WEEKNUM(C2,2) & "-" & TEXT(ROW()-1,"000"))'

$sheetSol.UsedRange.Columns.AutoFit() | Out-Null

$workbook.Save()
$workbook.Close()
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "Separacion rapida de solicitudes completada."
