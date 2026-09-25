$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$excel.AutomationSecurity = 3 # msoAutomationSecurityForceDisable

$filePath = "c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"

try {
    Write-Host "Opening..."
    # Open(Filename, UpdateLinks, ReadOnly)
    $workbook = $excel.Workbooks.Open($filePath, 0, $false)
    if ($null -eq $workbook) {
        Write-Host "Workbook is NULL"
    } else {
        Write-Host "Workbook opened successfully!"
        $sheet = $workbook.Worksheets.Item("BD_FACTURAS")
        Write-Host "Sheet obtained: $($sheet.Name)"
        $workbook.Close($false)
    }
} catch {
    Write-Host "Error: $_"
} finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
}
