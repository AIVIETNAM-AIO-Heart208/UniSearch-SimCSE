# SimCSE · Machine Learning Lab 03

Đồ án nghiên cứu **SimCSE** và xây dựng trợ lý tra cứu quy chế học vụ tiếng Việt theo **Option 1 – Practical Application**. Nhóm đã so sánh BM25, SimCSE-VN và truy hồi lai trên [D1-test](experiments/external_dataset/results/E1/d1-test.md) và [D2-test quy chế HCMUS](experiments/application/results/D2/d2-test.md). Tiến độ và phân công được theo dõi trong [checklist đồ án](docs/PLAN.md).

**Bài nộp Nhóm 14.** Hồ sơ đã có PDF, mã nguồn và corpus. Minh quay video chính thức từ bộ slide và ảnh thao tác đã bàn giao. [Tư liệu quay và các lệnh kiểm, đóng gói](docs/README.md#báo-cáo-và-video)

## Bản đồ repo

```text
apps/                       Giao diện tra cứu quy chế đào tạo HCMUS
src/simcse_lab/             Package Python dùng chung
    model/                  Mã hóa câu, pooling và logic huấn luyện SimCSE
    retrieval/              Chia đoạn theo Điều/Khoản, lập chỉ mục và xếp hạng
    regulation_excerpts.py   Trình bày trích đoạn, bảng và công thức của quy chế
    evaluation/             Cách tính chỉ số dùng lại giữa các thí nghiệm
experiments/
    reproduction/           Tái hiện một kết quả cụ thể của paper
    external_dataset/       Kiểm tra mô hình trên dữ liệu paper chưa dùng
    application/            So sánh ứng dụng với giải pháp hiện có
data/                       Nguồn, cách chuẩn bị dữ liệu và tạo các tập chia
docs/                       Báo cáo IEEE và tài liệu phục vụ video demo
pyproject.toml              Cấu hình package Python
```

## Chạy từ bản clone

- **Kiểm tra mã và tài liệu.** Tạo môi trường như bên dưới, sau đó chạy `python -X utf8 tools/check_docs.py` và `.\.venv\Scripts\python.exe -m pytest tests -q -rs`. Để chạy cả kiểm thử truy hồi và endpoint Gradio cục bộ trên Windows, dùng Python 3.11 và cài `.[test,retrieval,evaluation,demo]` vào cùng môi trường.
- **D1.** [Hướng dẫn D1](experiments/external_dataset/README.md) có lệnh lấy CSV và checkpoint theo phiên bản, kiểm ba bảng xếp hạng dev và chạy E1 trên test. Dùng đầu ra E1 để [chấm theo mức trùng từ](experiments/application/README.md#e2-trên-d1-test) và [vẽ đường cong cảnh báo](experiments/external_dataset/README.md#biểu-đồ-riskcoverage-d1-test).
- **Demo và D2.** Tải [bộ D2 công khai dùng trong bài nộp](data/d2/README.md#bộ-d2-công-khai). Để chạy demo hoặc chấm D2-test, chuẩn bị [nguồn quy chế](data/d2/README.md#file) và [corpus HCMUS](experiments/external_dataset/README.md#lệnh-chuẩn-bị-hcmus-và-đánh-giá-d2), rồi [mở giao diện Gradio](apps/README.md) hoặc [chạy bộ chấm](experiments/application/README.md#chấm-d2-test). Corpus đầy đủ cần bản chép quy chế 2026 trong gói bàn giao. Bản clone công khai cho phép kiểm riêng quy chế 2021 bằng `--only-2021`.
- **Báo cáo.** Chạy `powershell -ExecutionPolicy Bypass -File docs\report\build.ps1`. PDF nằm ở `docs/report/build/main.pdf`. [Yêu cầu LaTeX](docs/report/README.md) · [Checklist rà soát](docs/reviews/workspace.md).

[Phép thử trên 16 câu phát triển HCMUS](experiments/application/results/clause-scope-pilot/comparison.md) ghi Khoản được chọn, cảnh báo và đoạn sinh viên thấy ngay cho bản hiện tại và ba bản thử.
Lượt [so sánh cách mở phiên bản được hỏi](experiments/application/results/edition-display-pilot/comparison.md) dùng lại đúng các xếp hạng Hybrid để đo riêng phần hiển thị.
Đã [chạy thử hai cách chọn khóa trên K24, K26 và tra cứu chung](experiments/application/results/cohort-walkthrough/comparison.md). [Gói mô phỏng ngoại tuyến](experiments/application/README.md#mô-phỏng-hai-cách-chọn-khóa) dùng cùng bộ câu hỏi.

## Cài package ở chế độ phát triển

Chạy từ thư mục gốc bằng PowerShell trên Windows.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -c "import simcse_lab; print(simcse_lab.__file__)"
```

Trên Linux hoặc macOS, tạo môi trường bằng `python3.11 -m venv .venv` rồi dùng `.venv/bin/python`. Package dùng PyTorch để chạy InfoNCE. Tùy chọn `[test]` cài pytest, NumPy và PyYAML. Tùy chọn `[evaluation]` cung cấp Matplotlib cho các lệnh vẽ E3.

## Tái hiện kết quả SimCSE

Đã đánh giá ba checkpoint bằng `evaluation.py` gốc tại `235f89e`. Trên 7 tác vụ STS, SimCSE có giám sát đạt trung bình **81,58** điểm Spearman × 100, bằng README của tác giả và cao hơn **0,01** điểm so với Bảng 5 của bài báo (81,57). SimCSE không giám sát đạt **76,25** và BERT chưa tinh chỉnh đạt **56,70**, bằng hai trung bình công bố. [Bảng đối chiếu và môi trường](experiments/reproduction/README.md)

Đã tự cài lại InfoNCE (R4) và kiểm thử đối chiếu với `cl_forward` của code gốc. Ở float64, mức lệch ≤ 1,4e-9.

```powershell
experiments\reproduction\run_r1.bat                     # R1, thêm R2 hoặc R3 nếu cần. Python 3.9–3.11
.\.venv\Scripts\python.exe -m pytest tests -q            # Toàn bộ bộ test
.\.venv\Scripts\python.exe experiments\reproduction\run_r4.py  # R4, kết quả mới ở outputs/reproduction/
```

## Tài liệu gốc

Tianyu Gao, Xingcheng Yao và Danqi Chen. *SimCSE: Simple Contrastive Learning of Sentence Embeddings*. EMNLP 2021. [Paper](https://aclanthology.org/2021.emnlp-main.552/) · [Mã nguồn của tác giả](https://github.com/princeton-nlp/SimCSE)
