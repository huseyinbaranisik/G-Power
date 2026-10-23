param([string]$CsvPath, [string]$ShotDir, [string]$OutJson, [string]$Only = '')
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public static class W {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr p, EnumProc f, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc f, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetDlgCtrlID(IntPtr h);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr SendMessage(IntPtr h, int m, IntPtr w, string l);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr SendMessage(IntPtr h, int m, IntPtr w, StringBuilder l);
  [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, int m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, int m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern IntPtr GetParent(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int cx, int cy, uint f);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint f);
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  public static List<IntPtr> Children(IntPtr p) { var r = new List<IntPtr>(); EnumChildWindows(p, (h,l)=>{ r.Add(h); return true; }, IntPtr.Zero); return r; }
  public static List<IntPtr> TopWindows(uint pid) { var r = new List<IntPtr>(); EnumWindows((h,l)=>{ uint q; GetWindowThreadProcessId(h, out q); if (q==pid && IsWindowVisible(h)) r.Add(h); return true; }, IntPtr.Zero); return r; }
  public static string Cls(IntPtr h) { var s = new StringBuilder(256); GetClassName(h, s, 256); return s.ToString(); }
  public static string Text(IntPtr h) { int n = (int)SendMessage(h, 0x000E, IntPtr.Zero, IntPtr.Zero); var s = new StringBuilder(n+2); SendMessage(h, 0x000D, (IntPtr)(n+1), s); return s.ToString(); }
}
"@

$WM_SETTEXT=0x000C; $BM_CLICK=0x00F5; $CB_GETCOUNT=0x0146; $CB_GETCURSEL=0x0147; $CB_SETCURSEL=0x014E; $CB_GETLBTEXT=0x0148; $CB_GETLBTEXTLEN=0x0149; $WM_COMMAND=0x0111; $CBN_SELCHANGE=1; $WM_CLOSE=0x0010

[W]::SetProcessDPIAware() | Out-Null   # screen coordinates in physical pixels, so captures are not cropped
$p = Get-Process GPowerNT | Select-Object -First 1
$main = $p.MainWindowHandle
[W]::SetWindowPos($main, [IntPtr]::Zero, 40, 40, 0, 0, 0x0001 -bor 0x0004) | Out-Null   # move on-screen, keep size

function Ctl([int]$id, [string]$cls) {
  foreach ($h in [W]::Children($main)) { if ([W]::GetDlgCtrlID($h) -eq $id -and [W]::Cls($h) -eq $cls) { return $h } }
  throw "control $id/$cls not found"
}
function ComboItems($h) {
  $n = [int][W]::SendMessage($h, $CB_GETCOUNT, [IntPtr]::Zero, [IntPtr]::Zero)
  0..($n-1) | ForEach-Object { $len = [int][W]::SendMessage($h, $CB_GETLBTEXTLEN, [IntPtr]$_, [IntPtr]::Zero); $sb = New-Object System.Text.StringBuilder ($len+2); [W]::SendMessage($h, $CB_GETLBTEXT, [IntPtr]$_, $sb) | Out-Null; $sb.ToString() }
}
function SetMode([string]$prefix) {
  $cb = Ctl 1002 'ComboBox'
  $items = @(ComboItems $cb)
  $idx = [array]::FindIndex([string[]]$items, [Predicate[string]]{ param($s) $s.StartsWith($prefix) })
  if ($idx -lt 0) { throw "mode $prefix not in: $($items -join ' | ')" }
  if ([int][W]::SendMessage($cb, $CB_GETCURSEL, [IntPtr]::Zero, [IntPtr]::Zero) -ne $idx) {
    [W]::SendMessage($cb, $CB_SETCURSEL, [IntPtr]$idx, [IntPtr]::Zero) | Out-Null
    $wparam = [IntPtr](($CBN_SELCHANGE -shl 16) -bor 1002)
    [W]::SendMessage([W]::GetParent($cb), $WM_COMMAND, $wparam, $cb) | Out-Null
    Start-Sleep -Milliseconds 500
  }
}
function Label([int]$id) { [W]::Text((Ctl $id 'Static')) }
function Shot([string]$path, [IntPtr[]]$wins) {
  # union of window rects, captured from screen so popups on top are included
  $x0=99999;$y0=99999;$x1=-99999;$y1=-99999
  foreach ($w in $wins) { $rc = New-Object W+RECT; [W]::GetWindowRect($w, [ref]$rc) | Out-Null; $x0=[Math]::Min($x0,$rc.L);$y0=[Math]::Min($y0,$rc.T);$x1=[Math]::Max($x1,$rc.R);$y1=[Math]::Max($y1,$rc.B) }
  $bmp = New-Object System.Drawing.Bitmap ($x1-$x0), ($y1-$y0)
  $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($x0, $y0, 0, 0, $bmp.Size); $g.Dispose()
  $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
}

$rows = Import-Csv $CsvPath
if ($Only) { $rows = $rows | Where-Object { ($Only -split ',') -contains $_.id } }
$results = @()
foreach ($row in $rows) {
  if ($row.mode -eq 'a-priori') { SetMode 'A priori' } else { SetMode 'Post hoc' }
  $inputs = @{}
  foreach ($id in 1020..1023) {   # labels 1004..1007 pair with edits 1020..1023
    $lbl = Label ($id - 16)
    $key = switch -Regex ($lbl) { '^Effect' { 'w'; break } '^Power' { 'power'; break } '^Total' { 'n'; break } '^Df' { 'df'; break } 'err prob' { 'alpha'; break } default { $lbl } }
    $inputs[$key] = (Ctl $id 'Edit')
  }
  $want = @{ 'w' = $row.w; 'alpha' = $row.alpha; 'df' = $row.df }
  if ($row.mode -eq 'a-priori') { $want['power'] = $row.power } else { $want['n'] = $row.n_total }
  foreach ($k in $want.Keys) {
    if (-not $inputs.ContainsKey($k)) { throw "$($row.id): no input labelled '$k' (have: $($inputs.Keys -join ', '))" }
    [W]::SendMessage($inputs[$k], $WM_SETTEXT, [IntPtr]::Zero, [string]$want[$k]) | Out-Null
  }
  foreach ($id in 1050..1053) { [W]::SendMessage((Ctl $id 'Edit'), $WM_SETTEXT, [IntPtr]::Zero, '?') | Out-Null }   # clear stale outputs
  [W]::SetForegroundWindow($main) | Out-Null
  $before = @([W]::TopWindows([uint32]$p.Id))
  [W]::PostMessage((Ctl 1009 'Button'), $BM_CLICK, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null
  # wait until a result lands in the first output box or a dialog opens (large N can take a while)
  $deadline = (Get-Date).AddSeconds(120)
  do {
    Start-Sleep -Milliseconds 500
    $popups = @([W]::TopWindows([uint32]$p.Id) | Where-Object { $before -notcontains $_ })
    $done = $popups.Count -gt 0 -or [W]::Text((Ctl 1050 'Edit')) -ne '?'
  } until ($done -or (Get-Date) -gt $deadline)
  Start-Sleep -Milliseconds 700   # let the plot and remaining boxes repaint before capture
  $popups = @([W]::TopWindows([uint32]$p.Id) | Where-Object { $before -notcontains $_ })
  $popupText = @()
  foreach ($pp in $popups) {
    $popupText += ([W]::Text($pp) + ': ' + (([W]::Children($pp) | ForEach-Object { [W]::Text($_) } | Where-Object { $_ }) -join ' / '))
  }
  # read back what the input boxes hold after Calculate (G*Power may rewrite them)
  $echo = @{}; foreach ($k in $inputs.Keys) { $echo[$k] = [W]::Text($inputs[$k]) }
  $out = @{}; foreach ($id in 1050..1053) {   # labels 1060..1063 pair with edits 1050..1053
    $lbl = Label ($id + 10)
    $key = switch -Regex ($lbl) { '^Noncentrality' { 'ncp'; break } '^Critical' { 'critical_chi2'; break } '^Total' { 'n_total'; break } '^Actual' { 'actual_power'; break } '^Power' { 'power'; break } default { $lbl } }
    $out[$key] = [W]::Text((Ctl $id 'Edit'))
  }
  Shot (Join-Path $ShotDir "$($row.id).png") (@($main) + $popups)
  foreach ($pp in $popups) { [W]::PostMessage($pp, $WM_CLOSE, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null }
  if ($popups) { Start-Sleep -Milliseconds 500 }
  $results += [pscustomobject]@{ id = $row.id; mode = $row.mode; inputs_after = $echo; outputs = $out; popups = $popupText }
  Write-Host "$($row.id) -> $(($out.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join '; ') $(if ($popupText) { '| POPUP: ' + ($popupText -join ' || ') })"
}
$results | ConvertTo-Json -Depth 5 | Out-File -Encoding utf8 $OutJson
