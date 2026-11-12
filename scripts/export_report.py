from pathlib import Path
import markdown
p=Path(__file__).resolve().parents[1]
s=(p/'报告.md').read_text(encoding='utf-8-sig')
body=markdown.markdown(s,extensions=['tables','fenced_code'])
css='''@page {size: A4; margin: 18mm 16mm;} body {font-family: "Microsoft YaHei",sans-serif; font-size: 10pt; line-height: 1.6; color:#1d2732;} h1 {font-size:18pt; line-height:1.35;} h2 {font-size:14pt; border-bottom:1px solid #aac2d5; padding-bottom:3px; margin-top:20px; break-after:avoid;} h3 {font-size:11pt; break-after:avoid;} p {margin: 7px 0;} table {border-collapse: collapse; width:100%; font-size:8.1pt; margin:10px 0; break-inside:avoid;} th,td {border:1px solid #aab4bd; padding:4px; text-align:left;} th {background:#e5eef5;} img {display:block; max-width:95%; max-height:420px; margin:auto;} p:has(img) {break-inside:avoid; text-align:center;} a {color:#155f91;} code {font-family:Consolas,monospace;}'''
(p/'report-preview.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>SQLite 课程报告</title><style>'+css+'</style><body>'+body+'</body></html>',encoding='utf-8')
