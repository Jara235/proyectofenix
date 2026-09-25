$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$files = @(
    "C:\Users\JOSE\Desktop\Proyecto fenix\gasolina\SEMANA 26 (1).xlsx",
    "C:\Users\JOSE\Desktop\Proyecto fenix\gasolina\CONSUMOS  DE GASOLINA SEMANALES GT.xlsx",
    "C:\Users\JOSE\Desktop\Proyecto fenix\gasolina\CONTROL JDJ PROVISIONAL semana 27.xlsx"
)

foreach ($f in $files) {
    Write-Host "--- File: $f ---"
    $workbook = $excel.Workbooks.Open($f)
    foreach ($sheet in $workbook.Sheets) {
        Write-Host "Sheet: $($sheet.Name)"
        $maxRow = 15
        $maxCol = 10
        for ($r = 1; $r -le $maxRow; $r++) {
            $rowStr = ""
            for ($c = 1; $c -le $maxCol; $c++) {
                $val = $sheet.Cells.Item($r, $c).Text
                $rowStr += """$val"","
            }
            Write-Host $rowStr
        }
    }
    $workbook.Close($false)
}

$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
