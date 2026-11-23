# Tái hiện kết quả SimCSE (R1–R3)

**Phạm vi:** đánh giá lại các checkpoint công khai của tác giả bằng `evaluation.py` gốc của [princeton-nlp/SimCSE](https://github.com/princeton-nlp/SimCSE/tree/235f89e0244b23673b69fbbc4a1cd9868c5a5c24) tại commit `235f89e`. Không huấn luyện lại mô hình.

**Mốc so sánh:** paper Table 5 và bảng kết quả trong README của repo gốc.

**Giao thức:** Spearman × 100 giữa cosine của từng cặp câu và nhãn, gộp theo setting "all", không dùng regressor, tính trên tập test của 7 tác vụ STS.

## Cách chạy

```bat
:: Windows (từ bất kỳ đâu; script tự chuyển về thư mục gốc repo)
experiments\reproduction\run_r1.bat        :: R1
experiments\reproduction\run_r1.bat R2
experiments\reproduction\run_r1.bat R3
```

Trên Linux/macOS: `python3.11 experiments/reproduction/run_r1.py --exp R1`. Cần Python 3.9–3.11.

Script tự làm các bước sau, bước nào đã có sẵn thì bỏ qua:

1. Lấy code gốc @ `235f89e` vào `SimCSE/`. Thư mục này nằm trong `.gitignore`.
2. Tạo `.venv-repro` ở thư mục gốc và cài `requirements-r1.txt`.
3. Tải dữ liệu STS (`senteval.tar`, khoảng 90 MB).
4. Gọi nguyên bản `evaluation.py`.
5. Ghi `results/<exp>/`:
   - `metrics.json`: điểm và chênh lệch so với README/paper.
   - `env.txt`, `pip_freeze.txt`, `eval_log.txt`, `status.txt`.

| Exp | Checkpoint | Pooler |
|---|---|---|
| R1 | `princeton-nlp/sup-simcse-bert-base-uncased` | `cls` |
| R2 | `princeton-nlp/unsup-simcse-bert-base-uncased` | `cls_before_pooler` |
| R3 | `bert-base-uncased` (chưa fine-tune, baseline) | `avg_first_last` |

## Kết quả (23/11/2026)

| Exp | | STS12 | STS13 | STS14 | STS15 | STS16 | STS-B | SICK-R | **TB** |
|---|---|---|---|---|---|---|---|---|---|
| R1 | Nhóm | 75,30 | 84,67 | 80,19 | 85,40 | 80,82 | 84,26 | 80,39 | **81,58** |
| | Paper | 75,30 | 84,67 | 80,19 | 85,40 | 80,82 | 84,25 | 80,39 | 81,57 |
| R2 | Nhóm | 68,40 | 82,41 | 74,38 | 80,91 | 78,56 | 76,85 | 72,23 | **76,25** |
| | Paper | 68,40 | 82,41 | 74,38 | 80,91 | 78,56 | 76,85 | 72,23 | 76,25 |
| R3 | Nhóm | 39,70 | 59,37 | 49,67 | 66,03 | 66,19 | 53,88 | 62,06 | **56,70** |
| | Paper | 39,70 | 59,38 | 49,67 | 66,03 | 66,19 | 53,87 | 62,06 | 56,70 |

**Nhận xét**

- **Cả ba thí nghiệm đều khớp.** Mọi chênh lệch đều ≤ 0,01. R1 trùng tuyệt đối với README repo; chỉ lệch 0,01 so với paper vì paper ghi STS-B là 84,25, còn README ghi 84,26.
- **Thứ tự chất lượng của paper được tái hiện đúng:** BERT thô 56,70 → unsup SimCSE 76,25 → sup SimCSE 81,58.
- **Về pooler `avg_first_last` (R3):** tại commit này, "first" là `hidden_states[0]`, tức output của lớp embedding. R3 ra đúng 56,70, nên số của paper được tính đúng theo cách này.

## Môi trường

| Thông tin | Giá trị |
|---|---|
| Máy | Windows (build 26300), CPU AMD 16 luồng, không dùng GPU (`cuda_available: False`) |
| Phần mềm | Python 3.11.9 · torch 2.5.1+cpu · transformers 4.46.3 · numpy 1.23.5 · scipy 1.10.1 · scikit-learn 1.2.2 |
| Thời gian đánh giá | Khoảng 15 phút mỗi thí nghiệm (868 / 908 / 904 giây) |
| Revision checkpoint | R1 `2d82fab`, R2 `218baf6`, R3 `86b5e09` (đầy đủ trong `env.txt`) |

**Sai lệch so với repo gốc**

- Repo pin `transformers==4.2.1`, `scipy==1.5.4`, `scikit-learn==0.24.0` và khuyên dùng torch 1.7.1. Các bản này không cài được trên Python 3.11/Windows.
- Nhóm dùng các bản ở bảng trên. Kết quả khớp README cho thấy khác biệt phiên bản không ảnh hưởng tới phép đánh giá này.
- Bắt buộc dùng `numpy<1.24`. Lý do: `SentEval/senteval/sts.py` tạo `np.array` từ danh sách câu có độ dài khác nhau, và numpy ≥ 1.24 báo lỗi ở chỗ này.

**Ghi chú đường dẫn**

- R1–R3 được chạy ở thư mục cũ `D:\Lab03_Group14\repro\` trước khi chuyển vào repo. Vì vậy `status.txt` và `env.txt` vẫn ghi đường dẫn cũ.
- Code chỉ được cập nhật đường dẫn cho cấu trúc mới. Bản đã cập nhật được chạy thử trên dữ liệu giả, không phải chạy lại thật.

Phân tích phương pháp và kế hoạch đầy đủ: [docs/application/PROJECT.md §4](../../docs/application/PROJECT.md#4-simcse-research-foundation).
