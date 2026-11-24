# SimCSE · Machine Learning Lab 03

Đồ án nghiên cứu **SimCSE** và xây dựng trợ lý tra cứu quy chế học vụ tiếng Việt theo **Option 1 – Practical Application**. Nhóm sẽ so sánh BM25, SimCSE-VN và truy hồi lai trên tác vụ tìm Điều/Khoản từ câu hỏi của sinh viên. Tiến độ và phân công được theo dõi trong [checklist đồ án](docs/PLAN.md).

## Bản đồ repo

```text
apps/                       Giao diện hoặc demo tương tác của ứng dụng
src/simcse_lab/             Package Python dùng chung
    model/                  Mã hóa câu, pooling và logic huấn luyện SimCSE
    evaluation/             Cách tính chỉ số dùng lại giữa các thí nghiệm
experiments/
    reproduction/           Tái hiện một kết quả cụ thể của paper
    external_dataset/       Kiểm tra mô hình trên dữ liệu paper chưa dùng
    application/            So sánh ứng dụng với giải pháp hiện có
data/                       Nguồn, cách chuẩn bị dữ liệu và tạo các tập chia
docs/                       Báo cáo IEEE và tài liệu phục vụ video demo
pyproject.toml              Cấu hình package Python
```

## Luồng làm việc

1. **Từ dữ liệu đến embedding.** Mô tả nguồn và cách chia dữ liệu trong [data/](data/README.md). Đặt logic mã hóa câu trong `src/simcse_lab/model/` để thí nghiệm và demo dùng cùng cách tokenize, pooling và suy luận.
2. **Từ embedding đến kết quả nghiên cứu.** Chọn một mốc của paper trong [reproduction/](experiments/reproduction/README.md), sau đó thực hiện [đánh giá trên dữ liệu mới](experiments/external_dataset/README.md). Gắn mỗi bảng kết quả với cấu hình và lệnh đã tạo ra nó.
3. **Từ mô hình đến ứng dụng.** Xác định người dùng và tác vụ trong [apps/](apps/README.md). Lưu cách so sánh với giải pháp hiện có cùng bằng chứng thực nghiệm trong [experiments/application/](experiments/application/README.md).
4. **Từ kết quả đến bài nộp.** Dùng các kết quả đã kiểm chứng cho [báo cáo và video](docs/README.md). Khi có mã thực thi, bổ sung lệnh chạy thí nghiệm và demo tại README này.

## Cài package ở chế độ phát triển

Chạy từ thư mục gốc bằng PowerShell trên Windows.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -c "import simcse_lab; print(simcse_lab.__file__)"
```

Trên Linux hoặc macOS, dùng `.venv/bin/python` thay cho `.\.venv\Scripts\python.exe`. Package khai báo PyTorch để chạy InfoNCE. Tùy chọn `[test]` cài thêm pytest.

## Tái hiện kết quả SimCSE

Đã đánh giá lại ba checkpoint công khai bằng `evaluation.py` gốc @ `235f89e`. Trung bình Spearman trên 7 tác vụ STS: **81,58** (sup SimCSE), **76,25** (unsup SimCSE), **56,70** (BERT chưa fine-tune), khớp Table 5 của paper. Bảng chi tiết, môi trường và sai lệch phiên bản: [experiments/reproduction/](experiments/reproduction/README.md).

Đã tự cài lại InfoNCE (R4) và kiểm thử đối chiếu với `cl_forward` của code gốc. Ở float64, mức lệch ≤ 1,4e-9.

```powershell
experiments\reproduction\run_r1.bat                     # R1, thêm R2 hoặc R3 nếu cần. Python 3.9–3.11
.\.venv\Scripts\python.exe -m pytest tests -q            # Toàn bộ bộ test
.\.venv\Scripts\python.exe experiments\reproduction\run_r4.py  # R4, kết quả mới ở outputs/reproduction/
```

## Tài liệu gốc

Tianyu Gao, Xingcheng Yao và Danqi Chen. *SimCSE: Simple Contrastive Learning of Sentence Embeddings*. EMNLP 2021. [Paper](https://aclanthology.org/2021.emnlp-main.552/) · [Mã nguồn của tác giả](https://github.com/princeton-nlp/SimCSE)
