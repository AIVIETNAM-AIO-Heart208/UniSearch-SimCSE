"""Compare the four frozen retrieval variants on the open HCMUS development pilot."""

from __future__ import annotations

import argparse
import json
import platform
import tempfile
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from html import escape
from importlib.metadata import version
from pathlib import Path
from time import perf_counter
from xml.etree import ElementTree

from apps import app
from simcse_lab.model.encoders import REVISION, SimCSEEncoder, verify_snapshot
from simcse_lab.provenance import base_commit, working_tree_status
from simcse_lab.retrieval.hcmus import load_article_map
from simcse_lab.retrieval.search import RetrievalIndex, _scale

PILOT = Path("data/development/clause-scope-pilot.jsonl")
PILOT_SHA256 = "3ffd896f4fa645c84cbf1a85e3c016672cea4e1d34d5062a8c25d820b0525fd0"
MANIFEST = Path("experiments/application/results/D2/summary.json")
VARIANTS = ("A", "K", "G", "K+G")

# Source phrases needed together in an eligible clause. These are grading keys
# for the eight labelled questions, never inputs to retrieval or warning rules.
EVIDENCE = {
    "pilot-01": ("lịch học tập trung", "không vượt quá 15 giờ/tuần và 4 giờ/ngày"),
    "pilot-03": ("hiệu trưởng ban hành quy định về việc lấy ý kiến phản hồi", "mức độ, hình thức công khai"),
    "pilot-05": ("bảng điểm theo từng học phần", "phát kèm theo bằng tốt nghiệp"),
    "pilot-07": ("trường quản lý đầy đủ", "tình trạng việc làm sau tốt nghiệp"),
    "pilot-09": ("sinh viên tham gia chương trình tích hợp", "thông tin đầy đủ", "điều kiện chuyển ra khỏi chương trình"),
    "pilot-11": ("bảo quản bài thi", "phòng khảo thí và đảm bảo chất lượng thực hiện"),
    "pilot-13": ("sử dụng kết quả phản hồi", "người sử dụng lao động", "để cải tiến chương trình đào tạo"),
    "pilot-15": ("loại học phần thực hành", "các điểm thành phần bao gồm", "điểm chuyên cần"),
}


def select_clauses(index: RetrievalIndex, scores: tuple, ranked: list, weight: float) -> list:
    """Choose a window within each article while preserving every article score and rank."""
    lexical, dense = scores
    rank_weight = Fraction(str(weight))
    scale_b, scale_d = (_scale([max(values[i] for i in indices) for indices in index.groups.values()])
                        for values in scores)
    selected = []
    for article, score, original in ranked:
        candidates = [i for i in index.groups[article] if index.chunks[i]["clause_id"] is not None]
        chunk_id = original
        if candidates:
            def sort_key(i: int) -> tuple:
                rank_b = 1 + sum(lexical[j] > lexical[i] for j in candidates)
                rank_d = 1 + sum(dense[j] > dense[i] for j in candidates)
                reciprocal = rank_weight / rank_b + (1 - rank_weight) / rank_d
                fused = weight * scale_b(lexical[i]) + (1 - weight) * scale_d(dense[i])
                return -reciprocal, -fused, index.chunks[i]["chunk_id"]

            chunk_id = index.chunks[min(candidates, key=sort_key)]["chunk_id"]
        selected.append([article, score, chunk_id])
    return selected


def evidence_path(row: dict, group: list, index: RetrievalIndex, accepted: bool) -> list[str] | None:
    """Return the fewest disclosures needed to read a sufficient passage in the first topic."""
    if not row["gold_clause_ids"]:
        return None
    paths = []
    for position, (chunk, _) in enumerate(group):
        passage = ElementTree.fromstring("<root>" + app._edition_body(chunk, index) + "</root>").find(
            "div[@class='passage']"
        )
        # The UI may put the first numbered clause behind a disclosure for a title-only hit.
        clause_id = chunk["clause_id"]
        if clause_id is None and passage.find("details") is not None:
            numbered = [index.chunks[i] for i in index.groups[chunk["article_id"]]
                        if index.chunks[i]["clause_id"] is not None]
            if numbered:
                clause_id = min(numbered, key=lambda c: c["char_start"])["clause_id"]
        if clause_id not in row["gold_clause_ids"]:
            continue

        def sufficient(text: str) -> bool:
            normalized = " ".join(text.casefold().split())
            return all(phrase in normalized for phrase in EVIDENCE[row["qid"]])

        if not sufficient(" ".join(passage.itertext())):
            continue
        steps = []
        if not accepted:
            steps.append("open_topic")
        if position:
            steps.append("other_edition")
        visible = " ".join(word for element in passage if element.tag != "details" for word in element.itertext())
        if not sufficient(visible):
            steps.append("read_more")
        paths.append(steps)
    return min(paths, key=len) if paths else None


def compare_question(index: RetrievalIndex, scores: tuple, row: dict, config: dict,
                     html_dir: Path, positions: dict, topics: dict) -> dict:
    weight, threshold = config["weight"], config["threshold"]
    ranked, base_cosine = index.rank(scores, "hybrid", weight=weight)
    reranked = select_clauses(index, scores, ranked, weight)
    bm25 = index.rank(scores, "bm25")[0][0]
    dense = index.rank(scores, "dense")[0][0]
    leaders = {"bm25": bm25[0], "dense": dense[0], "hybrid": ranked[0][0]}
    agree = bm25[1] > 0 and len({topics[article] for article in leaders.values()}) == 1
    if len(ranked) != len(index.groups) or [r[:2] for r in ranked] != [r[:2] for r in reranked]:
        raise ValueError("Article scores, order and completeness must match")

    gold = row["gold_clause_ids"]
    gold_articles = {cid.split(":khoan-")[0] for cid in gold}
    top_article = ranked[0][0]
    article_hit = top_article in gold_articles
    topic_hit = any(topics[a] == topics[top_article] for a in gold_articles)
    article_edition_miss = topic_hit and top_article.split(":")[0] not in {a.split(":")[0] for a in gold_articles}
    result = {key: row[key] for key in ("qid", "family_id", "question", "scope", "gold_clause_ids")}
    result.update(article_hit=article_hit if gold else None, topic_hit=topic_hit if gold else None,
                  wrong_edition_same_topic=article_edition_miss if gold else None,
                  first_articles=leaders, first_topics={k: topics[v] for k, v in leaders.items()},
                  max_bm25=bm25[1], topic_gate=agree,
                  article_order=[r[0] for r in ranked], article_scores=[r[1] for r in ranked],
                  selected_chunks={"A": [r[2] for r in ranked], "K": [r[2] for r in reranked]},
                  raw_bm25=scores[0], raw_cosine=scores[1], variants={})

    # Also call the application's actual single-query entry point for exact baseline parity.
    baseline_html, _, baseline_status = app.answer(index, row["question"], weight, threshold, show_reasons=False)
    for name in VARIANTS:
        ranking = reranked if name in ("K", "K+G") else ranked
        first = index.by_chunk[ranking[0][2]]
        cosine = scores[1][positions[first["chunk_id"]]]
        accepted = cosine >= threshold and (name not in ("G", "K+G") or agree)
        groups = app.group_results(index, ranking)
        primary = groups[0][0][0]
        body = app.render_groups(groups, index, question=row["question"], expand_first=accepted)
        message = ""
        if cosine < threshold:
            message = (f"Độ tin cậy thấp đối với trích đoạn hạng đầu của Hybrid "
                       f"({app._edition(first)}, {app._citation(first)}). "
                       "Hãy đối chiếu văn bản gốc hoặc hỏi Phòng Đào tạo.")
        elif not accepted:
            message = "Chưa đủ căn cứ để xác nhận chủ đề. Hãy đối chiếu văn bản gốc hoặc hỏi Phòng Đào tạo."
        if name == "A" and (base_cosine != cosine or (body, message) != (baseline_html, baseline_status)):
            raise ValueError(f"{row['qid']}: control differs from the running app code")
        view = f"{row['qid']}-{name}.html"
        html = ('<!doctype html><html lang="vi"><meta charset="utf-8"><title>Tra cứu quy chế HCMUS</title>'
                '<link rel="stylesheet" href="search.css"><body class="gradio-container"><main id="regulations">'
                f'<h1>{escape(row["question"])}</h1><p role="status">{escape(message)}</p>{body}</main></body></html>')
        (html_dir / view).write_bytes(html.encode())
        path = evidence_path(row, groups[0], index, accepted)
        result["variants"][name] = {
            "chunk_id": first["chunk_id"], "clause_id": first["clause_id"], "cosine": cosine,
            "accepted": accepted, "clause_hit": first["clause_id"] in gold if gold else None,
            "primary_chunk_id": primary["chunk_id"], "primary_clause_id": primary["clause_id"],
            "evidence_path": path, "visible_evidence": path == [] if gold else None,
            "view": "html/" + view, "view_sha256": sha256(html.encode()).hexdigest(),
        }
    return result


def count_outcomes(rows: list[dict]) -> dict:
    counts = {}
    for name in VARIANTS:
        metrics = Counter()
        for row in rows:
            v = row["variants"][name]
            if row["scope"] == "in":
                metrics.update({"article_hit": row["article_hit"], "topic_hit": row["topic_hit"],
                                "wrong_edition_same_topic": row["wrong_edition_same_topic"],
                                "clause_miss_given_article_hit": row["article_hit"] and not v["clause_hit"],
                                "clause_hit": v["clause_hit"], "accepted_in": v["accepted"],
                                "visible_evidence": v["visible_evidence"],
                                "correct_clause_needs_disclosure": v["clause_hit"] and bool(v["evidence_path"])})
            else:
                metrics["false_confident_" + row["scope"]] += v["accepted"]
        counts[name] = dict(metrics)
    return counts


def paired_outcomes(rows: list[dict]) -> dict:
    paired = {}
    for scope, field in [("in", "clause_hit"), ("near_out", "accepted"), ("far_out", "accepted"),
                         ("in", "accepted"), ("in", "visible_evidence")]:
        cells = {"both_success": [], "K+G_only": [], "A_only": [], "both_fail": []}
        for row in rows:
            if row["scope"] != scope:
                continue
            a, k = (row["variants"][n][field] for n in ("A", "K+G"))
            if scope != "in":
                a, k = not a, not k
            key = {(True, True): "both_success", (True, False): "A_only",
                   (False, True): "K+G_only", (False, False): "both_fail"}[a, k]
            cells[key].append(row["qid"])
        paired[f"{scope}/{field}"] = cells
    return paired


def run(model_path: Path, output: Path) -> None:
    import torch

    manifest = json.loads(MANIFEST.read_bytes())
    paths = {k: Path(manifest["inputs"][k]["path"]) for k in ("config", "corpus", "topic_map")}
    paths["pilot"] = PILOT
    blobs = {k: p.read_bytes() for k, p in paths.items()}
    hashes = {k: sha256(data).hexdigest() for k, data in blobs.items()}
    expected = {k: manifest["inputs"][k]["sha256"] for k in ("config", "corpus", "topic_map")}
    if hashes != {**expected, "pilot": PILOT_SHA256}:
        raise ValueError("Frozen inputs do not match their recorded SHA-256")
    frozen = json.loads(blobs["config"])
    config = manifest["frozen"]
    if (frozen["split"] != "D1-dev" or REVISION != config["model_revision"]
            or any(frozen["selected"][k] != config[k] for k in ("weight", "threshold"))
            or verify_snapshot(model_path) != frozen["checkpoint"]["snapshot_sha256"]):
        raise ValueError("Published operating point or checkpoint mismatch")
    chunks = list(map(json.loads, blobs["corpus"].splitlines()))
    cases = list(map(json.loads, blobs["pilot"].splitlines()))
    positions = {c["chunk_id"]: i for i, c in enumerate(chunks)}
    topics = {a: r["topic_id"] for a, r in load_article_map(paths["topic_map"]).items()}
    if len(chunks) != 273 or len(topics) != 51 or len(set(topics.values())) != 26:
        raise ValueError("Expected the complete HCMUS corpus and mapping")
    if {c["qid"] for c in cases if c["scope"] == "in"} != EVIDENCE.keys():
        raise ValueError("Missing source-based UI grading key")
    counts = Counter(c["scope"] for c in cases)
    torch.set_num_threads(frozen["run"]["threads"])
    torch.manual_seed(frozen["run"]["torch_seed"])
    start = perf_counter()
    index = RetrievalIndex(chunks, SimCSEEncoder(str(model_path), "cpu"), frozen["run"]["batch_size"])
    html_dir = output / "html"
    html_dir.mkdir()
    css = Path("apps/search.css")
    (html_dir / "search.css").write_bytes(css.read_bytes())
    rows = [compare_question(index, next(index.score([r["question"]])), r, config, html_dir, positions, topics)
            for r in cases]
    predictions = "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n" for r in rows)
    (output / "predictions.jsonl").write_bytes(predictions.encode())
    code = [Path(__file__).relative_to(Path.cwd()), Path("apps/app.py"), css, Path("apps/search.js"),
            *(Path("src/simcse_lab") / f for f in ("regulation_excerpts.py", "retrieval/search.py",
              "retrieval/hcmus.py", "retrieval/preprocess.py", "model/encoders.py"))]
    summary = {
        "split": "hcmus-development/open-pilot", "cases": dict(counts), "config": config,
        "inputs": {k: {"path": paths[k].as_posix(), "sha256": h} for k, h in hashes.items()},
        "snapshot_sha256": frozen["checkpoint"]["snapshot_sha256"],
        "raw_score_chunk_order": [c["chunk_id"] for c in chunks],
        "raw_score_clause_ids": [c["clause_id"] for c in chunks],
        "counts": count_outcomes(rows), "paired_K+G_vs_A": paired_outcomes(rows),
        "predictions_sha256": sha256(predictions.encode()).hexdigest(),
        "run": {"git_commit": base_commit(),
                "source_sha256": {p.as_posix(): sha256(p.read_bytes()).hexdigest() for p in code},
                "working_tree_code": working_tree_status(code),
                "python": platform.python_version(), "platform": platform.platform(), "cpu": platform.processor(),
                "torch": str(torch.__version__), "threads": torch.get_num_threads(), "seed": torch.initial_seed(),
                "corpus_batch_size": index.batch_size, "query_batch_size": 1, "device": "cpu",
                "packages": {p: version(p) for p in frozen["run"]["packages"]},
                "index_and_pilot_seconds": perf_counter() - start},
    }
    (output / "summary.json").write_bytes((json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", type=Path, default=Path("outputs/d1-model"))
    parser.add_argument("--output", required=True, type=Path, help="New local directory for rankings and rendered views")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Choose a new output directory")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=args.output.parent) as temp:
        stage = Path(temp) / "pilot"
        stage.mkdir()
        run(args.model_path, stage)
        stage.rename(args.output)
    print(f"Compared A, K, G and K+G on the 16 development questions in {args.output}")


if __name__ == "__main__":
    main()
