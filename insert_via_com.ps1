$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$jsonPath = "c:\Users\JOSE\Desktop\Proyecto fenix\temp_facturas.json"
$filePath = "c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"

try {
    if (-not (Test-Path $jsonPath)) {
        Write-Host "ERROR: temp_facturas.json no existe."
        exit 1
    }
    
    $invoices = Get-Content $jsonPath -Raw | ConvertFrom-Json
    Write-Host "Cargadas $($invoices.Count) facturas desde JSON."
    
    $workbook = $excel.Workbooks.Open($filePath)
    if ($null -eq $workbook) {
        Write-Host "ERROR: No se pudo abrir el archivo de Excel."
        exit 1
    }
    
    $sheet = $workbook.Worksheets.Item("BD_FACTURAS")
    
    # Obtener el ultimo renglon
    $lastRow = $sheet.Cells.Item($sheet.Rows.Count, 2).End(-4162).Row # End(xlUp) por columna B (Folio)
    Write-Host "Ultima fila con datos: $lastRow"
    
    # Leer folios existentes para evitar duplicados
    $existingFolios = @{}
    for ($r = 2; $r -le $lastRow; $r++) {
        $fVal = [string]$sheet.Cells.Item($r, 2).Value2
        if (-not [string]::IsNullOrEmpty($fVal)) {
            $existingFolios[$fVal.Trim()] = $true
        }
    }
    
    $added = 0
    $currentRow = $lastRow + 1
    
    foreach ($inv in $invoices) {
        $folioStr = [string]$inv.folio
        if ($null -ne $folioStr) {
            $folioStr = $folioStr.Trim()
        }
        
        if ($existingFolios.ContainsKey($folioStr)) {
            Write-Host "Factura folio $folioStr ya existe, omitiendo."
            continue
        }
        
        # Escribir columnas
        # Col 2 (B): FOLIO
        $sheet.Cells.Item($currentRow, 2).Value2 = $inv.folio
        # Col 3 (C): FECHA
        $sheet.Cells.Item($currentRow, 3).Value2 = $inv.fecha
        # Col 5 (E): PROVEEDOR
        $sheet.Cells.Item($currentRow, 5).Value2 = $inv.proveedor
        # Col 6 (F): PUNTO DE CARGA
        $sheet.Cells.Item($currentRow, 6).Value2 = $inv.destino
        # Col 7 (G): LITROS
        $sheet.Cells.Item($currentRow, 7).Value2 = $inv.litros
        # Col 8 (H): PRECIO
        $sheet.Cells.Item($currentRow, 8).Value2 = $inv.precio
        # Col 9 (I): IMPORTE
        $sheet.Cells.Item($currentRow, 9).Value2 = $inv.importe
        # Col 10 (J): IVA
        $sheet.Cells.Item($currentRow, 10).Value2 = $inv.iva
        # Col 11 (K): TOTAL
        $sheet.Cells.Item($currentRow, 11).Value2 = $inv.total
        # Col 12 (L): TIPO
        $sheet.Cells.Item($currentRow, 12).Value2 = "Diésel"
        
        # Formulas
        $sheet.Cells.Item($currentRow, 4).Formula = "=IF(C$currentRow=`"`",`"`", `"Semana `" & WEEKNUM(C$currentRow, 2))"
        $sheet.Cells.Item($currentRow, 1).Formula = "=IF(C$currentRow=`"`",`"`", `"FA`" & `"-`" & IFERROR(VLOOKUP(F$currentRow, CATALOGOS!`$A`$2:`$B`$50, 2, 0), `"XX`") & `"-`" & WEEKNUM(C$currentRow, 2) & `"-`" & TEXT(ROW()-1, `"000`"))"
        
        $currentRow++
        $added++
    }
    
    if ($added -gt 0) {
        $workbook.Save()
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
