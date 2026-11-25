# Đánh giá ứng dụng

Ghi rõ tác vụ người dùng cần hoàn thành, giải pháp đối chứng, thay đổi nhóm tự phát triển và tiêu chí đo cải thiện. Chọn tiêu chí theo tác vụ, chẳng hạn tỷ lệ hoàn thành, chất lượng xếp hạng hoặc thời gian phản hồi.

Chạy ứng dụng và đối chứng trên cùng bộ tình huống với điều kiện đo nhất quán. Lưu cấu hình, lệnh chạy hoặc quy trình đánh giá với người dùng, kết quả và phân tích các trường hợp thất bại. Nếu dùng cùng nguồn dữ liệu với [đánh giá mô hình](../external_dataset/README.md), tham chiếu cùng phiên bản dữ liệu và nêu rõ câu hỏi mà từng phép đo trả lời.

## E2 trên D1-test

[Bảng chỉ số theo mức trùng từ](results/E2/d1-test.md) dùng ba bảng xếp hạng E1 đã lưu. Để tái lập, chạy từ gốc repo trong [môi trường truy hồi D1](../external_dataset/README.md#truy-hồi-phase-3).

```powershell
& $d1Python -m experiments.application.analyze_d1_overlap --output outputs/d1-test-overlap/replay.json
```

Lệnh đọc đường dẫn CSV, câu hỏi D1-test và các bảng xếp hạng từ [dữ liệu kết quả E1](../external_dataset/results/E1/d1-test.json). Dùng `--input` nếu CSV đúng checksum nằm ở đường dẫn khác và chọn một file đầu ra mới. File kết quả lưu mốc Jaccard, mã câu từng nhóm, chỉ số và khoảng tin cậy.

## Chấm D2-test

Sau khi nhóm chốt `data/d2/queries_d2.jsonl`, dùng [lệnh truy hồi HCMUS](../external_dataset/README.md#lệnh-chuẩn-bị-hcmus-và-đánh-giá-d2) để lưu xếp hạng đủ 51 Điều của BM25, SimCSE-VN và Hybrid. Chạy lệnh sau từ gốc repo bằng môi trường truy hồi có Matplotlib. Lệnh đọc lại ba xếp hạng đã lưu và hai văn bản nguồn đã kiểm SHA-256.

```powershell
$env:PYTHONPATH = 'src'
& $d1Python -m experiments.application.evaluate_d2 --chunks data/processed/d2/corpus.jsonl --runs outputs/d2-test --output outputs/d2-evaluation
```

Bộ chấm lấy trọng số, ngưỡng và checkpoint từ [cấu hình chốt trên D1-dev](../external_dataset/results/D1-dev-tuning/summary.json). Với lượt truy hồi có checksum trong `summary.json`, lệnh đối chiếu SHA-256 của corpus, nhãn và cả ba xếp hạng. Với bản xuất cũ, bảng kết quả ghi rõ checksum được tính khi chấm. Dùng `--queries` nếu file nhãn đã chốt nằm ở đường dẫn khác và chỉ định một thư mục đầu ra mới.

- `d2-test.md` ghi Hit@k và MRR@10 theo Điều và chủ đề, Clause@1 trên câu có nhãn Khoản, chênh lệch Hybrid so với BM25 cùng khoảng tin cậy 95%. Bảng có số câu, kết quả chung, các nhóm trùng từ và nhóm `origin: form` nếu có.
- `summary.json` ghi mã câu từng nhóm, mốc Jaccard, số liệu cảnh báo tại ngưỡng cố định, từng điểm risk–coverage và checksum đầu vào. Chỉ số có mẫu số bằng 0 ghi `null`.
- `risk-coverage.png` có đường theo Điều và theo chủ đề khi có câu trong phạm vi. Độ bao phủ tính trên toàn bộ câu, risk tính trên câu trong phạm vi đã được đánh dấu tin cậy, và false-confidence tính riêng trên các câu ngoài phạm vi. Xem [quy tắc tính](../../docs/application/PROJECT.md#63-baseline-và-metrics).

Lệnh đã được kiểm với nhãn và bảng xếp hạng giả. Kết quả D2 chính thức cần bộ nhãn mà hai thành viên đã thống nhất.
