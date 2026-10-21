"""Run the skill on each test case in a clean headless claude process.

usage: python3 run_iter.py <iter_name> <skill_dir> <instructions_file> [--model sonnet] [--reps 2]
The system prompt mimics the Copilot setup: agent instructions + skill files.
"""
from __future__ import annotations

import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
name, skill_dir, inst_file = sys.argv[1:4]
model = "sonnet"
reps = 2
if "--model" in sys.argv:
    model = sys.argv[sys.argv.index("--model") + 1]
if "--reps" in sys.argv:
    reps = int(sys.argv[sys.argv.index("--reps") + 1])

def strip_frontmatter(s: str) -> str:
    if s.startswith("---\n"):
        return s.split("\n---\n", 1)[1]
    return s

parts = [open(inst_file, encoding="utf-8").read(), "\n\n---\n# スキル: sakimawari\n"]
parts.append(strip_frontmatter(open(os.path.join(skill_dir, "SKILL.md"), encoding="utf-8").read()))
ref_dir = os.path.join(skill_dir, "references")
for f in sorted(os.listdir(ref_dir)):
    if f == "sources.md":
        continue
    parts.append(f"\n\n## ファイル: references/{f}\n" + open(os.path.join(ref_dir, f), encoding="utf-8").read())
system_prompt = "".join(parts)

out_dir = os.path.join(HERE, "runs", name)
os.makedirs(out_dir, exist_ok=True)
open(os.path.join(out_dir, "_system_prompt.txt"), "w", encoding="utf-8").write(system_prompt)

truth = json.load(open(os.path.join(HERE, "truth.json"), encoding="utf-8"))
only = None
if "--cases" in sys.argv:
    only = set(sys.argv[sys.argv.index("--cases") + 1].split(","))
jobs = []
for case, info in truth.items():
    if only and case not in only:
        continue
    doc = open(os.path.join(HERE, "cases", case + ".md"), encoding="utf-8").read()
    aud = info.get("audience") or "なし"
    prompt = f"次の資料について、想定質問を出してください。\n相手の情報: {aud}\n\n---資料ここから---\n{doc}---資料ここまで---\n"
    for r in range(1, reps + 1):
        jobs.append((case, r, prompt))

cwd = os.path.join(HERE, "run_cwd")
os.makedirs(cwd, exist_ok=True)

def run(job: tuple[str, int, str]) -> tuple[str, int]:
    case, r, prompt = job
    path = os.path.join(out_dir, f"{case}_r{r}.md")
    cmd = ["claude", "-p", "--system-prompt", system_prompt, "--tools", "", "--setting-sources", "project",
           "--disable-slash-commands", "--strict-mcp-config", "--no-session-persistence", "--model", model]
    try:
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=900, cwd=cwd)
        text = p.stdout if p.returncode == 0 else f"[ERROR rc={p.returncode}]\n{p.stdout}\n{p.stderr}"
    except subprocess.TimeoutExpired:
        text = "[ERROR timeout]"
    open(path, "w", encoding="utf-8").write(text)
    return path, len(text)

with ThreadPoolExecutor(max_workers=6) as ex:
    for path, n in ex.map(run, jobs):
        print(os.path.basename(path), n)
