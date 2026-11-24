# Đánh giá truy hồi trên ViRHE4QA (D1)

D1 dùng 1.000 dòng từ [ViRHE4QA_v2.csv trong ViRE](https://github.com/longstnguyen/ViRE/blob/60ea7155134eaa426ab1d0a82d2bbbf327d1b470/data/ViRHE4QA_v2.csv). SHA-256 là `23fb969985150599d3ad0b5229d039b8541ed335fbc29dcfa0b0d733ccaa5682`. Script đọc được CSV local qua `--input` và kiểm tra đúng phiên bản trước khi xuất JSONL.

## Chạy từ thư mục gốc bằng PowerShell

Cấu hình đã chạy là Windows, Python 3.13.9, PyTorch 2.14.1+cu126 ở chế độ CPU, Transformers 5.15.1 và NumPy 2.5.5. Chạy lệnh tạo môi trường với Python 3.13.

```powershell
python -m venv .venv
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

## Đầu ra và giao thức

- `data/processed/d1/corpus.jsonl` giữ nguyên văn từng đoạn nguồn. `queries.jsonl` giữ qid gốc và mã đoạn đúng. `split.json` ghi nguồn, SHA-256, seed, 17 dòng lặp đã bỏ và số câu theo split. Bốn câu có qid `9512`, `9538`, `9539`, `9542` thuộc cùng nhóm dev.
- `data/processed/d1/dense/corpus.jsonl` lưu các chunk có offset ký tự tính trên từng context gốc. Script chuẩn hóa Unicode và dấu thanh, tách từ bằng pyvi, rồi chia cửa sổ có phần giao tối đa 24 từ gốc cho các đoạn dài. Mỗi đầu vào có tối đa 256 token kể cả token đặc biệt.
- [Xếp hạng D1-dev](results/D1-dev/runs/dense.jsonl) lưu top 20 đoạn nguồn phân biệt mỗi câu. NumPy tính cosine trên vector L2, rồi MaxP lấy điểm cao nhất trên các chunk của từng đoạn nguồn. Nếu bằng điểm, ưu tiên mã tăng dần.
- [Bảng điểm và cấu hình thực chạy](results/D1-dev/metrics.json) ghi Hit@1, Hit@3 và MRR@10 theo thang 0–1. Ví dụ trong trường `example` chỉ ra qid, đoạn đúng, hạng và offset để đối chiếu với corpus. Script tính lại điểm từ file run đã lưu.

Kết quả này dùng cho D1-dev. Giao thức khác ViRE công bố do nhóm chia câu hỏi theo nguồn. D1-test được đánh giá ở E1 sau khi nhóm chốt tiền xử lý và cấu hình Hybrid.
