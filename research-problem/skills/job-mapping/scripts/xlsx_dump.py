#!/usr/bin/env python3
"""Выгрузка .xlsx в текст без openpyxl (для Google Sheets-экспортов и любых файлов).

Использование:
    python3 xlsx_dump.py файл.xlsx [вывод.txt]
Без второго аргумента печатает в stdout; листы разделяются заголовком,
строки — ячейки через ' | '.

ВАЖНО (проверено 01.10.2026 на шаблонах интервью): сначала удаляются
самозакрывающиеся пустые ячейки (<c .../>). Иначе наивный regex
<c ...>(.*?)</c> «проглатывает» следующие ячейки, и текст вопросов
превращается в числа (индексы sharedStrings).
"""
import html as h
import re
import sys
import zipfile


def dump(path):
    z = zipfile.ZipFile(path)

    # shared strings
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        xml = z.read('xl/sharedStrings.xml').decode('utf-8', 'replace')
        for si in re.findall(r'<si>(.*?)</si>', xml, re.S):
            ts = re.findall(r'<t[^>]*>(.*?)</t>', si, re.S)
            ss.append(h.unescape(''.join(ts)))

    # листы: имя -> файл
    wb = z.read('xl/workbook.xml').decode('utf-8', 'replace')
    sheets = re.findall(r'<sheet[^>]*name="([^"]+)"[^>]*r:id="(rId\d+)"', wb)
    rels = z.read('xl/_rels/workbook.xml.rels').decode('utf-8', 'replace')
    relmap = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels))

    def col_num(ref):
        m = re.match(r'([A-Z]+)(\d+)', ref)
        col = 0
        for ch in m.group(1):
            col = col * 26 + (ord(ch) - 64)
        return col, int(m.group(2))

    def cell_val(t, body):
        if t == 's':  # индекс в sharedStrings
            vm = re.search(r'<v>(\d+)</v>', body)
            return ss[int(vm.group(1))] if vm else ''
        if t == 'inlineStr':
            return h.unescape(''.join(re.findall(r'<t[^>]*>(.*?)</t>', body, re.S)))
        vm = re.search(r'<v>(.*?)</v>', body, re.S)
        return h.unescape(vm.group(1)) if vm else ''

    out = []
    for name, rid in sheets:
        fname = 'xl/' + relmap.get(rid, '')
        if fname not in z.namelist():
            out.append(f'\n########## ЛИСТ: {name} — файл не найден ({fname}) ##########\n')
            continue
        sh = z.read(fname).decode('utf-8', 'replace')
        sh = re.sub(r'<c [^>]*?/>', '', sh, flags=re.S)  # КЛЮЧЕВОЙ ФИКС
        rows = {}
        for cm in re.finditer(r'<c r="([A-Z]+\d+)"(?:[^>]*?t="([^"]*)")?[^>]*>(.*?)</c>', sh, re.S):
            ref, t, body = cm.group(1), cm.group(2), cm.group(3)
            v = cell_val(t, body)
            if v.strip():
                c, r = col_num(ref)
                rows.setdefault(r, {})[c] = v.strip()
        out.append(f'\n########## ЛИСТ: {name} ##########\n')
        for r in sorted(rows):
            cells = rows[r]
            out.append(' | '.join(cells.get(c, '') for c in sorted(cells)))
    return '\n'.join(out)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    text = dump(sys.argv[1])
    if len(sys.argv) > 2:
        open(sys.argv[2], 'w', encoding='utf-8').write(text)
        print(f'OK: {sys.argv[2]} ({len(text)} символов)')
    else:
        print(text)


if __name__ == '__main__':
    main()
