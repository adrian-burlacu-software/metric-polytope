"""Rough text recovery from dvips PostScript (no Ghostscript available). Lossy for math symbols.

Strings (...) are glyph runs; '<num> a' and '<num> <num> y' are absolute moves (word / line break);
'p' is an inter-word space; other single-letter procedures are kerns inside a word.
Usage: python scripts/tools/dvips_text.py file.ps > file.txt
"""
import re
import sys

LIG = {0o013: "ff", 0o014: "fi", 0o015: "fl", 0o016: "ffi", 0o017: "ffl", 0o050: "(", 0o051: ")", 0o134: "\\"}

src = open(sys.argv[1], "rb").read().decode("latin-1")
body = src[src.find("%%Page:"):]
tok = re.compile(r"\((?:[^()\\]|\\.)*\)|[A-Za-z]+|-?\d+")
out = []
for t in tok.findall(body):
    if t.startswith("("):
        s = t[1:-1]
        s = re.sub(r"\\([0-7]{3})", lambda m: LIG.get(int(m.group(1), 8), "?"), s)
        s = re.sub(r"\\(.)", r"\1", s)
        out.append(s)
    elif t == "y":
        out.append("\n")
    elif t in ("a", "p"):
        out.append(" ")
    elif t == "bop":
        out.append("\n\n=== PAGE ===\n")
print(re.sub(r"[ ]+", " ", "".join(out)))
