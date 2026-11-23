# Trợ lý tra cứu quy chế học vụ tiếng Việt (SimCSE)

Đồ án Lab 03 – Machine Learning, **Nhóm 14**, **Option 1: Practical Application**.
Ứng dụng tìm đúng **Điều/Khoản** trong quy chế đào tạo của Trường ĐH Khoa học Tự nhiên – ĐHQG-HCM cho câu hỏi tự nhiên của sinh viên, hiển thị đoạn văn bản kèm tên văn bản, số hiệu và phạm vi áp dụng.

> **Trạng thái:** đã tái hiện R1–R3, khớp paper (TB STS 81,58 / 76,25 / 56,70), và R4 (InfoNCE tự cài khớp `cl_forward`, lệch ≤ 1,4e-9 ở float64); **chưa có code ứng dụng và chưa có kết quả đánh giá ứng dụng**.
> Trạng thái chi tiết và việc tiếp theo: xem [PROJECT.md – Current Status](PROJECT.md#1-current-status).

## Thành viên

| MSSV | Họ tên | Phụ trách chính |
|---|---|---|
| 24127177 | Thái Quang Huy | Phương pháp SimCSE, tái hiện, so sánh thực nghiệm, báo cáo |
| 24127205 | Nguyễn Văn Minh | Dữ liệu tiếng Việt, truy hồi SimCSE-VN, ứng dụng, video |

Phân công chi tiết: [docs/PLAN.md](../PLAN.md).

## Bài toán

Sinh viên hỏi bằng lời thường, còn quy chế viết bằng thuật ngữ. Ví dụ thật trong bộ dữ liệu công khai ViRHE4QA (theo nội dung là quy chế ĐH CNTT; câu index 9542): *"Việc làm KLTN có thể bị dừng giữa chừng không?"*. Câu trả lời nằm ở Điều 6 "Báo cáo tiến độ thực hiện KLTN", và Điều này dùng chữ "đình chỉ", không có cụm "dừng giữa chừng". Ctrl+F hoặc tìm kiếm từ khóa chỉ khớp đúng từ, nên dễ bỏ sót. Chatbot sinh câu trả lời thì có thể "bịa" và không chỉ ra căn cứ.

**Mục tiêu:** trả về 3 Điều/Khoản liên quan nhất, kèm trích đoạn, tên văn bản, số hiệu, ngày ban hành và phạm vi áp dụng.
- Corpus gồm hai phiên bản Quy chế đào tạo: QĐ 1175/2021 và QĐ 3087/2026. Điều 27 của quy chế 2026 ghi: quy chế áp dụng cho các khóa tuyển từ năm học 2026–2027; đối với các khóa tuyển sinh từ năm 2025 trở về trước, Trường lựa chọn áp dụng quy định mới có lợi hơn cho người học. Vì vậy ứng dụng giữ cả hai bản và ghi rõ phạm vi áp dụng.
- Bản 2026 là bản ChatGPT chép từ bản scan và nhóm làm sạch lỗi OCR, không phải nguyên văn; ứng dụng ghi rõ điều này khi hiển thị.
- Khi độ tin cậy thấp, ứng dụng cảnh báo để người dùng tự đối chiếu.
- Hiệu quả được chứng minh bằng số liệu so với tìm kiếm từ khóa.

## Giải pháp

- **Encoder câu tiếng Việt huấn luyện theo SimCSE:** checkpoint cộng đồng `VoVanPhuc/sup-SimCSE-VietNamese-phobert-base`, dựa trên PhoBERT, cần tách từ bằng `pyvi`.
- **Truy hồi lai (hybrid):** BM25 cho khớp từ khóa, kết hợp SimCSE cho khớp ngữ nghĩa và câu hỏi diễn đạt khác văn bản.
- **Chunking theo cấu trúc văn bản:** chia theo Điều/Khoản, giữ metadata văn bản và phiên bản để trích dẫn chính xác.
- **Cảnh báo độ tin cậy thấp:** ngưỡng được chọn và đánh giá trên tập dev. Ngưỡng này không phải xác suất đúng.
- **Không dùng LLM sinh câu trả lời:** ứng dụng chỉ hiển thị đoạn văn bản có trong corpus kèm nguồn.

Phần tái hiện bài báo dùng mã nguồn chính thức [princeton-nlp/SimCSE](https://github.com/princeton-nlp/SimCSE) tại commit `235f89e0244b23673b69fbbc4a1cd9868c5a5c24`.

## Kiến trúc tổng quan

```
Quy chế đào tạo HCMUS (QĐ 1175/2021, QĐ 3087/2026) + data/d2/documents.yaml
   └─► Tách Điều/Khoản + metadata ─► Chuẩn hóa + tách từ (pyvi)
                                    ├─► BM25 index
                                    └─► SimCSE-VN embeddings (FAISS)
Câu hỏi ─► Chuẩn hóa + tách từ ─► BM25 + SimCSE ─► Kết hợp điểm ─► Xếp hạng theo Điều
   └─► Giao diện Gradio: top-3 Điều/Khoản · trích đoạn · văn bản/số hiệu/phạm vi áp dụng · cảnh báo tin cậy
```

Chi tiết xem [PROJECT.md §5](PROJECT.md#5-application-architecture--implementation).

## Công nghệ

Python · PyTorch · HuggingFace Transformers · pyvi · rank_bm25 · faiss-cpu · Gradio. Chạy được trên CPU; GPU chỉ cần cho phần mở rộng tùy chọn.

## Cài đặt và chạy

Chạy các lệnh từ thư mục gốc repo.

### Tái hiện kết quả SimCSE gốc (đã có)

Cần Python **3.9–3.11**, vì SentEval của repo gốc yêu cầu `numpy<1.24`. Script tự tạo venv, tải code SimCSE @ `235f89e`, dữ liệu STS và checkpoint, chạy `evaluation.py` gốc, rồi lưu kết quả cùng môi trường.

```bat
experiments\reproduction\run_r1.bat        :: R1: sup-simcse-bert-base-uncased (TB 81,58)
experiments\reproduction\run_r1.bat R2     :: unsup-simcse-bert-base-uncased (TB 76,25)
experiments\reproduction\run_r1.bat R3     :: bert-base-uncased chưa fine-tune (TB 56,70)
```

Trên Linux/macOS: `python3.11 experiments/reproduction/run_r1.py --exp R1`. Kết quả và môi trường: [experiments/reproduction/](../../experiments/reproduction/README.md).

### Ứng dụng và đánh giá (dự kiến)

> ⚠️ Các lệnh dưới đây là **dự kiến**. Sẽ được cập nhật và kiểm tra khi có code.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe data\prepare_virhe4qa.py          # tải và xử lý ViRHE4QA (bản con trong ViRE)
.\.venv\Scripts\python.exe apps\app.py                       # chạy ứng dụng demo
```

Corpus của ứng dụng cần toàn văn hai quy chế trong `data/raw/d2/`. Thư mục này **không có trong Git** cho tới khi rõ quyền công bố bản chép 2026 (Q7); xem [data/d2/](../../data/d2/README.md).

## Dữ liệu

| Bộ dữ liệu | Vai trò | Nguồn |
|---|---|---|
| ViRHE4QA (bản con 1.000 câu hỏi trong benchmark ViRE) | Đánh giá chính trên dataset mới (D1), trên corpus riêng của bộ dữ liệu (quy chế ĐH CNTT) | [ViRHE4QA_v2.csv @ ViRE `60ea715`](https://github.com/longstnguyen/ViRE/blob/60ea7155134eaa426ab1d0a82d2bbbf327d1b470/data/ViRHE4QA_v2.csv), bài báo gốc R2GQA ([arXiv:2409.02840](https://arxiv.org/abs/2409.02840)) |
| D2: quy chế đào tạo HCMUS (QĐ 1175/2021, QĐ 3087/2026) + bộ câu hỏi nhóm tự gán nhãn | Corpus của ứng dụng; đánh giá trong bối cảnh thực tế, có câu ngoài phạm vi (chỉ dùng để test) | Nhóm tự xây dựng; mô tả ở [data/d2/](../../data/d2/README.md) |
| STS 2012–2016, STS-B, SICK-R | Tái hiện kết quả bài báo | Script của repo SimCSE |

Điều kiện sử dụng từng bộ dữ liệu xem [PROJECT.md §6](PROJECT.md#6-datasets--experimental-evaluation).

## Tài liệu dự án

- **[PROJECT.md](PROJECT.md)**: đặc tả và trạng thái (phạm vi, ánh xạ yêu cầu Lab 03, nền tảng SimCSE, kiến trúc, thí nghiệm, rủi ro).
- **[docs/PLAN.md](../PLAN.md)**: checklist và phân công.

## Tham khảo

- T. Gao, X. Yao, D. Chen. *SimCSE: Simple Contrastive Learning of Sentence Embeddings.* EMNLP 2021, pp. 6894–6910. <https://aclanthology.org/2021.emnlp-main.552/>
- Mã nguồn: <https://github.com/princeton-nlp/SimCSE/tree/235f89e0244b23673b69fbbc4a1cd9868c5a5c24>
- Trường ĐH Khoa học Tự nhiên, ĐHQG-HCM. *Quy chế đào tạo trình độ đại học*, ban hành kèm QĐ 1175/QĐ-KHTN ngày 24/9/2021. <https://www.ctda.hcmus.edu.vn/wp-content/uploads/2023/03/Quy-che-dao-tao-2021.pdf>
- Trường ĐH Khoa học Tự nhiên, ĐHQG-HCM. *Quy chế đào tạo trình độ đại học*, ban hành kèm QĐ 3087/QĐ-KHTN ngày 29/9/2026 (bản scan, chưa thấy đăng công khai).
