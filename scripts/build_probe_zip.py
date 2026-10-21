#!/usr/bin/env python3
"""Copilot がスキルのどのファイルを読むかを調べるための、確認用 ZIP を作る。

各ファイルに「読んだ印」の決まりを入れる。出力の最後の行に、読んだファイルの印が出る。
出力: dist/sakimawari_probe.zip（普通の点検には使わない）
"""
from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "sakimawari"
OUT = ROOT / "dist" / "sakimawari_probe.zip"

MARKS = {
    "hole-types.md": "H",
    "audience.md": "A",
    "output-format.md": "O",
    "diagram-patterns.md": "D",
    "lenses.md": "L",
    "sources.md": "R",
}


def build() -> Path:
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "sakimawari"
        shutil.copytree(SKILL, work)

        skill_md = work / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        text = text.replace("description: ", "description: （読み込み確認用）", 1)
        marker = "# sakimawari（先回り）\n"
        if text.count(marker) != 1:
            raise SystemExit("SKILL.md の見出しが見つかりません")
        notice = (
            "\n## 読んだ印（確認用。実際の点検では使わない）\n\n"
            "出力の一番最後に、「読んだ印: 」で始まる行を1行だけ書く。"
            "そこには、内容を実際に読んだファイルの印だけを、並べて書く。"
            "このファイル（SKILL.md）を読んだときは「S」。"
            "各ファイルの先頭にも、同じ決まりがある。読んでいないファイルの印は、書かない。\n"
        )
        skill_md.write_text(text.replace(marker, marker + notice, 1), encoding="utf-8")

        for name, mark in MARKS.items():
            path = work / "references" / name
            if not path.exists():
                continue
            lines = path.read_text(encoding="utf-8").split("\n")
            lines = [
                lines[0],
                "",
                f"【読んだ印】このファイルを読んだときは、出力の最後の「読んだ印」の行に「{mark}」を足す。",
                "",
            ] + lines[1:]
            path.write_text("\n".join(lines), encoding="utf-8")

        OUT.parent.mkdir(parents=True, exist_ok=True)
        if OUT.exists():
            OUT.unlink()
        with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(skill_md, "SKILL.md")
            for p in sorted((work / "references").rglob("*")):
                if p.is_file():
                    z.write(p, p.relative_to(work).as_posix())
    return OUT


if __name__ == "__main__":
    print(f"作成しました: {build()}")
