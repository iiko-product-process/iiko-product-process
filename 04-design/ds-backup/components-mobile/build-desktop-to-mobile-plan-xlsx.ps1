# build-desktop-to-mobile-plan-xlsx.ps1
# Собирает Excel-версию плана "desktop-to-mobile-plan.xlsx" из markdown-файла
# "desktop-to-mobile-plan.md". Запуск: & 'путь\build-desktop-to-mobile-plan-xlsx.ps1'
# Если план в md поменяется — просто перезапустить скрипт, Excel пересоберётся.

$ErrorActionPreference = 'Stop'

$base = Split-Path -Parent $MyInvocation.MyCommand.Path
$md   = Join-Path $base 'desktop-to-mobile-plan.md'
$out  = Join-Path $base 'desktop-to-mobile-plan.xlsx'
if ($env:PLAN_OUT) { $out = $env:PLAN_OUT }   # переопределение цели (например, для предпросмотра)

if (-not (Test-Path -LiteralPath $md)) { throw "Не найден файл: $md" }

# ---------- вспомогательные функции разбора ----------

function Split-RowCells([string]$line) {
  $t = $line.Trim().Trim('|')
  $parts = $t -split '\|'
  $res = @()
  foreach ($p in $parts) { $res += $p.Trim() }
  return ,$res
}

function Test-SepCells($cells) {
  $cells = @($cells)
  foreach ($c in $cells) { if ($c -notmatch '^:?-{2,}:?$') { return $false } }
  return $true
}

function Get-FirstTable($body) {
  $body = @($body)
  $rows = New-Object System.Collections.ArrayList
  $cur  = New-Object System.Collections.ArrayList
  foreach ($ln in $body) {
    $t = ''
    if ($null -ne $ln) { $t = ([string]$ln).Trim() }
    if ($t.StartsWith('|')) {
      $cells = Split-RowCells $t
      if (Test-SepCells $cells) { continue }
      [void]$cur.Add($cells)
    } elseif ($cur.Count -gt 0) {
      [void]$rows.Add($cur.ToArray())
      $cur = New-Object System.Collections.ArrayList
    }
  }
  if ($cur.Count -gt 0) { [void]$rows.Add($cur.ToArray()) }
  if ($rows.Count -eq 0) { return $null }
  return ,$rows[0]
}

function CleanText([string]$s) {
  if ($null -eq $s) { return '' }
  return ($s -replace '\*\*', '')
}

function Get-Bullets($body) {
  $body = @($body)
  $res = New-Object System.Collections.ArrayList
  foreach ($ln in $body) {
    $s = ''
    if ($null -ne $ln) { $s = ([string]$ln).Trim() }
    if ($s.StartsWith('- ')) { [void]$res.Add($s.Substring(2).Trim()) }
  }
  return $res.ToArray()
}

function Bgr([string]$hex) {
  $r = [Convert]::ToInt32($hex.Substring(0, 2), 16)
  $g = [Convert]::ToInt32($hex.Substring(2, 2), 16)
  $b = [Convert]::ToInt32($hex.Substring(4, 2), 16)
  return ($b * 65536) + ($g * 256) + $r
}

function Add-MergedRow($ws, [int]$row, [string]$text, [string]$fillHex, [bool]$bold, [int]$cpl) {
  $ws.Cells.Item($row, 1).Value2 = $text
  $rng = $ws.Range($ws.Cells.Item($row, 1), $ws.Cells.Item($row, 3))
  $rng.Merge()
  $rng.WrapText = $true
  $rng.VerticalAlignment = -4160
  if ($bold) { $rng.Font.Bold = $true }
  if ($fillHex -ne '') { $rng.Interior.Color = (Bgr $fillHex) }
  if ($cpl -gt 0) {
    $l = [Math]::Ceiling([Math]::Max(1, $text.Length) / $cpl)
    if ($l -lt 1) { $l = 1 }
    $ws.Rows.Item($row).RowHeight = [Math]::Max(16, $l * 14.5)
  }
  return ($row + 1)
}

function Add-TwoColTable($ws, [int]$row, $table) {
  if ($null -eq $table) { return $row }
  $table = @($table)
  for ($i = 0; $i -lt $table.Count; $i++) {
    $cells = @($table[$i])
    if ($cells.Count -lt 2) { continue }
    $ws.Cells.Item($row, 1).Value2 = (CleanText $cells[0])
    $ws.Cells.Item($row, 2).Value2 = (CleanText $cells[1])
    $rr = $ws.Range($ws.Cells.Item($row, 1), $ws.Cells.Item($row, 2))
    $rr.WrapText = $true
    $rr.VerticalAlignment = -4160
    $rr.Borders.LineStyle = 1
    $rr.Borders.Color = (Bgr 'BFBFBF')
    if ($i -eq 0) {
      $rr.Font.Bold = $true
      $rr.Interior.Color = (Bgr 'DCE6F1')
    }
    $l1 = [Math]::Ceiling([Math]::Max(1, (CleanText $cells[0]).Length) / 28)
    $l2 = [Math]::Ceiling([Math]::Max(1, (CleanText $cells[1]).Length) / 65)
    $lm = [Math]::Max($l1, $l2)
    $ws.Rows.Item($row).RowHeight = [Math]::Max(16, $lm * 14.5)
    $row++
  }
  return $row
}

# ---------- разбор markdown ----------

$lines  = Get-Content -LiteralPath $md -Encoding UTF8
$blocks = New-Object System.Collections.ArrayList
$curTitle = ''; $curLevel = 0; $curBody = New-Object System.Collections.ArrayList

foreach ($ln in $lines) {
  $m = [regex]::Match(([string]$ln), '^(#{1,4})\s+(.*)$')
  if ($m.Success) {
    [void]$blocks.Add([pscustomobject]@{ Level = $curLevel; Title = $curTitle; Body = $curBody.ToArray() })
    $curLevel = $m.Groups[1].Value.Length
    $curTitle = $m.Groups[2].Value.Trim()
    $curBody  = New-Object System.Collections.ArrayList
  } else {
    [void]$curBody.Add(([string]$ln))
  }
}
[void]$blocks.Add([pscustomobject]@{ Level = $curLevel; Title = $curTitle; Body = $curBody.ToArray() })

function Get-Block([string]$prefix) {
  foreach ($b in $blocks) { if ($b.Title.StartsWith($prefix)) { return $b } }
  return $null
}

# группы компонентов (A/B/C/D)
$groups = New-Object System.Collections.ArrayList
foreach ($b in $blocks) {
  if ($b.Level -eq 3 -and $b.Title -match '^[A-D]\.') {
    $tab = Get-FirstTable $b.Body
    if ($null -eq $tab) { continue }
    $tm = [regex]::Match($b.Title, '\[(.*?)\]')
    $type = ''
    if ($tm.Success) { $type = $tm.Groups[1].Value }
    $label = ($b.Title -split ' — ')[0].Trim()
    $rows = @()
    for ($i = 1; $i -lt $tab.Count; $i++) { $rows += , $tab[$i] }
    [void]$groups.Add([pscustomobject]@{ Label = $label; Type = $type; Rows = $rows })
  }
}

# справка
$blkFrames = Get-Block 'Рамки'
$frames = @()
if ($null -ne $blkFrames) { $frames = @(Get-Bullets $blkFrames.Body) }

$blkGroups = Get-Block 'Группы изменений'
$groupsTable = $null
if ($null -ne $blkGroups) { $groupsTable = Get-FirstTable $blkGroups.Body }

$blkTokens = Get-Block 'Привязка к токенам'
$tokensTable = $null
if ($null -ne $blkTokens) { $tokensTable = Get-FirstTable $blkTokens.Body }

$blkMobDone = Get-Block '_mob-компоненты'
$mobDoneTable = $null
if ($null -ne $blkMobDone) { $mobDoneTable = Get-FirstTable $blkMobDone.Body }

$blkBp = Get-Block 'Брейкпоинты'
$breakpoints = @()
if ($null -ne $blkBp) { $breakpoints = @(Get-Bullets $blkBp.Body) }

$blkPr = Get-Block 'Общие принципы'
$principles = @()
if ($null -ne $blkPr) { $principles = @(Get-Bullets $blkPr.Body) }

$blkSrc = Get-Block 'Источники'
$sources = @()
if ($null -ne $blkSrc) { $sources = @(Get-Bullets $blkSrc.Body) }

$blkTot = Get-Block 'Итоги'
$totals = @()
if ($null -ne $blkTot) { $totals = @(Get-Bullets $blkTot.Body) }

$blkQ = Get-Block 'Открытые вопросы'
$questions = @()
if ($null -ne $blkQ) {
  $res = New-Object System.Collections.ArrayList
  foreach ($ln in @($blkQ.Body)) {
    $s = ([string]$ln).Trim()
    $m = [regex]::Match($s, '^\d+\.\s+(.*)$')
    if ($m.Success) { [void]$res.Add($m.Groups[1].Value.Trim()) }
  }
  $questions = @($res.ToArray())
}

# расшифровки групп (таблица "Группы изменений") — для строк-заголовков на листе «План»
$groupMeaning = @{}
if ($null -ne $groupsTable) {
  $gt = @($groupsTable)
  for ($i = 1; $i -lt $gt.Count; $i++) {
    $cells = @($gt[$i])
    if ($cells.Count -lt 2) { continue }
    $k = CleanText $cells[0]
    if ($k -ne '') { $groupMeaning[$k] = (CleanText $cells[1]) }
  }
}

# короткие названия групп изменений для листа «План» и легенды (без букв A–D)
$gshort = @{ 'A' = 'Размеры'; 'B' = 'Размеры + поведение'; 'C' = 'Структура'; 'D' = 'Нет' }

# статусы «Статус _mob»: значения выпадающего списка + расшифровка + цвет (раздел на листе «Справка»)
# вместо «нет» показываем пустое поле
$mobStatuses = New-Object System.Collections.ArrayList
[void]$mobStatuses.Add(@('Собран', 'Собран по рекомендациям плана', 'FFE699'))
[void]$mobStatuses.Add(@('Проверен', 'Проверен на макетах', 'BDD7EE'))
[void]$mobStatuses.Add(@('Готов', 'Привязан к токенам', 'C6E0B4'))

# спринты для выпадающего списка в колонке «Спринт» (пустое поле — спринт ещё не назначен)
$sprints = @('14.09 по 04.10', '05.10 по 18.10', '19.10 по 01.11')

# ---------- сборка Excel ----------

$missing = [System.Reflection.Missing]::Value
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

try {
  $wb = $excel.Workbooks.Add()
  while ($wb.Worksheets.Count -gt 1) { $wb.Worksheets.Item($wb.Worksheets.Count).Delete() }

  $wsPlan = $wb.Worksheets.Item(1)
  $wsPlan.Name = 'План'
  $wsRef = $wb.Worksheets.Add($missing, $wsPlan)
  $wsRef.Name = 'Справка'
  $wsSum = $wb.Worksheets.Add($missing, $wsRef)
  $wsSum.Name = 'Итоги и вопросы'

  # --- лист "План" ---
  $headers = @('№', 'Компонент', 'Группа изменений', 'Что меняется на мобиле', 'Как в Material Design / Angular Material', 'Статус _mob', 'Спринт', 'Комментарий', 'Привязка к токенам')
  for ($c = 0; $c -lt $headers.Count; $c++) { $wsPlan.Cells.Item(1, $c + 1).Value2 = $headers[$c] }

  $fills = @{ 'A' = 'E2EFDA'; 'B' = 'FFF2CC'; 'C' = 'FBE5D6'; 'D' = 'EDEDED' }

  # строки данных (для выпадающего списка «Статус _mob») и строки-заголовки групп
  $valRows = New-Object System.Collections.ArrayList
  $grpRows = New-Object System.Collections.ArrayList

  $r = 2; $n = 0
  foreach ($g in $groups) {
    $gk = $g.Label.Substring(0, 1)
    $fillHex = $fills[$gk]

    # строка-заголовок группы: просто заголовок — белый фон, выравнивание слева
    $htext = $gshort[$gk]
    if ($groupMeaning.ContainsKey($g.Label)) {
      $m = $groupMeaning[$g.Label]
      if ($m.Length -gt 1) { $m = $m.Substring(0, 1).ToLower() + $m.Substring(1) }
      $htext = $htext + ' — ' + $m
    }
    $hrng = $wsPlan.Range($wsPlan.Cells.Item($r, 1), $wsPlan.Cells.Item($r, 9))
    $hrng.Merge()
    $wsPlan.Cells.Item($r, 1).Value2 = $htext
    $hrng.Font.Bold = $true
    $hrng.Interior.Pattern = -4142
    $hrng.VerticalAlignment = -4108
    $hrng.HorizontalAlignment = -4131
    $wsPlan.Rows.Item($r).RowHeight = 22
    [void]$grpRows.Add($r)
    $r++

    foreach ($row in $g.Rows) {
      if ($null -eq $row -or @($row).Count -lt 5) { continue }
      $n++
      $name = CleanText $row[0]
      $mob  = CleanText $row[1]
      if ($mob -eq 'нет') { $mob = '' }   # пустое поле вместо «нет»
      $what = CleanText $row[2]
      $mat  = CleanText $row[3]
      $tok  = CleanText $row[4]
      $wsPlan.Cells.Item($r, 1).Value2 = [double]$n
      $wsPlan.Cells.Item($r, 2).Value2 = $name
      $wsPlan.Cells.Item($r, 3).Value2 = $gshort[$gk]
      $wsPlan.Cells.Item($r, 4).Value2 = $what
      $wsPlan.Cells.Item($r, 5).Value2 = $mat
      $wsPlan.Cells.Item($r, 6).Value2 = $mob
      $wsPlan.Cells.Item($r, 9).Value2 = $tok
      [void]$valRows.Add($r)

      $wsPlan.Range($wsPlan.Cells.Item($r, 1), $wsPlan.Cells.Item($r, 6)).Interior.Color = (Bgr $fillHex)
      $r++
    }
  }
  $last = $r - 1

  $hdr = $wsPlan.Range('A1:I1')
  $hdr.Font.Bold = $true
  $hdr.Font.Color = 16777215
  $hdr.Interior.Color = (Bgr '1F4E79')
  $hdr.HorizontalAlignment = -4108
  $hdr.VerticalAlignment = -4108
  $hdr.WrapText = $true
  $wsPlan.Rows.Item(1).RowHeight = 30

  $data = $wsPlan.Range("A2:I$last")
  $data.VerticalAlignment = -4160
  $data.WrapText = $true

  $grid = $wsPlan.Range("A1:I$last")
  $grid.Borders.LineStyle = 1
  $grid.Borders.Color = (Bgr 'D9D9D9')

  $wsPlan.Columns.Item(1).ColumnWidth = 5
  $wsPlan.Columns.Item(2).ColumnWidth = 24
  $wsPlan.Columns.Item(3).ColumnWidth = 20
  $wsPlan.Columns.Item(4).ColumnWidth = 66
  $wsPlan.Columns.Item(5).ColumnWidth = 58
  $wsPlan.Columns.Item(6).ColumnWidth = 12
  $wsPlan.Columns.Item(7).ColumnWidth = 16
  $wsPlan.Columns.Item(8).ColumnWidth = 28
  $wsPlan.Columns.Item(9).ColumnWidth = 34

  $wsPlan.Columns.Item(1).HorizontalAlignment = -4108

  # заголовки групп — по левому краю (перекрываем выравнивание колонки №)
  foreach ($gr in $grpRows) { $wsPlan.Range($wsPlan.Cells.Item($gr, 1), $wsPlan.Cells.Item($gr, 9)).HorizontalAlignment = -4131 }

  $wsPlan.Range("A2:I$last").Rows.AutoFit() | Out-Null
  $wsPlan.Range("A1:I$last").AutoFilter() | Out-Null

  # закрепляем «№» и «Компонент» (нужно видимое развёрнутое окно — иначе Excel ограничивает раздел одной колонкой)
  $wsPlan.Activate()
  $excel.Visible = $true
  $excel.WindowState = -4137
  $excel.ActiveWindow.SplitRow = 1
  $excel.ActiveWindow.SplitColumn = 2
  $excel.ActiveWindow.FreezePanes = $true
  $excel.Visible = $false

  try {
    $wsPlan.PageSetup.Orientation = 2
    $wsPlan.PageSetup.Zoom = $false
    $wsPlan.PageSetup.FitToPagesWide = 1
    $wsPlan.PageSetup.FitToPagesTall = $false
  } catch { }

  # --- лист "Справка" ---
  $wsRef.Columns.Item(1).ColumnWidth = 30
  $wsRef.Columns.Item(2).ColumnWidth = 70
  $wsRef.Columns.Item(3).ColumnWidth = 50

  $r = 1
  $r = Add-MergedRow $wsRef $r 'План перевода компонентов ДС: Desktop → Mobile' '' $true 0
  $wsRef.Cells.Item(1, 1).Font.Size = 14

  $r++
  $r = Add-MergedRow $wsRef $r 'Рамки' 'D9E2F3' $true 0
  foreach ($b in $frames) { $r = Add-MergedRow $wsRef $r ('- ' + (CleanText $b)) '' $false 150 }

  $r++
  $r = Add-MergedRow $wsRef $r 'Группы изменений' 'D9E2F3' $true 0
  # в легенде — те же короткие названия, что и в колонке «Группа изменений»
  $groupsTableShow = New-Object System.Collections.ArrayList
  $gt = @($groupsTable)
  for ($gi = 0; $gi -lt $gt.Count; $gi++) {
    $cells = @($gt[$gi])
    if ($cells.Count -lt 2) { continue }
    $nm = CleanText $cells[0]
    if ($gi -gt 0 -and $nm.Length -gt 0) {
      $ck = $nm.Substring(0, 1)
      if ($gshort.ContainsKey($ck)) { $nm = $gshort[$ck] }
    }
    [void]$groupsTableShow.Add(@($nm, (CleanText $cells[1])))
  }
  $r = Add-TwoColTable $wsRef $r $groupsTableShow

  $r++
  $r = Add-MergedRow $wsRef $r 'Привязка к токенам' 'D9E2F3' $true 0
  $r = Add-TwoColTable $wsRef $r $tokensTable

  $r++
  $r = Add-MergedRow $wsRef $r '_mob: уже собрано (Figma)' 'D9E2F3' $true 0
  $r = Add-TwoColTable $wsRef $r $mobDoneTable

  $r++
  $r = Add-MergedRow $wsRef $r 'Статусы _mob (значения выпадающего списка)' 'D9E2F3' $true 0
  $stRows = New-Object System.Collections.ArrayList
  [void]$stRows.Add(@('Статус', 'Что означает'))
  foreach ($st in $mobStatuses) { [void]$stRows.Add($st) }
  $stFirst = $r + 1
  $r = Add-TwoColTable $wsRef $r $stRows
  $stLast = $stFirst + $mobStatuses.Count - 1

  # легенда: ячейки статусов — теми же цветами, что и в таблице
  for ($si = 0; $si -lt $mobStatuses.Count; $si++) {
    $wsRef.Cells.Item($stFirst + $si, 1).Interior.Color = (Bgr $mobStatuses[$si][2])
  }
  $r = Add-MergedRow $wsRef $r 'Пустое поле — мобильной версии пока нет' '' $false 150

  # выпадающий список «Статус _mob» на листе «План» — значения берём из раздела выше
  $stFormula = '=Справка!$A$' + $stFirst + ':$A$' + $stLast
  foreach ($vr in $valRows) {
    $vcell = $wsPlan.Cells.Item($vr, 6)
    $vcell.Validation.Delete()
    $vcell.Validation.Add(3, 1, 1, $stFormula)
    $vcell.Validation.IgnoreBlank = $true
    $vcell.Validation.InCellDropdown = $true
  }

  # спринты — значения выпадающего списка для колонки «Спринт»
  $r++
  $r = Add-MergedRow $wsRef $r 'Спринты (значения выпадающего списка)' 'D9E2F3' $true 0
  $spFirst = $r
  foreach ($sp in $sprints) { $wsRef.Cells.Item($r, 1).Value2 = $sp; $r++ }
  $spLast = $spFirst + $sprints.Count - 1
  $r = Add-MergedRow $wsRef $r 'Пустое поле — спринт ещё не назначен' '' $false 150

  # выпадающий список «Спринт» на листе «План»
  $spFormula = '=Справка!$A$' + $spFirst + ':$A$' + $spLast
  foreach ($vr in $valRows) {
    $vcell = $wsPlan.Cells.Item($vr, 7)
    $vcell.Validation.Delete()
    $vcell.Validation.Add(3, 1, 1, $spFormula)
    $vcell.Validation.IgnoreBlank = $true
    $vcell.Validation.InCellDropdown = $true
  }

  # условное форматирование: цвет ячейки «Статус _mob» зависит от значения
  # (формулу задаём при активной ячейке F3 — иначе Excel пересчитывает ссылки от другой активной ячейки)
  $wsPlan.Activate()
  $wsPlan.Cells.Item(3, 6).Activate()
  $cfRange = $wsPlan.Range('F3:F' + $last)
  $cfRange.FormatConditions.Delete()
  foreach ($st in $mobStatuses) {
    $cf = $cfRange.FormatConditions.Add(2, $missing, '=$F3="' + $st[0] + '"')
    $cf.Interior.Color = (Bgr $st[2])
  }
  # пустое поле — белый фон
  $cf0 = $cfRange.FormatConditions.Add(2, $missing, '=$F3=""')
  $cf0.Interior.Color = (Bgr 'FFFFFF')

  $r++
  $r = Add-MergedRow $wsRef $r 'Брейкпоинты' 'D9E2F3' $true 0
  foreach ($b in $breakpoints) { $r = Add-MergedRow $wsRef $r ('- ' + (CleanText $b)) '' $false 150 }

  $r++
  $r = Add-MergedRow $wsRef $r 'Общие принципы мобильного слоя' 'D9E2F3' $true 0
  foreach ($b in $principles) { $r = Add-MergedRow $wsRef $r ('- ' + (CleanText $b)) '' $false 150 }

  $r++
  $r = Add-MergedRow $wsRef $r 'Источники' 'D9E2F3' $true 0
  foreach ($b in $sources) { $r = Add-MergedRow $wsRef $r ('- ' + (CleanText $b)) '' $false 150 }

  # --- лист "Итоги и вопросы" ---
  $wsSum.Columns.Item(1).ColumnWidth = 8
  $wsSum.Columns.Item(2).ColumnWidth = 85
  $wsSum.Columns.Item(3).ColumnWidth = 55

  $r = 1
  $r = Add-MergedRow $wsSum $r 'Итоги' 'D9E2F3' $true 0
  foreach ($b in $totals) { $r = Add-MergedRow $wsSum $r ('- ' + (CleanText $b)) '' $false 145 }

  $r++
  $r = Add-MergedRow $wsSum $r 'Открытые вопросы (решить до нарезки задач)' 'D9E2F3' $true 0
  $qi = 0
  foreach ($b in $questions) { $qi++; $r = Add-MergedRow $wsSum $r ("$qi. " + (CleanText $b)) '' $false 145 }

  # вид листа «План» при открытии: закреплены «№» и «Компонент», прокрутка — с начала таблицы
  $wsPlan.Activate()
  $wsPlan.Cells.Item(3, 3).Activate()
  try { $excel.ActiveWindow.ScrollColumn = 3; $excel.ActiveWindow.ScrollRow = 2 } catch { }

  # --- сохранение ---
  $wb.SaveAs($out, 51)
  $wb.Close($false)
  Write-Output ("OK: " + $out)
  Write-Output ("SIZE: " + (Get-Item -LiteralPath $out).Length)
}
finally {
  try { $excel.Quit() } catch { }
  try { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) } catch { }
  [GC]::Collect()
  [GC]::WaitForPendingFinalizers()
}
