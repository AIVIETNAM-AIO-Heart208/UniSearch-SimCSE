# Đánh giá truy hồi trên ViRHE4QA (D1)

D1 dùng 1.000 dòng từ [ViRHE4QA_v2.csv trong ViRE](https://github.com/longstnguyen/ViRE/blob/60ea7155134eaa426ab1d0a82d2bbbf327d1b470/data/ViRHE4QA_v2.csv). SHA-256 là `23fb969985150599d3ad0b5229d039b8541ed335fbc29dcfa0b0d733ccaa5682`. Script đọc được CSV local qua `--input` và kiểm tra đúng phiên bản trước khi xuất JSONL.

## Chạy từ thư mục gốc bằng PowerShell

Cấu hình D1-dev ban đầu của Minh là Windows, Python 3.13.9, PyTorch 2.14.1+cu126 ở chế độ CPU, Transformers 5.15.1 và NumPy 2.5.5. Các lệnh dưới dùng Python 3.13. Khi tái lập lượt test của Huy, dùng các phiên bản đã ghi cho [D1-test](results/E1/d1-test.json) và [D2-test](../application/results/D2/summary.json), rồi đối chiếu SHA-256 của từng run.

```powershell
py -3.13 -m venv .venv
$d1Python = '.\.venv\Scripts\python.exe'
& $d1Python -m pip install -e . 'torch==2.14.1' 'transformers==5.15.1' 'numpy==2.5.5' 'pyvi==0.1.1' 'scikit-learn==1.9.1' 'sklearn-crfsuite==0.5.0' 'python-crfsuite==0.9.12'
New-Item -ItemType Directory -Force data/raw/d1 | Out-Null
Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/longstnguyen/ViRE/60ea7155134eaa426ab1d0a82d2bbbf327d1b470/data/ViRHE4QA_v2.csv' -OutFile data/raw/d1/ViRHE4QA_v2.csv
& $d1Python data/prepare_virhe4qa.py
& $d1Python -c "from huggingface_hub import snapshot_download; snapshot_download('VoVanPhuc/sup-SimCSE-VietNamese-phobert-base', revision='608779b86741a8acd8c8d38132974ff04086b138', local_dir='outputs/d1-model', ignore_patterns=['pytorch_model.bin'])"
& $d1Python experiments/external_dataset/run_dense_dev.py --model-path outputs/d1-model --output outputs/d1-rerun
```

Model và tokenizer cùng lấy tại [revision 608779b](https://huggingface.co/VoVanPhuc/sup-SimCSE-VietNamese-phobert-base/tree/608779b86741a8acd8c8d38132974ff04086b138). Model card dùng `pooler_output`. Transformers báo hai tensor `mlp.dense.*` dư khi nạp checkpoint vào `RobertaModel`.

Để kiểm tra công thức bằng các thứ hạng đã biết và kiểm tra MaxP, cài `pytest` rồi chạy `python -m pytest -q tests/test_d1_dense.py tests/test_stats.py`.

## Bàn giao cho Huy

Mở [manifest D1-dev](results/D1-dev-retrieval-check/manifest.json) để xem cấu hình, SHA-256 và điểm của từng run. Run BM25 và Hybrid nằm trong [gói kiểm tra](results/D1-dev-retrieval-check/runs/). Run dense dùng [bản Phase 2 đã xác minh](results/D1-dev/runs/dense.jsonl). Hybrid dùng λ = 0,5 để kiểm tra pipeline. Để quét các giá trị λ khác, phép trộn cần điểm trên toàn bộ corpus trước khi cắt top 20.

Bộ xuất JSONL ghi xuống dòng LF theo `.gitattributes`. Manifest ghi SHA-256 của các file LF trong Git. Trường `verification.ranking_sha256` trong [kết quả Dense](results/D1-dev/metrics.json) ghi SHA-256 của đầu ra CRLF dùng trong lần đối chiếu ban đầu trên Windows.

Sau khi chuẩn bị `data/processed/d1/` bằng `prepare_virhe4qa.py`, chạy từ gốc repo để tính lại chỉ số, đối chiếu SHA-256, ID và thứ tự. Nếu đã có file chunk từ Phase 2, thêm `--chunks data/processed/d1/dense/corpus.jsonl` để kiểm tra từng ID với catalog.

```powershell
$env:PYTHONPATH = 'src'
& $d1Python -m experiments.external_dataset.run_retrieval verify-d1-dev --manifest experiments/external_dataset/results/D1-dev-retrieval-check/manifest.json
```

## Truy hồi Phase 3

Dùng môi trường D1 ở trên và cài thêm các phần phụ thuộc truy hồi. Các lệnh chạy từ gốc repo. Mỗi lần chạy dùng một thư mục đầu ra mới.

```powershell
& $d1Python -m pip install -e ".[retrieval,evaluation]"
& $d1Python experiments/external_dataset/run_retrieval.py run --corpus d1 --chunks data/processed/d1/dense/corpus.jsonl --queries data/processed/d1/queries.jsonl --split dev --methods bm25 dense hybrid --weight 0.5 --model-path outputs/d1-model --output outputs/d1-dev-check
```

`--weight` là trọng số BM25. Lần kiểm tra trên 224 câu dùng `0.5`. Mỗi run lưu top 20 Điều. Bảng dưới dùng thang 0–1. Run dense trùng SHA-256 với run Phase 2 đã lưu.

| Phương pháp | Hit@1 | Hit@3 | MRR@10 |
|---|---:|---:|---:|
| BM25 | 0,665179 | 0,808036 | 0,749676 |
| Dense | 0,464286 | 0,656250 | 0,582836 |
| Hybrid (λ = 0,5, kiểm tra) | 0,665179 | 0,861607 | 0,768789 |

[Ghi chú E0](results/E0/d1-dev.md) đối chiếu điểm BM25 từng chunk và thứ tự top 20 cho câu 9542 trên D1-dev.

Khi đo E4, dùng `RetrievalIndex.rank_bm25(question)` để đo đường tách từ và xếp hạng BM25 riêng. Đường xuất run dùng cosine của chunk được BM25 chọn cho trường `top1_dense_cos`. Nếu đo chức năng có cảnh báo, ghi riêng thời gian mã hóa và tính cosine.

### Chốt cấu hình bằng D1-dev

[Phiếu bàn giao cho Minh](results/D1-dev-tuning/handoff.md) ghi tham số demo, bảng so sánh và độ bao phủ. [Kết quả quét](results/D1-dev-tuning/summary.json) ghi cả 11 mức trọng số, checkpoint, checksum và môi trường thực chạy.

Từ gốc repo, dùng môi trường truy hồi với các phiên bản trong kết quả quét và nhập đúng đường dẫn CSV đã kiểm SHA-256.

```powershell
$env:PYTHONPATH = 'src'
& $d1Python -m experiments.external_dataset.tune_d1_dev --input data/raw/d1/ViRHE4QA_v2.csv --model-path outputs/d1-model --output outputs/d1-dev-tuning-rerun
```

`scores.npz` chứa hai ma trận `bm25` và `cosine`. Hàng theo `qids` và cột theo `chunk_ids`, với `article_ids` lưu đoạn nguồn của từng cột. Đọc bằng `numpy.load(..., allow_pickle=False)`. Script đọc lại bảng điểm trước khi quét và ghi `selected.jsonl` với top 20 của cấu hình được chọn.

### Đánh giá D1-test

[Bảng kết quả D1-test](results/E1/d1-test.md) và [dữ liệu kết quả, cấu hình](results/E1/d1-test.json) ghi kết quả ba phương pháp trên 759 câu test, khoảng tin cậy Hybrid so với BM25 và số liệu cảnh báo của Hybrid.

[So sánh theo mức trùng từ E2 trên D1-test](../application/results/E2/d1-test.md) tính chỉ số từng nhóm từ cùng ba bảng xếp hạng.

[Phân tích lỗi E5 trên D1-test](../application/results/E5/d1-test.md) đối chiếu các trường hợp Hybrid trượt Hit@1 và ví dụ Hybrid đưa đoạn chuẩn lên đầu.

Chạy từ gốc repo với môi trường truy hồi, CSV đúng checksum và checkpoint đã ghim. Chọn đường dẫn CSV thực tế và thư mục đầu ra mới.

```powershell
$env:HF_HUB_OFFLINE = '1'
& $d1Python -m experiments.external_dataset.evaluate_d1_test --input data/raw/d1/ViRHE4QA_v2.csv --model-path outputs/d1-model --output outputs/d1-test-rerun
```

Script lấy trọng số và ngưỡng từ [kết quả D1-dev](results/D1-dev-tuning/summary.json). Script dựng lại chunk và chia tập từ CSV, lưu corpus cùng các câu test vào `inputs/`, rồi lưu top 20 đoạn nguồn mỗi câu vào `retrieval/runs/`. Sau khi kiểm xong, lệnh xuất `summary.json` với Hit@1/3/5/10, MRR@10, khoảng tin cậy, độ bao phủ và SHA-256 của các đầu vào. Truyền file này cho E2 và E3 bằng `--e1-summary`.

### Biểu đồ risk–coverage D1-test

[Biểu đồ PNG](results/E3/d1-test-risk-coverage.png), [bản vector dùng trong báo cáo](../../docs/report/figures/d1-test-risk-coverage.pdf) và [dữ liệu đường cong](results/E3/d1-test.json) lấy từ xếp hạng Hybrid cùng nhãn chuẩn đã lưu ở lượt E1. Script kiểm SHA-256 và dùng ngưỡng đã chốt ghi trong E1. Các điểm trên đường cong dùng cosine của chunk trích dẫn ở hạng đầu. Cách tính độ bao phủ và risk ở [PROJECT §6.3](../../docs/application/PROJECT.md#63-baseline-và-metrics).

Chạy từ gốc repo bằng môi trường Python có Matplotlib. Lượt tạo hình dùng Matplotlib 3.11.1. Lệnh đọc các tệp D1-test đã lưu và ghi kết quả vào thư mục mới.

```powershell
$env:PYTHONPATH = 'src'
& $d1Python -m experiments.external_dataset.plot_d1_risk_coverage --e1-summary outputs/d1-test-rerun/summary.json --output outputs/d1-test-risk-coverage-rerun
```

### Lệnh chuẩn bị HCMUS và đánh giá D2

Khi đã có bản `_clean.md` đúng SHA-256, chạy `python data/d2/prepare_2026.py` để tạo bản verified. Nếu bản verified đã có đúng SHA-256, chạy thẳng lệnh chuẩn bị corpus. Có thể thêm `--only-2021` để kiểm tra nguồn 2021 bằng một thư mục đầu ra riêng. Trong Git, đích phải là thư mục mới bên trong repo, được Git bỏ qua và chưa được theo dõi. Trong mã nguồn giải nén, dùng một thư mục con mới dưới `data/processed/` hoặc `outputs/`. Ví dụ, `--output data/processed/rebuilt` cho phép đối chiếu với corpus đi kèm.

```powershell
& $d1Python experiments/external_dataset/run_retrieval.py prepare-hcmus --model-path outputs/d1-model --output data/processed/d2
```

Nếu `data/processed/d2/corpus.jsonl` đã được tạo từ đúng hai nguồn và checkpoint đã ghim, dùng lại file đó. D2 dùng [nhãn đã chốt](../../data/d2/queries_d2.jsonl), áp dụng trọng số trong [cấu hình D1-dev](results/D1-dev-tuning/handoff.md) và lưu toàn bộ 51 Điều.

```powershell
$hybridWeight = '0.6'
& $d1Python experiments/external_dataset/run_retrieval.py run --corpus hcmus --chunks data/processed/d2/corpus.jsonl --queries data/d2/queries_d2.jsonl --split test --methods bm25 dense hybrid --weight $hybridWeight --model-path outputs/d1-model --output outputs/d2-test
```

`summary.json` của lượt truy hồi HCMUS lưu SHA-256 của file corpus, nhãn và từng bảng xếp hạng. Dùng [lệnh chấm D2-test](../application/README.md#chấm-d2-test) để tính chỉ số theo Điều, chủ đề và Khoản, phân nhóm E2 và đánh giá cảnh báo E3 từ các file vừa lưu.

[Kết quả D2 đã kiểm chứng](../application/results/D2/d2-test.md) dùng cấu hình D1-dev. [Bản ghi chạy](../application/results/D2/summary.json) lưu lệnh, môi trường và checksum của ba bảng xếp hạng.

## Đầu ra và giao thức

- `data/processed/d1/corpus.jsonl` giữ nguyên văn từng đoạn nguồn. `queries.jsonl` giữ qid gốc và mã đoạn đúng. `split.json` ghi nguồn, SHA-256, seed, 17 dòng lặp đã bỏ và số câu theo split. Bốn câu có qid `9512`, `9538`, `9539`, `9542` thuộc cùng nhóm dev.
- `data/processed/d1/dense/corpus.jsonl` lưu các chunk có offset ký tự tính trên từng context gốc. Script chuẩn hóa Unicode và dấu thanh, tách từ bằng pyvi, rồi chia cửa sổ có phần giao tối đa 24 từ gốc cho các đoạn dài. Mỗi đầu vào có tối đa 256 token kể cả token đặc biệt.
- [Xếp hạng D1-dev](results/D1-dev/runs/dense.jsonl) lưu top 20 đoạn nguồn phân biệt mỗi câu. NumPy tính cosine trên vector L2, rồi MaxP lấy điểm cao nhất trên các chunk của từng đoạn nguồn. Nếu bằng điểm, ưu tiên mã tăng dần.
- [Bảng điểm và cấu hình thực chạy](results/D1-dev/metrics.json) ghi Hit@1, Hit@3 và MRR@10 theo thang 0–1. Ví dụ trong trường `example` chỉ ra qid, đoạn đúng, hạng và offset để đối chiếu với corpus. Script tính lại điểm từ file run đã lưu.

Nhóm chia câu hỏi theo đoạn nguồn trước khi chốt cấu hình trên D1-dev và đánh giá D1-test, theo giao thức của đồ án.
