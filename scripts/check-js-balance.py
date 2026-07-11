#!/usr/bin/env python3
from pathlib import Path

t = Path(__file__).resolve().parent.parent.joinpath("index.html").read_text(encoding="utf-8")
start = t.rfind("<script>")
end = t.rfind("</script>")
js = t[start + 8 : end]

p = 0
b = 0
line = 1
in_s = None
esc = False
in_line = False
in_block = False
first_neg_p = None
first_neg_b = None

i = 0
while i < len(js):
    ch = js[i]
    if ch == "\n":
        line += 1
        in_line = False
        i += 1
        continue
    if in_line:
        i += 1
        continue
    if in_block:
        if ch == "*" and i + 1 < len(js) and js[i + 1] == "/":
            in_block = False
            i += 2
            continue
        i += 1
        continue
    if in_s:
        if esc:
            esc = False
            i += 1
            continue
        if ch == "\\":
            esc = True
            i += 1
            continue
        if ch == in_s:
            in_s = None
        i += 1
        continue
    if ch in ('"', "'", "`"):
        in_s = ch
        i += 1
        continue
    if ch == "/" and i + 1 < len(js) and js[i + 1] == "/":
        in_line = True
        i += 2
        continue
    if ch == "/" and i + 1 < len(js) and js[i + 1] == "*":
        in_block = True
        i += 2
        continue
    if ch == "(":
        p += 1
    elif ch == ")":
        p -= 1
        if p < 0 and first_neg_p is None:
            first_neg_p = (line, js[max(0, i - 60) : i + 60])
    if ch == "{":
        b += 1
    elif ch == "}":
        b -= 1
        if b < 0 and first_neg_b is None:
            first_neg_b = (line, js[max(0, i - 60) : i + 60])
    i += 1

print("final paren", p, "brace", b)
print("first_neg_p", first_neg_p[0] if first_neg_p else None)
if first_neg_p:
    print(repr(first_neg_p[1]))
print("first_neg_b", first_neg_b[0] if first_neg_b else None)
