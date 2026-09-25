$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$excel.AutomationSecurity = 3 # Force Disable Macros

$jsonPath = "c:\Users\JOSE\Desktop\Proyecto fenix\temp_facturas.json"
$filePath = "c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"

try {
    if (-not (Test-Path $jsonPath)) {
        Write-Host "ERROR: temp_facturas.json no existe."
        exit 1
    }
    
    $invoices = Get-Content $jsonPath -Raw | ConvertFrom-Json
    Write-Host "Cargadas $($invoices.Count) facturas desde JSON."
    
    Write-Host "Abriendo Excel (esto puede tomar 10-15 segundos)..."
    $workbook = $excel.Workbooks.Open($filePath, 0, $false)
    if ($null -eq $workbook) {
        Write-Host "ERROR: No se pudo abrir el archivo de Excel."
        exit 1
    }
    
    # Disable automatic calculations during edit
    $excel.Calculation = -4135 # xlCalculationManual
    Write-Host "Calculo automatico desactivado."
    
    $sheet = $workbook.Worksheets.Item("BD_FACTURAS")
    Write-Host "Pestaña obtenida con éxito."
    
    # Buscar ultima fila real
    $lastRow = 1
    while ($null -ne $sheet.Cells.Item($lastRow + 1, 2).Value2) {
        $lastRow++
    }
    Write-Host "Ultima fila real encontrada: $lastRow"
    
    # Leer folios existentes para evitar duplicados
    $existingFolios = @{}
    for ($r = 2; $r -le $lastRow; $r++) {
        $val2 = $sheet.Cells.Item($r, 2).Value2
        if ($null -ne $val2) {
            $fVal = "$($val2)".Trim()
            if ($fVal -ne "") {
                $existingFolios[$fVal] = $true
            }
        }
    }
    
    $added = 0
    $currentRow = $lastRow + 1
    
    foreach ($inv in $invoices) {
        $folioStr = ""
        if ($null -ne $inv.folio) {
            $folioStr = "$($inv.folio)".Trim()
        }
        
        if ($existingFolios.ContainsKey($folioStr)) {
            Write-Host "Factura folio $folioStr ya existe en el Excel, omitiendo."
            continue
        }
        
        # Escribir columnas
        # Col 2 (B): FOLIO
        $sheet.Cells.Item($currentRow, 2).Value2 = "$($inv.folio)"
        # Col 3 (C): FECHA
        $sheet.Cells.Item($currentRow, 3).Value2 = "$($inv.fecha)"
        # Col 5 (E): PROVEEDOR
        $sheet.Cells.Item($currentRow, 5).Value2 = "$($inv.proveedor)"
        # Col 6 (F): PUNTO DE CARGA
        $sheet.Cells.Item($currentRow, 6).Value2 = "$($inv.destino)"
        
        # Numeric values cast to [double]
        # Col 7 (G): LITROS
        $sheet.Cells.Item($currentRow, 7).Value2 = [double]$inv.litros
        # Col 8 (H): PRECIO
        $sheet.Cells.Item($currentRow, 8).Value2 = [double]$inv.precio
        # Col 9 (I): IMPORTE
        $sheet.Cells.Item($currentRow, 9).Value2 = [double]$inv.importe
        # Col 10 (J): IVA
        $sheet.Cells.Item($currentRow, 10).Value2 = [double]$inv.iva
        # Col 11 (K): TOTAL
        $sheet.Cells.Item($currentRow, 11).Value2 = [double]$inv.total
        
        # Col 12 (L): TIPO
        $sheet.Cells.Item($currentRow, 12).Value2 = "Diésel"
        
        # Formulas
        $sheet.Cells.Item($currentRow, 4).Formula = "=IF(C$currentRow=`"`",`"`", `"Semana `" & WEEKNUM(C$currentRow, 2))"
        $sheet.Cells.Item($currentRow, 1).Formula = "=IF(C$currentRow=`"`",`"`", `"FA`" & `"-`" & IFERROR(VLOOKUP(F$currentRow, CATALOGOS!`$A`$2:`$B`$50, 2, 0), `"XX`") & `"-`" & WEEKNUM(C$currentRow, 2) & `"-`" & TEXT(ROW()-1, `"000`"))"
        
        $currentRow++
        $added++
    }
    
    # Restore calculation to automatic so formula values update
    $excel.Calculation = -4105 # xlCalculationAutomatic
    Write-Host "Calculo automatico restaurado."
    
    if ($added -gt 0) {
        Write-Host "Guardando cambios especificamente en la ruta con SaveAs..."
        $workbook.SaveAs($filePath, 51)
        Write-Host "Exito: Se agregaron $added nuevas facturas de Diesel."
    } else {
        Write-Host "No se agregaron nuevas facturas (todas ya existian)."
    }
    
    $workbook.Close()
} catch {
    Write-Host "Error durante la ejecucion: $_"
} finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
}
