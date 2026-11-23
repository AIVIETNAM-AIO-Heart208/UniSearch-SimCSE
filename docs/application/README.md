# Trợ lý tra cứu quy chế học vụ tiếng Việt (SimCSE)

Đồ án Lab 03 – Machine Learning, **Option 1: Practical Application**.
Ứng dụng tìm đúng **Điều/Khoản** trong văn bản quy chế học vụ cho câu hỏi tự nhiên của sinh viên, hiển thị nguyên văn kèm nguồn và phiên bản văn bản.

> **Trạng thái:** đang ở giai đoạn thiết kế, **chưa có code và chưa có kết quả thực nghiệm**.
> Trạng thái chi tiết và việc tiếp theo: xem [PROJECT.md – Current Status](PROJECT.md#1-current-status).

## Thành viên

| MSSV | Họ tên | Phụ trách chính |
|---|---|---|
| 24127177 | Thái Quang Huy | Phân tích SimCSE, tái hiện kết quả, đánh giá thực nghiệm |
| 24127205 | Nguyễn Văn Minh | Dữ liệu quy chế, pipeline truy hồi, ứng dụng demo |

## Bài toán

Sinh viên thường hỏi những câu như *"rớt bao nhiêu tín chỉ thì bị cảnh báo học vụ?"*. Câu trả lời nằm trong các file PDF quy chế dài, nhưng cách hỏi lại khác cách văn bản viết. Ctrl+F hoặc tìm kiếm từ khóa chỉ khớp đúng từ, nên dễ bỏ sót. Chatbot sinh câu trả lời thì có thể "bịa" và không chỉ ra căn cứ.

**Mục tiêu:** trả về 3 Điều/Khoản liên quan nhất, kèm trích đoạn gốc, tên văn bản, số hiệu và ngày ban hành. Khi độ tin cậy thấp, ứng dụng cảnh báo để người dùng tự đối chiếu. Hiệu quả được chứng minh bằng số liệu so với tìm kiếm từ khóa.

## Giải pháp

- **Encoder câu tiếng Việt huấn luyện theo SimCSE:** checkpoint cộng đồng `VoVanPhuc/sup-SimCSE-VietNamese-phobert-base`, dựa trên PhoBERT, cần tách từ bằng `pyvi`.
- **Truy hồi lai (hybrid):** BM25 cho khớp từ khóa, kết hợp SimCSE cho khớp ngữ nghĩa và câu hỏi diễn đạt khác văn bản.
- **Chunking theo cấu trúc văn bản:** chia theo Điều/Khoản, giữ metadata để trích dẫn chính xác.
- **Cảnh báo độ tin cậy thấp:** ngưỡng được chọn và đánh giá trên tập dev. Ngưỡng này không phải xác suất đúng.
- **Không dùng LLM sinh câu trả lời:** ứng dụng chỉ hiển thị nguyên văn kèm nguồn.

Phần tái hiện bài báo dùng mã nguồn chính thức [princeton-nlp/SimCSE](https://github.com/princeton-nlp/SimCSE) tại commit `235f89e0244b23673b69fbbc4a1cd9868c5a5c24`.

## Kiến trúc tổng quan

```
Văn bản quy chế (PDF/DOCX/TXT)
   └─► Tách Điều/Khoản + metadata ─► Chuẩn hóa + tách từ (pyvi)
                                        ├─► BM25 index
                                        └─► SimCSE-VN embeddings (FAISS)
Câu hỏi ─► Chuẩn hóa + tách từ ─► BM25 + SimCSE ─► Kết hợp điểm ─► Xếp hạng theo Điều
   └─► Giao diện Gradio: top-3 Điều/Khoản · trích đoạn · nguồn/phiên bản · cảnh báo tin cậy
```

Chi tiết xem [PROJECT.md §5](PROJECT.md#5-application-architecture--implementation).

## Công nghệ

Python · PyTorch · HuggingFace Transformers · pyvi · rank_bm25 · faiss-cpu · Gradio. Chạy được trên CPU; GPU chỉ cần cho phần mở rộng tùy chọn.

## Cài đặt và chạy

> ⚠️ Các lệnh dưới đây là **dự kiến**. Sẽ được cập nhật và kiểm tra khi có code.

```bash
# 1. Cài đặt
git clone <repo-url> && cd <repo>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Chuẩn bị dữ liệu và index
python scripts/prepare_virhe4qa.py      # tải và xử lý bộ đánh giá ViRHE4QA (bản con trong ViRE)
python scripts/build_index.py --config configs/default.yaml

# 3. Chạy ứng dụng demo
python app/app.py

# 4. Đánh giá truy hồi (BM25 / SimCSE / Hybrid)
python scripts/run_eval.py --config configs/default.yaml

# 5. Tái hiện kết quả SimCSE gốc (STS, checkpoint chính thức)
bash repro/run_repro.sh
```

## Dữ liệu

| Bộ dữ liệu | Vai trò | Nguồn |
|---|---|---|
| ViRHE4QA (bản con 1.000 câu hỏi trong benchmark ViRE) | Đánh giá chính trên dataset mới | [ViRE](https://github.com/longstnguyen/ViRE), bài báo gốc R2GQA ([arXiv:2409.02840](https://arxiv.org/abs/2409.02840)) |
| Quy chế của trường + bộ câu hỏi nhóm tự gán nhãn | Đánh giá trong bối cảnh thực tế (chỉ dùng để test) | Nhóm tự xây dựng |
| STS 2012–2016, STS-B, SICK-R | Tái hiện kết quả bài báo | Script của repo SimCSE |

Điều kiện sử dụng từng bộ dữ liệu xem [PROJECT.md §6](PROJECT.md#6-datasets--experimental-evaluation).

## Tài liệu dự án

- **[PROJECT.md](PROJECT.md)** là nguồn thông tin duy nhất (single source of truth): phạm vi, ánh xạ yêu cầu Lab 03, nền tảng SimCSE, kiến trúc, thí nghiệm, phân công, rủi ro.

## Tham khảo

- T. Gao, X. Yao, D. Chen. *SimCSE: Simple Contrastive Learning of Sentence Embeddings.* EMNLP 2021, pp. 6894–6910. <https://aclanthology.org/2021.emnlp-main.552/>
- Mã nguồn: <https://github.com/princeton-nlp/SimCSE/tree/235f89e0244b23673b69fbbc4a1cd9868c5a5c24>
