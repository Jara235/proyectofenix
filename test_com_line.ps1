$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$filePath = "c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"

try {
    Write-Host "Opening workbook..."
    $workbook = $excel.Workbooks.Open($filePath)
    Write-Host "Workbook opened."
    
    $sheet = $workbook.Worksheets.Item("BD_FACTURAS")
    Write-Host "Sheet obtained."
    
    $rows = $sheet.Rows
    Write-Host "Rows obtained."
    
    $rowsCount = $rows.Count
    Write-Host "Rows count: $rowsCount"
    
    $cell = $sheet.Cells.Item($rowsCount, 2)
    Write-Host "Cell obtained."
    
    # Let's see if End() works
    $endCell = $cell.End(-4162)
    Write-Host "End cell obtained."
    
    $lastRow = $endCell.Row
    Write-Host "Last row: $lastRow"
    
    $workbook.Close($false)
} catch {
    Write-Host "ERROR at line $($_.InvocationInfo.ScriptLineNumber): $_"
} finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
}
