"""Score runs. usage: python3 score.py <iter_name> [--detail]"""
from __future__ import annotations

import json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
name = sys.argv[1]
detail = "--detail" in sys.argv
truth = json.load(open(os.path.join(HERE, "truth.json"), encoding="utf-8"))
run_dir = os.path.join(HERE, "runs", name)

JARGON = ["飛躍", "論拠", "内部の不整合", "比較対象の欠落", "隠れた前提", "代替案の不在",
          "範囲・条件の抜け", "実行面の抜け", "断定の強さのずれ", "目的・問いの不在", "課題と施策のずれ",
          "反証", "Toulmin", "Paul", "反証への対応"]
SUBS = ["原文", "どこが引っかかるか", "直し方", "答えの準備", "勧めと重さ"]

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[\s「」『』]", "", s)
    return s

def split_sections(text: str) -> tuple[list[dict], list[dict]]:
    lines = text.split("\n")
    qs, other, cur, mode = [], [], None, None
    for ln in lines:
        if re.match(r"^###\s*Q\d+", ln):
            cur = {"head": ln, "lines": []}
            qs.append(cur); mode = "q"; continue
        if re.match(r"^###\s*その他", ln):
            cur = {"head": ln, "lines": []}
            other.append(cur); mode = "o"; continue
        if re.match(r"^##\s", ln) or re.match(r"^###\s", ln):
            cur = None; mode = None; continue
        if cur is not None:
            cur["lines"].append(ln)
    return qs, other

def top_level_quotes(t: str) -> list[str]:
    depth, start, res = 0, None, []
    for i, ch in enumerate(t):
        if ch == "「":
            if depth == 0:
                start = i + 1
            depth += 1
        elif ch == "」" and depth > 0:
            depth -= 1
            if depth == 0:
                res.append(t[start:i])
    return res

def extract_quotes(lines: list[str]) -> list[str]:
    """quotes from the 原文 subsection: blockquote lines (top-level 「…」, else the whole line)."""
    quotes, in_orig = [], False
    for ln in lines:
        m = re.match(r"^####\s*(.+)", ln)
        if m:
            in_orig = "原文" in m.group(1)
            continue
        if in_orig and ln.lstrip().startswith(">"):
            t = ln.lstrip()[1:].strip()
            if not t:
                continue
            m2 = re.match(r"^(.*」)\s*[（(][^（）()]*[）)]\s*$", t)
            if m2:
                t = m2.group(1)
            qs = top_level_quotes(t)
            quotes.extend(qs if qs else [t])
    return quotes

def quote_segments(q: str) -> list[str]:
    return [s for s in re.split(r"…+|\.\.\.", norm(q)) if len(s) >= 3]

def overlap(seg: str, anchors: list[str]) -> bool:
    for a in anchors:
        na = norm(a)
        if seg in na or na in seg:
            return True
    return False

def numbers(s: str) -> set[str]:
    s = unicodedata.normalize("NFKC", s).replace(",", "")
    return set(re.findall(r"\d+(?:\.\d+)?", s))

def score_file(case: str, path: str, doc: str) -> dict:
    text = open(path, encoding="utf-8").read()
    info = truth[case]
    res = {"file": os.path.basename(path), "chars": len(text)}
    if text.startswith("[ERROR"):
        res["error"] = True
        return res
    qs, others = split_sections(text)
    res["n_q"] = len(qs)
    sev = {"高": 0, "中": 0, "低": 0}
    for q in qs:
        m = re.search(r"重さ[:：]\s*([高中低])", "\n".join(q["lines"]))
        if m:
            sev[m.group(1)] += 1
    res["sev"] = sev
    vps = []
    for q in qs:
        m = re.search(r"視点[:：]\s*([^\n]+)", "\n".join(q["lines"]))
        vps.append(m.group(1).strip() if m else "")
    res["viewpoints"] = vps
    res["alarm"] = (sev["高"] + sev["中"]) if not info["holes"] else None
    ndoc = norm(doc)

    # verbatim
    bad_quotes, n_quotes = [], 0
    for q in qs:
        for qt in extract_quotes(q["lines"]):
            n_quotes += 1
            segs = quote_segments(qt)
            if not segs or not all(s in ndoc for s in segs):
                bad_quotes.append(qt[:60])
    res["quotes"] = n_quotes
    res["bad_quotes"] = bad_quotes
    res["qs_without_quote"] = sum(1 for q in qs if not extract_quotes(q["lines"]))

    # holes
    found_main, found_minor = set(), set()
    q_match = []
    for q in qs:
        segs = [s for qt in extract_quotes(q["lines"]) for s in quote_segments(qt)]
        hit_h = [h["id"] for h in info["holes"] if any(overlap(s, h["anchors"]) for s in segs)]
        hit_d = any(any(overlap(s, d) for s in segs) for d in info["decoys"])
        q_match.append((q["head"], hit_h, hit_d))
        for h in hit_h:
            found_main.add(h)
    other_text = "\n".join("\n".join(o["lines"]) for o in others)
    for h in info["holes"]:
        if h["id"] in found_main:
            continue
        for m in re.findall(r"「([^」]+)」", other_text):
            if overlap(norm(m), h["anchors"]) and len(norm(m)) >= 4:
                found_minor.add(h["id"])
    res["holes"] = len(info["holes"])
    res["found_main"] = sorted(found_main)
    res["found_minor"] = sorted(found_minor)
    res["missed"] = [h["id"] for h in info["holes"] if h["id"] not in found_main | found_minor]
    res["decoy_flagged"] = [h for h, hh, d in q_match if d and not hh]
    res["unmatched_q"] = [h for h, hh, d in q_match if not hh and not d]
    high_ids = {h["id"] for h in info["holes"] if h["weight"] == "高"}
    res["high_total"] = len(high_ids)
    res["high_found"] = len(high_ids & found_main)

    # format
    body = "\n".join(l for l in text.split("\n") if "型:" not in l and "型：" not in l)
    res["jargon"] = sorted({w for w in JARGON if w in body})
    res["has_overview"] = "全体の見取り図" in text
    ov = text.split("全体の見取り図", 1)[-1].split("\n## 1", 1)[0] if res["has_overview"] else ""
    res["overview_table"] = sum(1 for l in ov.split("\n") if l.strip().startswith("|")) >= 3
    res["overview_figure"] = "```" in ov
    res["has_audience_line"] = "想定した相手" in text
    sub_missing, bullets = 0, 0
    for q in qs:
        heads = [m.group(1) for l in q["lines"] if (m := re.match(r"^####\s*(.+)", l))]
        sub_missing += sum(1 for s in SUBS if not any(s in h for h in heads))
        bullets += sum(1 for l in q["lines"] if re.match(r"^\s*[-*•]\s", l))
    res["sub_missing"] = sub_missing
    res["bullets_in_q"] = bullets
    fences = text.count("```")
    blocks = re.findall(r"```[^\n]*\n(.*?)```", text, re.S)
    res["figures"] = len(blocks)
    res["figure_over10"] = sum(1 for b in blocks if len([l for l in b.split("\n") if l.strip()]) > 10)
    res["fence_unbalanced"] = fences % 2 == 1

    # copilot-observed issues
    res["bold"] = text.count("**")
    nonblank = [l for l in text.split("\n") if l.strip()]
    res["preamble"] = bool(nonblank) and not (nonblank[0].startswith("#") or nonblank[0].startswith("想定した相手"))
    fix_total = fix_concrete = 0
    for q in qs:
        sec, on = [], False
        for l in q["lines"]:
            m = re.match(r"^####\s*(.+)", l)
            if m:
                on = "直し方" in m.group(1)
                continue
            if on:
                sec.append(l)
        fix_total += 1
        body = "\n".join(sec)
        if re.search(r"案[:：]\s*「[^」]{8,}", body) or re.search(r"案[:：]\s*[^\n]{0,4}「[^」]{8,}", body):
            fix_concrete += 1
    res["fix_total"] = fix_total
    res["fix_concrete"] = fix_concrete
    ovtxt = text.split("全体の見取り図", 1)[-1].split("\n## 1", 1)[0] if "全体の見取り図" in text else ""
    figs = re.findall(r"```[^\n]*\n(.*?)```", ovtxt, re.S)
    res["overview_markers"] = any(re.search(r"←\s*Q\d", f) for f in figs)
    res["overview_fig"] = bool(figs)
    vp = set()
    for v in res.get("viewpoints", []):
        for k in ("承認する人", "実行する人", "影響を受ける人", "疑う専門家", "失敗の想像", "文ごとの疑問", "理由の検査", "言葉の曖昧さ"):
            if k in v:
                vp.add(k)
    res["vp_kinds"] = len(vp)
    # invented numbers
    t2 = re.sub(r"Q\d+", "", text)
    t2 = "\n".join(l for l in t2.split("\n") if "型:" not in l and "型：" not in l)
    t2 = re.sub(r"(スライド|ページ)\s*\d+|\d+\s*枚目|\d+\s*ページ|^#+\s*\d+\.|^\s*\d+\.\s", "", t2, flags=re.M)
    t2 = re.sub(r"【[^】]*】", "", t2)
    t2 = re.sub(r"\b\d+[〜~]\d+\s*文|\d+件程度|10件|1〜2|2〜4|3\s*つ|2\s*つ", "", t2)
    extra = sorted(numbers(t2) - numbers(doc) - {"1", "2", "3", "4", "5", "10", "0"})
    res["new_numbers"] = extra
    return res

all_res = []
for case in truth:
    doc = open(os.path.join(HERE, "cases", case + ".md"), encoding="utf-8").read()
    for f in sorted(os.listdir(run_dir)):
        if f.startswith(case + "_r") and f.endswith(".md"):
            r = score_file(case, os.path.join(run_dir, f), doc)
            r["case"] = case
            all_res.append(r)

json.dump(all_res, open(os.path.join(run_dir, "_scores.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def pct(a: int, b: int) -> str:
    return f"{a}/{b}" + (f" ({100*a//b}%)" if b else "")

tot = dict(holes=0, found=0, high_t=0, high_f=0, decoy=0, unmatched=0, nq=0, badq=0, nq_noquote=0, jargon=0,
           subm=0, bullets=0, over10=0, newnum=0, runs=0, noov=0, notable=0, nofig=0)
print(f"== {name} ==")
for r in all_res:
    if r.get("error"):
        print(r["file"], "ERROR"); continue
    tot["runs"] += 1
    tot["holes"] += r["holes"]; tot["found"] += len(r["found_main"]) + len(r["found_minor"])
    tot["high_t"] += r["high_total"]; tot["high_f"] += r["high_found"]
    tot["decoy"] += len(r["decoy_flagged"]); tot["unmatched"] += len(r["unmatched_q"]); tot["nq"] += r["n_q"]
    tot["badq"] += len(r["bad_quotes"]); tot["nq_noquote"] += r["qs_without_quote"]
    tot["jargon"] += len(r["jargon"]); tot["subm"] += r["sub_missing"]; tot["bullets"] += r["bullets_in_q"]
    tot["over10"] += r["figure_over10"]; tot["newnum"] += len(r["new_numbers"])
    tot["noov"] += 0 if r["has_overview"] else 1
    tot["notable"] += 0 if r["overview_table"] else 1
    tot["nofig"] += 0 if r["overview_figure"] else 1
    line = (f"{r['file']:<18} Q={r['n_q']:<2} 穴 {len(r['found_main'])}+{len(r['found_minor'])}/{r['holes']} "
            f"高 {r['high_found']}/{r['high_total']} 罠誤指摘={len(r['decoy_flagged'])} 未照合Q={len(r['unmatched_q'])} "
            f"引用不一致={len(r['bad_quotes'])} 用語={len(r['jargon'])} 小見出し欠={r['sub_missing']} 箇条={r['bullets_in_q']} "
            f"図={r['figures']} 新数字={len(r['new_numbers'])} 字数={r['chars']} 重さ高/中/低={r['sev']['高']}/{r['sev']['中']}/{r['sev']['低']}")
    print(line)
    if detail:
        for k in ("missed", "decoy_flagged", "unmatched_q", "bad_quotes", "jargon", "new_numbers"):
            if r.get(k):
                print("   ", k, r[k])
print("-- 合計 --")
print("見つけた穴:", pct(tot["found"], tot["holes"]), "| 高の穴:", pct(tot["high_f"], tot["high_t"]))
print("罠の誤指摘:", tot["decoy"], "| 照合できないQ(要確認):", tot["unmatched"], "/", tot["nq"], "Q")
print("引用が原文と不一致:", tot["badq"], "| 引用のないQ:", tot["nq_noquote"])
print("用語の漏れ:", tot["jargon"], "| 小見出しの欠け:", tot["subm"], "| Q内の箇条書き:", tot["bullets"])
print("10行超の図:", tot["over10"], "| 資料にない数字(要確認):", tot["newnum"])
clean = [r for r in all_res if not r.get("error") and r.get("alarm") is not None]
print("穴のない資料での警報(高+中のQ数。0〜1が理想):", [r["alarm"] for r in clean])
ch = [(r["case"], r["sev"]["高"], r["n_q"]) for r in all_res if not r.get("error") and not truth[r["case"]]["holes"]]
print("穴のない資料(E,I,J)での『高』の数:", sum(x[1] for x in ch), "| 同Q数:", sum(x[2] for x in ch), "|", ch)
print("見取り図なし:", tot["noov"], "| 見取り図に表なし:", tot["notable"], "| 見取り図に図なし:", tot["nofig"], "| 実行数:", tot["runs"])
