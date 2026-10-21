#!/usr/bin/env python3
"""実行（runs/<名前>/）ごとの採点の結果を、1行ずつ並べる。

使い方:
    python3 score.py <名前>          # 先に採点して、_scores.json を作る
    python3 compare.py <名前1> <名前2> ...
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name: str) -> list[dict]:
    path = HERE / "runs" / name / "_scores.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    return [r for r in rows if not r.get("error")]


def summarize(rows: list[dict], truth: dict) -> dict:
    holes = sum(r["holes"] for r in rows)
    main = sum(len(r["found_main"]) for r in rows)
    found = sum(len(r["found_main"]) + len(r["found_minor"]) for r in rows)
    clean = [r for r in rows if not truth[r["case"]]["holes"]]
    return {
        "runs": len(rows),
        "main": f"{main}/{holes}",
        "found": f"{found}/{holes}",
        "q_per_run": round(sum(r["n_q"] for r in rows) / max(len(rows), 1), 1),
        "clean_high": sum(r["sev"]["高"] for r in clean),
        "bad_quotes": sum(len(r["bad_quotes"]) for r in rows),
        "fig_over_10": sum(r["figure_over10"] for r in rows),
        "bold": sum(1 for r in rows if r.get("bold")),
        "fix_concrete": f"{sum(r.get('fix_concrete', 0) for r in rows)}/{sum(r.get('fix_total', 0) for r in rows)}",
        "viewpoint_kinds": round(sum(r.get("vp_kinds", 0) for r in rows) / max(len(rows), 1), 1),
    }


def main(names: list[str]) -> None:
    truth = json.loads((HERE / "truth.json").read_text(encoding="utf-8"))
    header = ["実行", "回", "本体の穴", "全穴", "Q/回", "穴なし資料の高", "引用NG", "図>10", "太字", "案が文", "視点の種類/回"]
    print("\t".join(header))
    for name in names:
        s = summarize(load(name), truth)
        print("\t".join([name, str(s["runs"]), s["main"], s["found"], str(s["q_per_run"]), str(s["clean_high"]),
                         str(s["bad_quotes"]), str(s["fig_over_10"]), str(s["bold"]), s["fix_concrete"],
                         str(s["viewpoint_kinds"])]))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1:])
