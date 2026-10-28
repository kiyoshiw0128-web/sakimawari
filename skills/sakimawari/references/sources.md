# 考え方の出典と、確認の程度

どの文献も、原文を通読したわけではない。ページを取得して要約を確認した程度である。強く引用する前に、原文で確かめること。

このファイルは出典の記録である。手順の順番ではない。手順は SKILL.md に従う。手順の前段では、6要素と知的基準は埋めない。5つの視点は、疑問を増やす装置としてラベルの前に置かない。

## 取り入れた考え方

| 考え方 | 出典 | 確認の程度 |
|---|---|---|
| 主張を「覆されうる推論」と見る。批判的質問は、結論を覆しうる条件を調べる質問である。質問のリストは網羅を保証できない。 | J. Anthony Blair「Walton's Argumentation Schemes For Presumptive Reasoning: A Critique And Development」（ISSA Proceedings 1998）https://rozenbergquarterly.com/issa-proceedings-1998-waltons-argumentation-schemes-for-presumptive-reasoning-a-critique-and-development/ | ページ本文を取得し、要約を確認した |
| 主張を6要素（主張、根拠、論拠、裏づけ、限定、反証への対応）に分ける | Stephen Toulmin『The Uses of Argument』（1958）。解説: https://owl.excelsior.edu/argument-and-critical-thinking/organizing-your-argument/organizing-your-argument-toulmin/ | 二次資料のみ。原著は未確認 |
| 思考の8要素（目的、問い、前提、視点、情報、概念、推論、含意）と、知的基準（明確さ、正確さ、精密さ、関連性、深さ、広さ、論理性） | Richard Paul・Linda Elder。解説: https://student.louisville.edu/paul-elder-critical-thinking-framework | 解説資料のみ。基準の文言は原書と照合していない |
| 質問は、要点を先に抜き出してから作る | Yining Juan, Chung-Chi Chen, Hen-Hsen Huang, Hsin-Hsi Chen「Generating Multiple Questions from Presentation Transcripts: A Pilot Study on Earnings Conference Calls」（INLG 2023）https://aclanthology.org/2023.inlg-main.35/ | 要旨のみ。方法と数値は未確認 |
| 人間の査読を唯一の正解にしない | Hexuan Deng ら「CoCoReviewBench」（arXiv:2605.07905、2026年のプレプリント、未査読）https://arxiv.org/abs/2605.07905 | 要旨のみ |

## 視点を切り替えて読む方法の出典（v0.2 で追加）

| 考え方 | 出典 | 確認の程度 |
|---|---|---|
| 文ごとの素朴な疑問（なぜ、詳しく、定義、背景、具体例、その先） | Wei-Jen Ko ら「Inquisitive Question Generation for High Level Text Comprehension」（EMNLP 2020）https://aclanthology.org/2020.emnlp-main.530 | 本文（PDF）で確認。ニュース記事で、分析した疑問は120件 |
| 理由の3つの検査（受け入れられる、関係がある、足りる） | Henning Wachsmuth ら「Computational Argumentation Quality Assessment in Natural Language」（EACL 2017）https://aclanthology.org/E17-1017/ 。Johnson と Blair の基準は https://plato.stanford.edu/entries/logic-informal/ | Wachsmuth らは本文（PDF）で確認。Stanford 百科事典は要約で確認 |
| 役割ごとの視点で読む | Basili ら「The Empirical Investigation of Perspective-Based Reading」（1996） | 検索結果の要約のみ。原論文は取得できなかった |
| 失敗の想像（先に失敗したものとして理由を考える） | Mitchell, Russo, Pennington「Back to the Future: Temporal Perspective in the Explanation of Events」（1989）https://colab.ws/articles/10.1002%2Fbdm.3960020103 | 抄録で確認。「30%」という数字は未確認 |
| 曖昧さと検証できなさ | Gentili と Falessi「Characterizing Requirements Smells」（2024）https://arxiv.org/html/2404.11106v1 | ページ本文で確認。実務者10人、1社 |
| 推論の落とし穴（13種類） | Zhijing Jin ら「Logical Fallacy Detection」（EMNLP 2022 Findings）https://aclanthology.org/2022.findings-emnlp.532/ | 本文（PDF）で確認 |
| 質問を広く出してから絞る | Blanca Calvo Figueras ら「Overview of the Critical Questions Generation Shared Task」（ArgMining 2025）https://aclanthology.org/2025.argmining-1.23 | 本文（PDF）で確認 |

## 限界

- 「上司や聴衆が、資料のどこで、実際に何を聞くか」を直接調べた研究は、見つかっていない。
- 穴の型の一覧は仮説であり、実際に出た質問と照らして直す前提である。
- 論証スキームの理論には、効果も根拠も十分ではないとする批判がある。
- 視点を切り替えて読む方法の根拠は、ニュース記事、要求仕様書、学生の問題などで得られたもので、仕事の資料で同じ効果が出るかは確かめていない。自作の検査では、穴の発見が数%増える程度だった。
