const fs = require('fs');
const path = require('path');
const D = require('docx');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, WidthType, BorderStyle, SectionType, ShadingType,
  PositionalTab, PositionalTabAlignment, PositionalTabRelativeTo, PositionalTabLeader,
} = D;

const SRC = path.join(__dirname, 'TANET2026_論文初稿.md');
const OUT = path.join(__dirname, 'TANET2026_結合形成性評量之程式設計適性學習輔助系統.docx');

const CN = '標楷體', EN = 'Times New Roman';
const FONT = { ascii: EN, hAnsi: EN, eastAsia: CN, cs: EN };
const COL_W = 4394;            // 7.75cm in twips
const PLACEHOLDER_COLOR = 'C00000';

// ---- inline parsing: **bold** and 【placeholder】 ----
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|【[^】]*】)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(mk(text.slice(last, m.index), base));
    const tok = m[0];
    if (tok.startsWith('**')) out.push(mk(tok.slice(2, -2), { ...base, bold: true }));
    else out.push(mk(tok, { ...base, bold: true, color: PLACEHOLDER_COLOR }));
    last = m.index + tok.length;
  }
  if (last < text.length) out.push(mk(text.slice(last), base));
  if (!out.length) out.push(mk('', base));
  return out;
}
function mk(t, o) {
  return new TextRun({ text: t, font: FONT, size: o.size || 20, bold: !!o.bold,
    italics: !!o.italics, color: o.color });
}
const P = (text, opts = {}) => new Paragraph({
  alignment: opts.align || AlignmentType.BOTH,
  spacing: { line: 240, lineRule: 'auto', before: opts.before || 0, after: opts.after || 60 },
  indent: opts.indent,
  children: runs(text, opts),
});

// ---- table builder ----
function buildTable(rows) {
  const nCol = rows[0].length;
  const w = Math.floor(COL_W / nCol);
  const widths = Array(nCol).fill(w);
  widths[nCol - 1] = COL_W - w * (nCol - 1);
  const border = { style: BorderStyle.SINGLE, size: 4, color: '000000' };
  const borders = { top: border, bottom: border, left: border, right: border };
  return new Table({
    columnWidths: widths,
    width: { size: COL_W, type: WidthType.DXA },
    rows: rows.map((cells, ri) => new TableRow({
      tableHeader: ri === 0,
      children: cells.map((c, ci) => new TableCell({
        width: { size: widths[ci], type: WidthType.DXA },
        borders,
        shading: ri === 0 ? { type: ShadingType.CLEAR, fill: 'EFEFEF' } : undefined,
        margins: { top: 30, bottom: 30, left: 60, right: 60 },
        children: [new Paragraph({
          alignment: ci === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
          spacing: { line: 240, after: 0 },
          children: runs(c, { size: 18, bold: ri === 0 }),
        })],
      })),
    })),
  });
}

// ---- markdown walk ----
const lines = fs.readFileSync(SRC, 'utf8').split(/\r?\n/);
const head = [], body = [];
let i = 0, inHead = true;

// front matter until first '---'
for (; i < lines.length; i++) {
  const l = lines[i].trim();
  if (l === '---') { i++; break; }
  if (!l) continue;
  if (l.startsWith('# ')) {
    head.push(new Paragraph({ alignment: AlignmentType.CENTER,
      spacing: { after: 160, line: 260 }, children: runs(l.slice(2), { size: 32, bold: true }) }));
  } else if (l.startsWith('**') && l.endsWith('**')) {
    head.push(new Paragraph({ alignment: AlignmentType.CENTER,
      spacing: { after: 160, line: 260 }, children: runs(l.slice(2, -2), { size: 28, bold: true }) }));
  } else {
    head.push(new Paragraph({ alignment: AlignmentType.CENTER,
      spacing: { after: 40, line: 240 }, children: runs(l, { size: 24, bold: true }) }));
  }
}

function isTableRow(s) { return /^\s*\|.*\|\s*$/.test(s); }
function cellsOf(s) { return s.trim().replace(/^\||\|$/g, '').split('|').map(x => x.trim()); }

for (; i < lines.length; i++) {
  let l = lines[i];
  const t = l.trim();
  if (!t) continue;
  if (t === '---') continue;

  // tables
  if (isTableRow(t)) {
    const rows = [];
    while (i < lines.length && isTableRow(lines[i].trim())) {
      const c = cellsOf(lines[i]);
      if (!c.every(x => /^:?-{2,}:?$/.test(x))) rows.push(c);
      i++;
    }
    i--;
    body.push(buildTable(rows));
    body.push(new Paragraph({ spacing: { after: 120 }, children: [mk('', {})] }));
    continue;
  }

  // equations
  if (t.startsWith('%%EQ%%')) {
    const raw = t.slice(6);
    const [expr, tag] = raw.split('\t');
    const kids = runs(expr, { size: 20, italics: false });
    if (tag) kids.push(new TextRun({ children: [new PositionalTab({
      alignment: PositionalTabAlignment.RIGHT, relativeTo: PositionalTabRelativeTo.MARGIN,
      leader: PositionalTabLeader.NONE })] }), mk(tag, {}));
    body.push(new Paragraph({ alignment: AlignmentType.LEFT,
      indent: { left: 340 }, spacing: { line: 240, after: 40 }, children: kids }));
    continue;
  }

  // headings
  if (t.startsWith('### ')) {
    body.push(new Paragraph({ alignment: AlignmentType.LEFT,
      spacing: { before: 180, after: 120, line: 240 },
      children: runs(t.slice(4), { size: 22, bold: true }) }));
    continue;
  }
  if (t.startsWith('## ')) {
    body.push(new Paragraph({ alignment: AlignmentType.LEFT,
      spacing: { before: 220, after: 140, line: 240 },
      children: runs(t.slice(3), { size: 24, bold: true }) }));
    continue;
  }

  // blockquote = 圖片位置 / 待補提示
  if (t.startsWith('> ')) {
    body.push(new Paragraph({ alignment: AlignmentType.LEFT,
      spacing: { before: 100, after: 140, line: 240 },
      shading: { type: ShadingType.CLEAR, fill: 'FFF2CC' },
      children: runs(t.slice(2), { size: 18, color: PLACEHOLDER_COLOR, bold: true }) }));
    continue;
  }

  // 表 X caption (bold standalone line) — 10pt bold, centered, above table
  if (/^\*\*(表|圖)\s*\d+/.test(t) && t.endsWith('**')) {
    body.push(new Paragraph({ alignment: AlignmentType.CENTER,
      spacing: { before: 140, after: 60, line: 240 },
      children: runs(t.slice(2, -2), { size: 20, bold: true }) }));
    continue;
  }

  // bullets
  let m;
  if ((m = t.match(/^[-*]\s+(.*)$/))) {
    body.push(new Paragraph({ alignment: AlignmentType.BOTH, bullet: { level: 0 },
      spacing: { line: 240, after: 40 }, children: runs(m[1], { size: 20 }) }));
    continue;
  }
  if ((m = t.match(/^(\d+)\.\s+(.*)$/))) {
    body.push(new Paragraph({ alignment: AlignmentType.BOTH,
      indent: { left: 340, hanging: 340 }, spacing: { line: 240, after: 40 },
      children: runs(`${m[1]}. ${m[2]}`, { size: 20 }) }));
    continue;
  }

  // reference entries [n]
  if (/^\[\d+\]/.test(t)) {
    body.push(new Paragraph({ alignment: AlignmentType.BOTH,
      indent: { left: 340, hanging: 340 }, spacing: { line: 240, after: 40 },
      children: runs(t.replace(/\*/g, ''), { size: 20 }) }));
    continue;
  }

  // 關鍵詞 / Keywords line
  body.push(P(t, { size: 20, indent: { firstLine: 400 } }));
}

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 20 } } } },
  sections: [
    { properties: { page: { size: { width: 11906, height: 16838 },
        margin: { top: 1418, right: 1418, bottom: 1418, left: 1418 } } },
      children: head },
    { properties: { type: SectionType.CONTINUOUS,
        page: { size: { width: 11906, height: 16838 },
          margin: { top: 1418, right: 1418, bottom: 1418, left: 1418 } },
        column: { count: 2, space: 283, equalWidth: true } },
      children: body },
  ],
});

Packer.toBuffer(doc).then(b => { fs.writeFileSync(OUT, b); console.log('written', OUT, b.length); });
