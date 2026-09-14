"""Standard-library checks for this repository's Markdown documentation."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def headings(text: str) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    in_fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
        if in_fence:
            continue
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            slug = re.sub(r"[^\w\- ]", "", match[1].lower()).replace(" ", "-")
            count = counts.get(slug, 0)
            counts[slug] = count + 1
            anchors.add(f"{slug}-{count}" if count else slug)
    return anchors


def main() -> int:
    files = [*sorted(ROOT.glob("*.md")), *sorted((ROOT / "docs").rglob("*.md")),
             *sorted((ROOT / "prototypes").glob("*.md"))]
    errors: list[str] = []
    links = blocks = 0
    for path in files:
        text = path.read_text()
        label = path.relative_to(ROOT)
        fence: str | None = None
        code: list[str] = []
        start = 0
        prose: list[str] = []
        for number, line in enumerate(text.splitlines(), 1):
            if line.startswith("```"):
                if fence is None:
                    fence = line[3:].strip()
                    code, start = [], number + 1
                else:
                    if fence == "python":
                        blocks += 1
                        try:
                            ast.parse("\n".join(code), filename=str(label))
                        except SyntaxError as exc:
                            errors.append(f"{label}:{start}: Python syntax: {exc.msg}")
                    fence = None
                continue
            if fence is not None:
                code.append(line)
            else:
                prose.append(line)
        if fence is not None:
            errors.append(f"{label}: unclosed code fence")
        for match in LINK.finditer("\n".join(prose)):
            target = match[1].strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("//"):
                continue
            links += 1
            dest = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if not dest.exists():
                errors.append(f"{label}: missing link target {target}")
            elif parsed.fragment and dest.suffix == ".md":
                if unquote(parsed.fragment) not in headings(dest.read_text()):
                    errors.append(f"{label}: missing heading {target}")
    for error in errors:
        print(error, file=sys.stderr)
    print(f"Checked {len(files)} Markdown files, {links} local links, "
          f"{blocks} Python examples: {len(errors)} errors.")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
