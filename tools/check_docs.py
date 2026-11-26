"""Check the repo's Markdown docs: relative links, heading anchors, table columns and tabs.

Usage (from the repo root):  python -X utf8 tools/check_docs.py [extra.md ...]
Checks tracked and untracked non-ignored *.md files plus local STATUS.md / AGENTS.md when present.
Exit code 1 if any problem is found.
"""
import os
import re
import subprocess
import sys
import unicodedata
from urllib.parse import unquote


def slug(text: str) -> str:
    """GitHub-style heading anchor."""
    text = re.sub(r"[`*_]", "", unicodedata.normalize("NFC", text.strip().lower()))
    out = []
    for ch in text:
        cat = unicodedata.category(ch)
        if ch == " ":
            out.append("-")
        elif ch == "-" or cat[0] in "LN" or cat == "Mn":
            out.append(ch)
    return "".join(out)


def strip_code_blocks(lines: list[str]) -> list[tuple[int, str]]:
    kept, in_code = [], False
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            kept.append((i, line))
    return kept


def anchors(path: str) -> set[str]:
    found, counts = set(), {}
    for _, line in strip_code_blocks(open(path, encoding="utf-8").read().split("\n")):
        m = re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
        if m:
            s = slug(m.group(1))
            n = counts.get(s, 0)
            counts[s] = n + 1
            found.add(s if n == 0 else f"{s}-{n}")
    return found


def check(path: str) -> list[str]:
    problems = []
    lines = strip_code_blocks(open(path, encoding="utf-8").read().split("\n"))
    header_cols = None
    for i, line in lines:
        if "\t" in line:
            problems.append(f"{path}:{i}: tab character")
        if line.startswith("|"):
            cols = len(re.findall(r"(?<!\\)\|", re.sub(r"`[^`]*`", "", line)))
            if header_cols is None:
                header_cols = cols
            elif cols != header_cols:
                problems.append(f"{path}:{i}: table row has {cols} pipes, header has {header_cols}")
        else:
            header_cols = None
        for m in re.finditer(r"\]\((?:<([^>]+)>|([^)\s]+))\)", re.sub(r"`[^`]*`", "", line)):
            target = m.group(1) or m.group(2)
            if re.match(r"^[a-z]+:", target):
                continue
            file_part, _, anchor = target.partition("#")
            dest = os.path.normpath(os.path.join(os.path.dirname(path), unquote(file_part))) if file_part else path
            if not os.path.exists(dest):
                problems.append(f"{path}:{i}: missing file {target}")
            elif anchor and dest.endswith(".md") and not re.fullmatch(r"L\d+(-L\d+)?", anchor):
                if unicodedata.normalize("NFC", unquote(anchor)) not in anchors(dest):
                    problems.append(f"{path}:{i}: missing anchor {target}")
    return problems


def main() -> int:
    candidates = subprocess.check_output(["git", "ls-files", "-z", "--cached", "--others",
                                          "--exclude-standard", "--", "*.md"])
    files = [os.fsdecode(name) for name in candidates.split(b"\0") if name and os.path.isfile(os.fsdecode(name))]
    files += [f for f in ("STATUS.md", "AGENTS.md") if os.path.exists(f)] + sys.argv[1:]
    files = list(dict.fromkeys(files))
    problems = [p for f in files for p in check(f)]
    for p in problems:
        print(p)
    print(f"checked {len(files)} Markdown files: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
