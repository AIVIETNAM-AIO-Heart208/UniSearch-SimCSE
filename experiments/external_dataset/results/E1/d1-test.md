# Kết quả D1-test

Lượt chạy ngày 25/11/2026 dùng 759 câu ViRHE4QA thuộc 238 đoạn đáp án. Cả ba phương pháp tìm trên cùng corpus gồm 297 đoạn nguồn, chia thành 955 chunk bằng tokenizer của checkpoint đã ghim. Nhóm đoạn đáp án của D1-test tách biệt với D1-dev.

Hybrid dùng `--weight 0.6` cho BM25. Cảnh báo dùng `--threshold 0.6201629042625427` trên cosine của chunk trích dẫn ở kết quả đầu tiên. Cả hai giá trị lấy từ [cấu hình chốt trên D1-dev](../D1-dev-tuning/handoff.md).

## Xếp hạng đoạn nguồn

Hit@k là tỷ lệ câu có đoạn nguồn đúng trong k kết quả đầu. MRR@10 là trung bình nghịch đảo hạng của đoạn đúng, tính 0 khi đoạn đúng nằm ngoài top 10.

| Phương pháp | Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR@10 |
|---|---:|---:|---:|---:|---:|
| BM25 | 70,36% | 86,82% | 91,30% | 94,73% | 0,791792 |
| SimCSE-VN | 45,98% | 67,06% | 77,08% | 85,77% | 0,588163 |
| Hybrid | 72,46% | 88,67% | 92,62% | 95,78% | 0,810780 |

## Hybrid so với BM25

| Chỉ số | Chênh lệch Hybrid − BM25 | Khoảng tin cậy 95% |
|---|---:|---:|
| Hit@1 (điểm phần trăm) | +2,11 | [+0,39, +3,82] |
| MRR@10 | +0,018988 | [+0,008363, +0,029811] |

Bootstrap ghép cặp lấy mẫu lại 759 câu có hoàn lại 1.000 lần với seed 42. Hai cận là phân vị 2,5% và 97,5% của chênh lệch trung bình, nội suy tuyến tính. Cả hai khoảng đều nằm trên 0 trên D1-test. [Giao thức trong PROJECT §6.3–6.4](../../../../docs/application/PROJECT.md#63-baseline-và-metrics)

## Cảnh báo của Hybrid

Độ bao phủ là **618/759 = 81,42%**. Các câu có cosine dưới ngưỡng vẫn có bảng xếp hạng và được đánh dấu cảnh báo.

| Nhóm | Số câu | Hit@1 |
|---|---:|---:|
| Tin cậy (cosine ≥ ngưỡng) | 618 | 76,05% |
| Có cảnh báo (cosine < ngưỡng) | 141 | 56,74% |

D1-test có 0 câu ngoài phạm vi, nên tỷ lệ tin cậy sai (`false_confidence`) có giá trị `null`.

Xem [biểu đồ risk–coverage E3](../E3/d1-test-risk-coverage.png) và [dữ liệu đường cong](../E3/d1-test.json) của cùng xếp hạng Hybrid.

## Tệp kết quả

- [Dữ liệu kết quả và cấu hình thực chạy](d1-test.json) ghi các chỉ số đầy đủ, khoảng tin cậy, môi trường CPU, lệnh chạy và SHA-256 của đầu vào cùng bảng xếp hạng.
- `outputs/d1-test/inputs/` chứa corpus, 759 câu test và thống kê split. `outputs/d1-test/retrieval/runs/` chứa ba file JSONL lưu top 20 đoạn nguồn mỗi câu.
- Các chỉ số, khoảng tin cậy và số liệu cảnh báo đã được tính lại độc lập từ xếp hạng đã lưu. Hit@5 và Hit@10 lấy từ phép tính lại này.
