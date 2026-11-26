# Đánh giá ứng dụng

Nhóm so sánh BM25, SimCSE-VN và Hybrid trên cùng câu hỏi, với cấu hình chốt ở D1-dev. Các phép đo gồm xếp hạng Điều, chủ đề và Khoản trên D2, cảnh báo, và [độ trễ truy hồi trên CPU](results/E4/cpu-latency.md). Các ví dụ E5 bên dưới giúp kiểm tra lỗi trên văn bản nguồn.

## E2 trên D1-test

[Bảng chỉ số theo mức trùng từ](results/E2/d1-test.md) dùng ba bảng xếp hạng E1 đã lưu. Để tái lập, chạy từ gốc repo trong [môi trường truy hồi D1](../external_dataset/README.md#truy-hồi-phase-3).

```powershell
& $d1Python -m experiments.application.analyze_d1_overlap --e1-summary outputs/d1-test-rerun/summary.json --output outputs/d1-test-overlap/replay.json
```

Lệnh trên đọc lượt E1 vừa chạy, đối chiếu SHA-256 của câu hỏi và từng bảng xếp hạng trước khi chấm. Nếu giữ nguyên các tệp đầu vào tại đường dẫn của lượt đã công bố, có thể bỏ `--e1-summary` để dùng [manifest E1 đã kiểm](../external_dataset/results/E1/d1-test.json). Dùng `--input` khi CSV đúng checksum nằm ở đường dẫn khác. File kết quả lưu mốc Jaccard, mã câu từng nhóm, chỉ số và khoảng tin cậy.

## Chấm D2-test

[Bảng E2 và E3 của lượt chạy 26/11](results/D2/d2-test.md), [dữ liệu kết quả và cấu hình](results/D2/summary.json) và [biểu đồ risk–coverage](results/D2/risk-coverage.png) dùng toàn bộ bộ nhãn đã chốt. Ba bảng xếp hạng của lượt chạy này nằm trong `outputs/d2-test/runs/` trên máy Huy.

Dùng [nhãn D2 đã chốt](../../data/d2/queries_d2.jsonl) với [lệnh truy hồi HCMUS](../external_dataset/README.md#lệnh-chuẩn-bị-hcmus-và-đánh-giá-d2) để lưu xếp hạng đủ 51 Điều của BM25, SimCSE-VN và Hybrid. Chạy lệnh sau từ gốc repo bằng môi trường truy hồi có Matplotlib. Lệnh đọc lại ba xếp hạng đã lưu và hai văn bản nguồn đã kiểm SHA-256.

```powershell
$env:PYTHONPATH = 'src'
& $d1Python -m experiments.application.evaluate_d2 --chunks data/processed/d2/corpus.jsonl --runs outputs/d2-test --output outputs/d2-evaluation
```

Bộ chấm lấy trọng số, ngưỡng và checkpoint từ [cấu hình chốt trên D1-dev](../external_dataset/results/D1-dev-tuning/summary.json). Với lượt truy hồi có checksum trong `summary.json`, lệnh đối chiếu SHA-256 của corpus, nhãn và cả ba xếp hạng. Với bản xuất cũ, bảng kết quả ghi rõ checksum được tính khi chấm. Dùng `--queries` nếu file nhãn đã chốt nằm ở đường dẫn khác và chỉ định một thư mục đầu ra mới.

- `d2-test.md` ghi Hit@k và MRR@10 theo Điều và chủ đề, Clause@1 trên câu có nhãn Khoản, chênh lệch Hybrid so với BM25 cùng khoảng tin cậy 95%. Bảng có số câu, kết quả chung, các nhóm trùng từ và nhóm `origin: form` nếu có.
- `summary.json` ghi mã câu từng nhóm, mốc Jaccard, số liệu cảnh báo tại ngưỡng cố định, từng điểm risk–coverage và checksum đầu vào. Chỉ số có mẫu số bằng 0 ghi `null`.
- `risk-coverage.png` có đường theo Điều và theo chủ đề khi có câu trong phạm vi. Độ bao phủ tính trên toàn bộ câu, risk tính trên câu trong phạm vi đã được đánh dấu tin cậy, và false-confidence tính riêng trên các câu ngoài phạm vi. Xem [quy tắc tính](../../docs/application/PROJECT.md#63-baseline-và-metrics).

Lượt chạy đã kiểm SHA-256 của đầu vào và cả ba bảng xếp hạng. Chỉ số E2, khoảng tin cậy và cảnh báo E3 đã được tính lại độc lập từ các xếp hạng lưu.

## Phân tích lỗi E5

[Bảng D1-test](results/E5/d1-test.md) ghi kết quả kiểm chéo thứ hạng và chunk được chọn từ ba bảng xếp hạng gốc. [Bảng D2-test](results/E5/d2-test.md) đối chiếu thứ hạng theo Điều và chủ đề, Khoản được chọn, điểm cảnh báo và nguyên văn hai quy chế.
