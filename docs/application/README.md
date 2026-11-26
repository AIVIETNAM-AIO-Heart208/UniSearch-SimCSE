# Trợ lý tra cứu quy chế học vụ tiếng Việt (SimCSE)

Đồ án Lab 03 – Machine Learning, **Nhóm 14**, **Option 1: Practical Application**.
Ứng dụng tìm đúng **Điều/Khoản** trong quy chế đào tạo của Trường ĐH Khoa học Tự nhiên – ĐHQG-HCM cho câu hỏi tự nhiên của sinh viên, hiển thị đoạn văn bản kèm tên văn bản, số hiệu và phạm vi áp dụng.

> **Trạng thái:** đã tái hiện R1–R4, [chốt cấu hình trên D1-dev](../../experiments/external_dataset/results/D1-dev-tuning/handoff.md), chấm [D1-test](../../experiments/external_dataset/results/E1/d1-test.md) và [D2-test](../../experiments/application/results/D2/d2-test.md). Minh đã kiểm demo và [đo độ trễ CPU](../../experiments/application/results/E4/cpu-latency.md). [Báo cáo IEEE](../report/README.md) đã có phần ứng dụng và đóng góp thành viên. [Checklist rà soát](../reviews/workspace.md).
> Đã kiểm chéo và đưa ví dụ của [E5 D1-test](../../experiments/application/results/E5/d1-test.md) và [E5 D2-test](../../experiments/application/results/E5/d2-test.md) vào báo cáo. Xem [trạng thái và việc tiếp theo](PROJECT.md#1-current-status).

## Thành viên

| MSSV | Họ tên | Phụ trách chính |
|---|---|---|
| 24127177 | Thái Quang Huy | Phương pháp SimCSE, tái hiện, so sánh thực nghiệm, báo cáo |
| 24127205 | Nguyễn Văn Minh | Dữ liệu tiếng Việt, truy hồi SimCSE-VN, ứng dụng, video |

Phân công chi tiết: [docs/PLAN.md](../PLAN.md).

## Bài toán

Sinh viên hỏi bằng lời thường, còn quy chế viết bằng thuật ngữ. Ví dụ thật trong bộ dữ liệu công khai ViRHE4QA (theo nội dung là quy chế ĐH CNTT; câu index 9542): *"Việc làm KLTN có thể bị dừng giữa chừng không?"*. Câu trả lời nằm ở Điều 6 "Báo cáo tiến độ thực hiện KLTN", và Điều này dùng chữ "đình chỉ", không có cụm "dừng giữa chừng". Ctrl+F hoặc tìm kiếm từ khóa chỉ khớp đúng từ, nên dễ bỏ sót. Chatbot sinh câu trả lời thì có thể "bịa" và không chỉ ra căn cứ.

**Mục tiêu:** trả về 3 Điều/Khoản liên quan nhất, kèm trích đoạn, tên văn bản, số hiệu, ngày ban hành và phạm vi áp dụng.
- Corpus gồm hai phiên bản Quy chế đào tạo: QĐ 1175/2021 và QĐ 3087/2026. Điều 27 của quy chế 2026 ghi: quy chế áp dụng cho các khóa tuyển từ năm học 2026–2027; đối với các khóa tuyển sinh từ năm 2025 trở về trước, Trường lựa chọn áp dụng quy định mới có lợi hơn cho người học. Vì vậy ứng dụng giữ cả hai bản và ghi rõ phạm vi áp dụng; trong mỗi kết quả, bản 2026 hiển thị trước vì là bản mới nhất.
- Bản 2026 là bản ChatGPT chép từ bản scan và nhóm đã hiệu đính theo PDF chính thức. Ứng dụng ghi rõ nguồn bản chép khi hiển thị. [Hướng dẫn tạo corpus](../../data/d2/README.md#file)
- Khi độ tin cậy thấp, ứng dụng cảnh báo để người dùng tự đối chiếu.
- Nhóm dùng BM25 làm mốc so sánh trên D1-test và D2. Trên 86 câu D2 có đáp án, MRR@10 theo Điều của Hybrid là 0,8750 và của BM25 là 0,8396. [Chỉ số và khoảng tin cậy D2](../../experiments/application/results/D2/d2-test.md)

## Giải pháp

- **Encoder câu tiếng Việt huấn luyện theo SimCSE:** checkpoint cộng đồng `VoVanPhuc/sup-SimCSE-VietNamese-phobert-base`, dựa trên PhoBERT, cần tách từ bằng `pyvi`.
- **Truy hồi lai (hybrid):** BM25 cho khớp từ khóa, kết hợp SimCSE cho khớp ngữ nghĩa và câu hỏi diễn đạt khác văn bản.
- **Chunking theo cấu trúc văn bản:** chia theo Điều/Khoản, giữ metadata văn bản và phiên bản để trích dẫn chính xác.
- **Cảnh báo độ tin cậy thấp:** chọn ngưỡng trên D1-dev, sau đó đánh giá trên D1-test và D2. Trên D2, ngưỡng đánh dấu 71/106 câu tin cậy, gồm 3/20 câu ngoài phạm vi. [Biểu đồ D1-test](../../experiments/external_dataset/results/E3/d1-test-risk-coverage.png) · [Biểu đồ D2-test](../../experiments/application/results/D2/risk-coverage.png)
- **Không dùng LLM sinh câu trả lời:** ứng dụng chỉ hiển thị đoạn văn bản có trong corpus kèm nguồn.

Phần tái hiện bài báo dùng mã nguồn chính thức [princeton-nlp/SimCSE](https://github.com/princeton-nlp/SimCSE) tại commit `235f89e0244b23673b69fbbc4a1cd9868c5a5c24`.

## Kiến trúc tổng quan

```
Quy chế đào tạo HCMUS (QĐ 1175/2021, QĐ 3087/2026) + data/d2/documents.yaml
   └─► Tách Điều/Khoản + metadata ─► Chuẩn hóa + tách từ (pyvi)
                                    ├─► BM25 index
                                    └─► SimCSE-VN embeddings (NumPy cosine)
Câu hỏi ─► Chuẩn hóa + tách từ ─► BM25 + SimCSE ─► Kết hợp điểm ─► Xếp hạng theo Điều
   └─► Giao diện Gradio: top-3 Điều/Khoản · trích đoạn · văn bản/số hiệu/phạm vi áp dụng · cảnh báo tin cậy
```

Chi tiết xem [PROJECT.md §5](PROJECT.md#5-application-architecture--implementation).

## Công nghệ

Python · PyTorch · Hugging Face Transformers · pyvi · rank_bm25 · NumPy · Gradio. Demo chạy trên CPU.

## Cài đặt và chạy

Chạy các lệnh từ thư mục gốc repo.

### Tái hiện kết quả SimCSE gốc (đã có)

Cần Python **3.9–3.11**, vì SentEval của repo gốc yêu cầu `numpy<1.24`. Script tự tạo venv, tải code SimCSE @ `235f89e`, dữ liệu STS và checkpoint, chạy `evaluation.py` gốc, rồi lưu kết quả cùng môi trường.

```bat
experiments\reproduction\run_r1.bat
experiments\reproduction\run_r1.bat R2
experiments\reproduction\run_r1.bat R3
```

Trên Linux/macOS: `python3.11 experiments/reproduction/run_r1.py --exp R1`. Kết quả và môi trường: [experiments/reproduction/](../../experiments/reproduction/README.md).

### Kiểm tra phần thống kê

Chạy `python -m pytest tests/test_stats.py -q` từ gốc repo. Bộ kiểm thử dùng xếp hạng giả với kết quả tính tay. Đầu vào và cách dùng với xếp hạng thực được mô tả ở [PROJECT.md §5.4](PROJECT.md#54-interface--định-dạng-dữ-liệu).

### Chạy ứng dụng

Xem [hướng dẫn chạy demo Gradio](../../apps/README.md) để chuẩn bị checkpoint, dựng corpus HCMUS và khởi động giao diện cục bộ. Chữ QĐ 1175 có trong Git. Cách chuẩn bị bản ChatGPT chép từ scan của QĐ 3087 và nguồn PDF chính thức nằm ở [hướng dẫn dữ liệu HCMUS](../../data/d2/README.md).

## Dữ liệu

| Bộ dữ liệu | Vai trò | Nguồn |
|---|---|---|
| ViRHE4QA (bản con 1.000 câu hỏi trong benchmark ViRE) | Đánh giá chính trên các đoạn quy chế đi kèm D1 | [ViRHE4QA_v2.csv @ ViRE `60ea715`](https://github.com/longstnguyen/ViRE/blob/60ea7155134eaa426ab1d0a82d2bbbf327d1b470/data/ViRHE4QA_v2.csv), bài báo gốc R2GQA ([arXiv:2409.02840](https://arxiv.org/abs/2409.02840)) |
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
- Trường ĐH Khoa học Tự nhiên, ĐHQG-HCM. *Quy chế đào tạo trình độ đại học*, ban hành kèm QĐ 3087/QĐ-KHTN ngày 29/9/2026. [PDF do Trường công bố](https://www.hcmus.edu.vn/wp-content/uploads/2026/10/QD3087_QD-Quy-che-dao-tao-2026.pdf).
