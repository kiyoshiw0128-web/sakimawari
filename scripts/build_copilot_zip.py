#!/usr/bin/env python3
"""Microsoft 365 Copilot (Agent Builder) 用のスキル ZIP を作る。

ZIP の直下に SKILL.md を置き、references/ を一緒に入れる。
出力: dist/sakimawari.zip
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "sakimawari"
OUT = ROOT / "dist" / "sakimawari.zip"


def collect(skill_dir: Path) -> list[Path]:
    files = [skill_dir / "SKILL.md"]
    files += sorted(p for p in (skill_dir / "references").rglob("*") if p.is_file())
    return [f for f in files if f.name != ".DS_Store"]


def build(skill_dir: Path = SKILL, out: Path = OUT) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in collect(skill_dir):
            z.write(f, f.relative_to(skill_dir).as_posix())
    return out


if __name__ == "__main__":
    path = build()
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
    print(f"作成しました: {path}")
    print(f"ファイル数: {len(names)}（上限 350）、SKILL.md が直下にある: {'SKILL.md' in names}")
    sys.exit(0)
