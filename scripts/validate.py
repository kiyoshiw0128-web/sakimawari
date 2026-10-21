#!/usr/bin/env python3
"""スキルとエージェント指示文の整合を確かめる。

確かめること:
- SKILL.md の先頭に、name と description だけがある（Microsoft の資料の条件）
- SKILL.md が 20,000 字未満、エージェント指示文が 8,000 字以内
- SKILL.md が挙げた references のファイルが、すべて存在する
- 型の一覧（SKILL.md の表と、指示文の一覧）の名前が一致する
- ZIP を作れて、SKILL.md が直下にあり、ファイル数・深さが上限内
- evals/truth.json の引用が、テスト資料の中に実在する
終了コード 0 なら、すべて通った。
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_copilot_zip  # noqa: E402

errors: list[str] = []


def check(cond: object, msg: str) -> None:
    if not cond:
        errors.append(msg)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"[\s「」『』]", "", s)


skill_dir = ROOT / "skills" / "sakimawari"
skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")

# 1. フロントマター
m = re.match(r"---\n(.*?)\n---\n", skill_md, re.S)
check(m is not None, "SKILL.md の先頭に、フロントマターがありません")
if m:
    keys = [line.split(":", 1)[0] for line in m.group(1).split("\n") if re.match(r"^[A-Za-z_-]+:", line)]
    check(keys == ["name", "description"], f"フロントマターは name と description だけにしてください: {keys}")
    name = re.search(r"^name:\s*(\S+)", m.group(1), re.M)
    check(name and name.group(1) == skill_dir.name, "name がフォルダ名と一致しません")
    body_chars = len(skill_md)
    check(body_chars < 20000, f"SKILL.md が長すぎます（{body_chars} 字、上限 20,000 字未満）")

# 2. 指示文
inst_path = ROOT / "copilot" / "エージェント指示文.md"
inst = inst_path.read_text(encoding="utf-8")
check(len(inst) <= 8000, f"エージェント指示文が長すぎます（{len(inst)} 字、上限 8,000 字）")

# 3. references の実在
refs = set(re.findall(r"`(references/[A-Za-z0-9_.-]+\.md)`", skill_md))
for r in sorted(refs):
    check((skill_dir / r).exists(), f"SKILL.md が挙げた {r} がありません")
for p in (skill_dir / "references").glob("*.md"):
    check(p.stat().st_size > 0, f"{p.name} が空です")

# 4. 型の一覧の一致
skill_types = {int(a): b.strip() for a, b in re.findall(r"^\| (\d+) \| ([^|]+) \|", skill_md, re.M)}
inst_section = re.search(r"# 穴の型\n(.*?)\n# ", inst, re.S)
if inst_section:
    inst_types = {int(a): b.strip() for a, b in re.findall(r"^(\d+)\. ([^:：]+)[:：]", inst_section.group(1), re.M)}
    check(skill_types == inst_types, f"型の一覧が、SKILL.md と指示文で食い違っています: {set(skill_types.items()) ^ set(inst_types.items())}")
check(len(skill_types) >= 11, f"SKILL.md の型の表が読み取れません（{len(skill_types)} 件）")

# 5. ZIP
zip_path = build_copilot_zip.build(out=ROOT / "dist" / "sakimawari.zip")
with zipfile.ZipFile(zip_path) as z:
    names = [n for n in z.namelist() if not n.endswith("/")]
    check("SKILL.md" in z.namelist(), "ZIP の直下に SKILL.md がありません")
    check(len(names) <= 350, f"ZIP のファイル数が上限を超えています（{len(names)}）")
    check(max(n.count("/") for n in names) <= 3, "ZIP のディレクトリの深さが上限（3）を超えています")
    check(zip_path.stat().st_size <= 50 * 1024 * 1024, "ZIP が 50 MB を超えています")

# 6. 評価データの整合
truth_path = ROOT / "evals" / "truth.json"
if truth_path.exists():
    truth = json.loads(truth_path.read_text(encoding="utf-8"))
    for case, info in truth.items():
        doc_path = ROOT / "evals" / "cases" / f"{case}.md"
        if not doc_path.exists():
            errors.append(f"evals/cases/{case}.md がありません")
            continue
        doc = norm(doc_path.read_text(encoding="utf-8"))
        anchors = [a for h in info["holes"] for a in h["anchors"]] + [a for g in info["decoys"] for a in g]
        for a in anchors:
            check(norm(a) in doc, f"{case}: 正解データの引用が資料にありません: {a[:30]}")

# 7. ライセンス
license_path = ROOT / "LICENSE"
check(license_path.exists(), "LICENSE がありません")
if license_path.exists() and "<著作権者の名前>" in license_path.read_text(encoding="utf-8"):
    print("注意: LICENSE の「<著作権者の名前>」を、公開前に書き換えてください。")

if errors:
    print("検証に失敗しました:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"検証に成功しました（SKILL.md {len(skill_md)} 字、指示文 {len(inst)} 字、型 {len(skill_types)} 種類、ZIP のファイル {len(names)} 個）")
