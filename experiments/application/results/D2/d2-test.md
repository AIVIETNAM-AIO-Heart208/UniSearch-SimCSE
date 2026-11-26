# Retrieval on D2-test

Fixed BM25 weight `0.6` and warning threshold `0.6201629042625427`.

The 26 November 2026 run used the [frozen D2 labels](../../../../data/d2/queries_d2.jsonl), the 51-article HCMUS corpus and [the settings selected on D1-dev](../../../external_dataset/results/D1-dev-tuning/summary.json). Retrieval ran offline on an AMD Ryzen 7 6800H with four PyTorch threads and an encoder batch size of 16. The retrieval and evaluation processes took 91.143 and 5.780 seconds respectively. [The JSON record](summary.json) contains the full commands, dependency versions and input and ranking hashes.

In the table, `dense` denotes SimCSE-VN. The 86 answerable questions form the denominator for retrieval metrics, including Clause@1. The lexical-overlap groups use the highest Jaccard overlap with a labelled article. The two cutoffs are 0.05386031 and 0.07595088. The random baseline shuffles article order and groups by topic before computing topic metrics.

| Slice | Queries | Method | Level | Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR@10 |
|---|---:|---|---|---:|---:|---:|---:|---:|
| All in-scope | 86 | bm25 | article | 0.7326 | 0.9302 | 0.9651 | 0.9884 | 0.8396 |
| All in-scope | 86 | bm25 | topic | 0.7558 | 0.9419 | 0.9884 | 1.0000 | 0.8592 |
| All in-scope | 86 | bm25 | clause | 0.6512 | — | — | — | — |
| All in-scope | 86 | dense | article | 0.6279 | 0.9070 | 0.9419 | 0.9884 | 0.7562 |
| All in-scope | 86 | dense | topic | 0.6512 | 0.9186 | 0.9651 | 1.0000 | 0.7924 |
| All in-scope | 86 | dense | clause | 0.5233 | — | — | — | — |
| All in-scope | 86 | hybrid | article | 0.7907 | 0.9651 | 1.0000 | 1.0000 | 0.8750 |
| All in-scope | 86 | hybrid | topic | 0.8023 | 1.0000 | 1.0000 | 1.0000 | 0.8895 |
| All in-scope | 86 | hybrid | clause | 0.6860 | — | — | — | — |
| low | 29 | bm25 | article | 0.6552 | 0.8966 | 0.9655 | 0.9655 | 0.7931 |
| low | 29 | bm25 | topic | 0.6552 | 0.9310 | 0.9655 | 1.0000 | 0.7998 |
| low | 29 | bm25 | clause | 0.6207 | — | — | — | — |
| low | 29 | dense | article | 0.5862 | 0.8621 | 0.8966 | 0.9655 | 0.7075 |
| low | 29 | dense | topic | 0.6552 | 0.8621 | 0.9310 | 1.0000 | 0.7808 |
| low | 29 | dense | clause | 0.4138 | — | — | — | — |
| low | 29 | hybrid | article | 0.7241 | 0.9310 | 1.0000 | 1.0000 | 0.8276 |
| low | 29 | hybrid | topic | 0.7241 | 1.0000 | 1.0000 | 1.0000 | 0.8391 |
| low | 29 | hybrid | clause | 0.6207 | — | — | — | — |
| medium | 28 | bm25 | article | 0.6786 | 0.9286 | 0.9286 | 1.0000 | 0.8021 |
| medium | 28 | bm25 | topic | 0.7143 | 0.9286 | 1.0000 | 1.0000 | 0.8375 |
| medium | 28 | bm25 | clause | 0.6071 | — | — | — | — |
| medium | 28 | dense | article | 0.6786 | 0.9286 | 0.9643 | 1.0000 | 0.7854 |
| medium | 28 | dense | topic | 0.6786 | 0.9643 | 1.0000 | 1.0000 | 0.8125 |
| medium | 28 | dense | clause | 0.6071 | — | — | — | — |
| medium | 28 | hybrid | article | 0.7500 | 0.9643 | 1.0000 | 1.0000 | 0.8482 |
| medium | 28 | hybrid | topic | 0.7857 | 1.0000 | 1.0000 | 1.0000 | 0.8810 |
| medium | 28 | hybrid | clause | 0.6786 | — | — | — | — |
| high | 29 | bm25 | article | 0.8621 | 0.9655 | 1.0000 | 1.0000 | 0.9224 |
| high | 29 | bm25 | topic | 0.8966 | 0.9655 | 1.0000 | 1.0000 | 0.9397 |
| high | 29 | bm25 | clause | 0.7241 | — | — | — | — |
| high | 29 | dense | article | 0.6207 | 0.9310 | 0.9655 | 1.0000 | 0.7768 |
| high | 29 | dense | topic | 0.6207 | 0.9310 | 0.9655 | 1.0000 | 0.7845 |
| high | 29 | dense | clause | 0.5517 | — | — | — | — |
| high | 29 | hybrid | article | 0.8966 | 1.0000 | 1.0000 | 1.0000 | 0.9483 |
| high | 29 | hybrid | topic | 0.8966 | 1.0000 | 1.0000 | 1.0000 | 0.9483 |
| high | 29 | hybrid | clause | 0.7586 | — | — | — | — |
| All in-scope | 86 | random | article | 0.0392 | 0.1148 | 0.1866 | 0.3506 | 0.1083 |
| All in-scope | 86 | random | topic | 0.0508 | 0.1513 | 0.2477 | 0.4728 | 0.1435 |

## Paired 95% confidence intervals

| Slice | Level | Metric | Hybrid − BM25 | Lower | Upper |
|---|---|---|---:|---:|---:|
| All in-scope | article | mrr_at_10 | 0.0354 | 0.0058 | 0.0717 |
| All in-scope | article | hit_at_1 | 0.0581 | 0.0000 | 0.1279 |
| All in-scope | topic | mrr_at_10 | 0.0303 | 0.0029 | 0.0651 |
| All in-scope | topic | hit_at_1 | 0.0465 | 0.0000 | 0.1047 |
| low | article | mrr_at_10 | 0.0345 | -0.0172 | 0.1034 |
| low | article | hit_at_1 | 0.0690 | 0.0000 | 0.1724 |
| low | topic | mrr_at_10 | 0.0393 | -0.0057 | 0.1016 |
| low | topic | hit_at_1 | 0.0690 | 0.0000 | 0.1724 |
| medium | article | mrr_at_10 | 0.0461 | -0.0015 | 0.1042 |
| medium | article | hit_at_1 | 0.0714 | 0.0000 | 0.1786 |
| medium | topic | mrr_at_10 | 0.0435 | -0.0042 | 0.1048 |
| medium | topic | hit_at_1 | 0.0714 | 0.0000 | 0.1786 |
| high | article | mrr_at_10 | 0.0259 | -0.0345 | 0.0862 |
| high | article | hit_at_1 | 0.0345 | -0.0690 | 0.1379 |
| high | topic | mrr_at_10 | 0.0086 | -0.0431 | 0.0603 |
| high | topic | hit_at_1 | 0.0000 | -0.1034 | 0.1034 |

## Hybrid warnings

Coverage 0.6698 across 106 questions. False confidence 0.1500 (3/20).

| Group | All | In scope | Article Hit@1 | Topic Hit@1 |
|---|---:|---:|---:|---:|
| confident | 71 | 68 | 0.8235 | 0.8382 |
| warned | 35 | 18 | 0.6667 | 0.6667 |


The 71 queries marked confident include 68 in scope. Among those 68, the top result is wrong for 12 at article level (17.65%) and 11 at topic level (16.18%). At full coverage these rates are 18/86 (20.93%) and 17/86 (19.77%).

| Out-of-scope query marked confident | Top article | Cosine |
|---|---|---:|
| `d2-huy-review-016` | `hcmus-qcdt-2021:dieu-18` | 0.636530 |
| `d2-huy-review-029` | `hcmus-qcdt-2021:dieu-13` | 0.689995 |
| `d2-huy-review-052` | `hcmus-qcdt-2026:dieu-11` | 0.625617 |

See [summary.json](summary.json) for the group cutoffs, risk-coverage points and input hashes.

[E5 case analysis](../E5/d2-test.md) examines all three false-confidence cases and five article-level top-rank misses.

[Risk-coverage figure](risk-coverage.png)
