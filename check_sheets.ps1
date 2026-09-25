$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$filePath = "c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"
$workbook = $excel.Workbooks.Open($filePath)

if ($null -eq $workbook) {
    Write-Host "ERROR: Workbook failed to open."
} else {
    Write-Host "Workbook opened successfully. Sheets:"
    foreach ($sheet in $workbook.Worksheets) {
        Write-Host " - '"$sheet.Name"'"
    }
    $workbook.Close($false)
}
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
