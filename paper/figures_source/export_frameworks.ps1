Add-Type -AssemblyName System.Drawing
$ErrorActionPreference = 'Stop'
$outDir = Join-Path $PSScriptRoot '../figures'
if (Test-Path -LiteralPath $outDir -PathType Leaf) {
  if ((Get-Item -LiteralPath $outDir).Length -ne 0) { throw 'figures is a nonempty file' }
  Remove-Item -LiteralPath $outDir
}
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$script:blue = '#29475F'
$script:svg = [System.Collections.Generic.List[string]]::new()
function N($v) { $v.ToString('0.###',[Globalization.CultureInfo]::InvariantCulture) }
function Brush($c) { [Drawing.SolidBrush]::new([Drawing.ColorTranslator]::FromHtml($c)) }
function StartFigure($name,$w,$h) {
  $script:name=$name; $script:w=$w; $script:h=$h
  $script:svg.Clear()
  $script:svg.Add('<svg xmlns="http://www.w3.org/2000/svg" width="260mm" height="'+(N (260*$h/$w))+'mm" viewBox="0 0 '+$w+' '+$h+'"><rect width="100%" height="100%" fill="white"/>')
  $script:bmp=[Drawing.Bitmap]::new($w*3,$h*3)
  $script:bmp.SetResolution(350,350)
  $script:g=[Drawing.Graphics]::FromImage($script:bmp)
  $script:g.Clear([Drawing.Color]::White)
  $script:g.ScaleTransform(3,3)
  $script:g.SmoothingMode='AntiAlias'
}
function ShapePath($p,$fill,$stroke,$sw=1.5) {
  $pts=$p.PathPoints; $types=$p.PathTypes; $d=''; $i=0
  while($i -lt $pts.Length) {
    $t=$types[$i] -band 7; $pt=$pts[$i]
    if($t -eq 0) { $d+='M'+(N $pt.X)+','+(N $pt.Y)+' '; $i++ }
    elseif($t -eq 1) { $d+='L'+(N $pt.X)+','+(N $pt.Y)+' '; if($types[$i] -band 128){$d+='Z '};$i++ }
    elseif($t -eq 3) { $d+='C'; for($j=0;$j -lt 3;$j++){ $pt=$pts[$i+$j];$d+=(N $pt.X)+','+(N $pt.Y)+' ' };if($types[$i+2] -band 128){$d+='Z '};$i+=3 }
    else { throw 'unsupported path' }
  }
  $script:svg.Add('<path d="'+$d+'" fill="'+$fill+'" stroke="'+$stroke+'" stroke-width="'+$sw+'"/>')
  if($fill -ne 'none'){ $b=Brush $fill;$script:g.FillPath($b,$p);$b.Dispose() }
  if($stroke -ne 'none'){ $pen=[Drawing.Pen]::new([Drawing.ColorTranslator]::FromHtml($stroke),$sw);$script:g.DrawPath($pen,$p);$pen.Dispose() }
  $p.Dispose()
}
function Text($x,$y,$text,$size=17,$color='#29475F',$align='center') {
  $lines=$text -split '\|';$lineY=$y
  foreach($line in $lines) {
    $p=[Drawing.Drawing2D.GraphicsPath]::new()
    $fam=[Drawing.FontFamily]::new('Microsoft YaHei')
    $p.AddString($line,$fam,0,$size,[Drawing.PointF]::new(0,0),[Drawing.StringFormat]::GenericTypographic)
    $r=$p.GetBounds();$dx=$x-$r.X
    if($align -eq 'center'){$dx-=$r.Width/2}
    $m=[Drawing.Drawing2D.Matrix]::new();$m.Translate($dx,$lineY-$r.Y);$p.Transform($m)
    ShapePath $p $color 'none';$fam.Dispose();$m.Dispose();$lineY+=$size*1.55
  }
}
function Rect($x,$y,$w,$h,$fill='#EDF3F8',$stroke='#29475F',$sw=1.5) {
  $p=[Drawing.Drawing2D.GraphicsPath]::new();$p.AddRectangle([Drawing.RectangleF]::new($x,$y,$w,$h));ShapePath $p $fill $stroke $sw
}
function Box($x,$y,$w,$h,$text,$kind='normal',$size=17) {
  $fill=switch($kind){'gray'{'#F2F3F5'} 'accent'{'#E6F2F1'} default{'#EDF3F8'}}
  Rect $x $y $w $h $fill
  $count=($text -split '\|').Length
  Text ($x+$w/2) ($y+($h-($count-1)*$size*1.55-$size)/2) $text $size
}
function Arrow($coords,$dash=$false) {
  $ps=$coords -split ' ';$points=@();foreach($pair in $ps){$v=$pair -split ',';$points+=,[Drawing.PointF]::new([float]$v[0],[float]$v[1])}
  $script:svg.Add('<polyline points="'+$coords+'" fill="none" stroke="#29475F" stroke-width="1.7"'+$(if($dash){' stroke-dasharray="6 4"'}else{''})+'/>')
  $pen=[Drawing.Pen]::new([Drawing.ColorTranslator]::FromHtml('#29475F'),1.7);if($dash){$pen.DashStyle='Dash'};$script:g.DrawLines($pen,[Drawing.PointF[]]$points);$pen.Dispose()
  $a=$points[-2];$b=$points[-1];$ang=[Math]::Atan2($b.Y-$a.Y,$b.X-$a.X)
  $p=[Drawing.Drawing2D.GraphicsPath]::new();$p.AddPolygon([Drawing.PointF[]]@($b,[Drawing.PointF]::new($b.X-8*[Math]::Cos($ang)-3.5*[Math]::Sin($ang),$b.Y-8*[Math]::Sin($ang)+3.5*[Math]::Cos($ang)),[Drawing.PointF]::new($b.X-8*[Math]::Cos($ang)+3.5*[Math]::Sin($ang),$b.Y-8*[Math]::Sin($ang)-3.5*[Math]::Cos($ang))))
  ShapePath $p '#29475F' 'none'
}
function EndFigure {
  $script:svg.Add('</svg>');[IO.File]::WriteAllText((Join-Path $outDir ($script:name+'.svg')),($script:svg -join "`n"),[Text.UTF8Encoding]::new($false))
  $script:bmp.Save((Join-Path $outDir ($script:name+'.png')),[Drawing.Imaging.ImageFormat]::Png);$script:g.Dispose();$script:bmp.Dispose()
}

StartFigure 'framework_A' 1200 760
Text 600 24 '整体求解框架' 25
Text 600 68 '统一流程按 P1 / P2 / P3 分别运行并评价' 18
Rect 20 112 1160 244 '#FFFFFF' '#B8C7D2' 1
Text 45 125 '种子阶段：基线起始候选与多种子候选' 18 '#29475F' 'left'
Box 40 185 160 100 '输入|计算图 G、硬件配置|问题场景' 'gray' 16
Box 230 200 150 70 '图特征预计算'
Box 420 165 260 62 'Baseline 基线|种子阶段起始候选' 'normal' 16
Box 420 250 260 86 'Multi-seed 四类候选|balanced / affinity / critical / pipe|粒度 4 / 12 / 32' 'normal' 15
Box 720 202 165 68 'HEFT-style|核分配'
Box 920 202 225 68 '种子候选逐个官方评价|严格目标比较' 'gray' 16
Arrow '200,235 230,235';Arrow '380,235 398,235 398,196 420,196';Arrow '398,235 398,293 420,293'
Arrow '680,196 700,196 700,236 720,236';Arrow '680,293 700,293 700,236';Arrow '885,236 920,236'
Text 550 368 'fine-grain=2：候选变体；Baseline 采用中间粒度的 balanced 粗化' 15
Rect 20 402 1160 228 '#FFFFFF' '#B8C7D2' 1
Text 45 417 'VNS 邻域搜索' 18 '#29475F' 'left'
Box 40 465 160 82 '当前解|incumbent /|best-so-far' 'gray' 16
Box 230 465 200 82 '生成邻域候选池|最多 48 个合法、唯一、|未评价候选' 'normal' 15
Box 460 473 140 66 '启发式排序'
Box 630 473 130 66 'Top-K 筛选|最多 3 个' 'normal' 16
Box 790 473 140 66 '官方评价' 'gray'
Box 960 458 190 96 '严格下降比较|改善：更新当前解|否则：保持当前解' 'accent' 16
Arrow '1032,270 1032,390 120,390 120,465'
Arrow '200,506 230,506';Arrow '430,506 460,506';Arrow '600,506 630,506';Arrow '760,506 790,506';Arrow '930,506 960,506'
Box 710 573 350 42 'adaptive 控制：邻域选择与停止' 'gray' 16
Arrow '1055,554 1055,573';Arrow '710,594 330,594 330,547' $true
Text 485 568 '继续搜索' 15
Arrow '885,615 885,648 600,648 600,676'
Text 770 629 '停止' 15
Box 40 676 330 62 'P1 最终方案及对应官方评价结果' 'gray' 16
Box 435 676 330 62 'P2 最终方案及对应官方评价结果' 'gray' 16
Box 830 676 330 62 'P3 最终方案及对应官方评价结果' 'gray' 16
Arrow '600,648 205,648 205,676';Arrow '885,648 995,648 995,676'
EndFigure

StartFigure 'framework_B' 1200 880
Text 600 24 '多种子与 VNS 两阶段搜索流程' 25
Text 600 70 '输入：图特征、场景与核数、求解配置接口' 17
Rect 20 112 1160 250 '#FFFFFF' '#B8C7D2' 1
Text 42 128 '第一阶段：种子候选逐个评价' 19 '#29475F' 'left'
Box 40 177 275 64 'Baseline 基线候选|先评价的起始候选' 'normal' 16
Box 40 262 275 78 'Multi-seed 四类多粒度候选|balanced / affinity / critical / pipe|fine-grain=2 为候选变体' 'normal' 15
Box 350 225 170 68 'HEFT-style|核分配'
Box 555 225 135 68 'digest 去重' 'normal' 16
Box 725 217 185 84 '种子候选|逐个官方评价' 'gray' 17
Box 945 207 210 104 '严格目标比较|（完工时间，新增拷贝量）|更新当前解与|best-so-far' 'accent' 15
Arrow '315,209 332,209 332,259 350,259';Arrow '315,301 332,301 332,259';Arrow '520,259 555,259';Arrow '690,259 725,259';Arrow '910,259 945,259'
Rect 20 394 860 458 '#FFFFFF' '#B8C7D2' 1
Text 42 412 '第二阶段：VNS 邻域候选池与 Top-K 评价' 19 '#29475F' 'left'
Box 40 468 150 78 '选择邻域|以种子阶段当前解|作为起点' 'normal' 15
Box 220 468 245 78 '最多 48 个候选|合法、唯一、未评价' 'normal' 17
Box 495 468 160 78 '启发式估计|与排序'
Box 685 468 170 78 'Top-K = 3|官方评价' 'gray' 17
Arrow '1050,311 1050,377 115,377 115,468'
Arrow '190,507 220,507';Arrow '465,507 495,507';Arrow '655,507 685,507'
Box 580 584 275 74 '官方目标是否严格改善？|（完工时间，新增拷贝量）' 'accent' 16
Arrow '770,546 770,584'
Box 310 584 220 56 '接受并更新 best-so-far' 'gray' 16
Box 310 676 220 56 '保持当前 best-so-far' 'gray' 16
Arrow '580,612 530,612';Text 557 584 '是' 15
Arrow '717,658 717,704 530,704';Text 688 678 '否' 15
Box 40 611 220 90 '更新邻域统计|adaptive 选择与停止|接受准则始终为严格下降' 'gray' 15
Arrow '310,612 280,612 280,637 260,637';Arrow '310,704 280,704 280,675 260,675'
Arrow '150,611 150,576 115,576 115,546' $true;Text 207 565 '继续' 15
Box 40 770 490 55 '达到停止条件：输出 best-so-far' 'gray' 17
Arrow '150,701 150,770';Text 185 734 '停止' 15
Rect 910 394 270 458 '#F7F9FB' '#B8C7D2' 1
Text 1045 413 '八个邻域动作' 19
$items=@('N1  重块优先换核','N2  两块核归属交换','N3  相邻无直接依赖块重排','N4  相邻块合并','N5  按工作量近半拆分','N6  边界节点右移','N7  高通信量连接块对|      优先同核','N8  关键块优先换核')
$yy=462;foreach($item in $items){Text 927 $yy $item 15 '#29475F' 'left';$yy+= $(if($item.Contains('|')){65}else{43})}
Text 680 789 '候选池与 Top-K 仅用于 VNS' 15
EndFigure

StartFigure 'framework_D' 1200 760
Text 600 24 'P3 共享只读L2 Cache 访问机制' 25
Rect 20 76 1160 78 '#F2F3F5' '#B8C7D2' 1
Text 600 90 'P2 基础执行语义：按核任务及跨核 COPY_IN / COPY_OUT，由官方执行规则构造' 17
Text 600 124 'P3：所有核心共享的只读L2 Cache；仅 COPY_IN 查询共享只读L2 Cache' 17
Box 40 216 155 82 '计算核 / 执行端|按核任务' 'gray' 17
Box 235 216 190 82 'COPY_IN|读取请求'
Box 470 209 260 96 '共享只读L2 Cache 查询|数据是否命中？' 'normal' 17
Arrow '195,257 235,257';Arrow '425,257 470,257'
Text 600 177 '容量由正式配置给定，非求解变量' 16
Box 790 185 230 84 '命中：缓存读取路径|使用对应缓存带宽' 'accent' 17
Box 790 326 230 70 '未命中：DDR 读取' 'gray' 17
Arrow '730,241 760,241 760,227 790,227';Arrow '600,305 600,361 790,361'
Text 746 207 '命中' 15;Text 643 333 '未命中' 15
Box 1055 216 110 160 '读取完成|执行事件' 'gray' 16
Arrow '1020,227 1055,227';Arrow '1020,361 1055,361'
Text 905 289 '命中不刷新 FIFO 顺序' 16
Box 745 456 300 64 'DDR 读取完成后|按 FIFO 规则更新缓存状态' 'normal' 17
Box 390 456 300 64 '容量不足时 FIFO 淘汰|FIFO 为状态更新 / 替换规则' 'normal' 16
Arrow '905,396 905,456';Arrow '745,488 690,488'
Arrow '390,488 350,488 350,410 510,410 510,305' $true
Text 465 430 '供后续请求查询的状态' 15
Box 40 352 200 76 'COPY_OUT|沿用 P2 基础执行语义' 'gray' 15
Arrow '115,298 115,352'
Box 745 602 420 66 '官方评价器|完工时间、新增拷贝量、缓存命中率' 'gray' 17
Arrow '1110,376 1110,602'
Arrow '240,390 285,390 285,635 745,635'
Text 600 705 'Cache Hit Rate（缓存命中率）为分析 / 评价指标，非优化目标' 18
EndFigure
Write-Output 'Generated framework_A/B/D.svg and .png'
