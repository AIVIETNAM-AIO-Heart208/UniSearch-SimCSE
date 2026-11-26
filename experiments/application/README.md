# Đánh giá ứng dụng

Nhóm so sánh BM25, SimCSE-VN và Hybrid trên cùng câu hỏi, với cấu hình chốt ở D1-dev. Các phép đo gồm xếp hạng Điều, chủ đề và Khoản trên D2, cảnh báo, và [độ trễ truy hồi trên CPU](results/E4/cpu-latency.md). Các ví dụ E5 bên dưới giúp kiểm tra lỗi trên văn bản nguồn.

Lượt [đối chiếu giao diện trước và sau](results/ui-review/search-behavior.json) lưu các căn cứ hiển thị cho từng câu hỏi. [Checklist trải nghiệm sinh viên](../../docs/reviews/workspace.md#trải-nghiệm-sinh-viên-và-tài-liệu) mô tả các trường hợp phải sửa hoặc còn giới hạn.

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

## So sánh trước khi thay bản truy hồi

[Kết quả trên 16 câu phát triển](results/clause-scope-pilot/comparison.md) đối chiếu từng câu trên Hybrid hiện tại và ba bản thử. Bộ kiểm tra đồng thuận vẫn chấp nhận sai câu đăng ký bù và cảnh báo thêm ba câu có đáp án. [Nhãn và căn cứ nguồn](../../data/development/clause-scope-pilot.jsonl) · [Thiết kế và tiêu chí thay bản](clause-scope-comparison.md)

Chạy từ gốc repo bằng môi trường truy hồi đã chuẩn bị checkpoint và corpus HCMUS. Chọn một thư mục đầu ra mới.

```powershell
$env:PYTHONPATH = 'src'
& $d1Python -m experiments.application.compare_clause_scope --model-path outputs/d1-model --output outputs/development/clause-scope-replay
```

Lệnh kiểm checksum trước khi chạy, gửi từng câu riêng và lưu hai tệp kết quả cùng 64 bản HTML trong `html/`. [Manifest](results/clause-scope-pilot/summary.json) ghi thứ tự đoạn, cấu hình và mã thực chạy. [Dự đoán từng câu](results/clause-scope-pilot/predictions.jsonl) lưu điểm thô dùng chung, đủ 51 Điều, các Khoản của A và K, quyết định và bằng chứng hiển thị của cả bốn bản. Với `evidence_path`, danh sách rỗng nghĩa là thấy căn cứ ngay, danh sách có phần tử là các thao tác cần mở, còn `null` nghĩa là thiếu căn cứ trong chủ đề đầu hoặc câu nằm ngoài phạm vi. Các bản HTML tái tạo cục bộ có trích đoạn từ văn bản nguồn.

## Thử mở phiên bản được hỏi

Phát lại điểm của **bản A** trên cùng 16 câu. Đối chứng đưa bản 2026 lên đầu mỗi chủ đề. Bản thử chỉ đưa văn bản sinh viên nêu đích danh lên đầu trong các phiên bản sẵn có của chủ đề. Câu chỉ nhắc khóa tuyển, năm học, hai phiên bản hoặc không nêu năm dùng thứ tự đối chứng. Cả hai cách dùng cùng 51 Điều, các đoạn đã chọn và quyết định cảnh báo trước khi gộp chủ đề.

Chỉ tính “thấy ngay” khi câu có đáp án và sinh viên đọc được căn cứ đủ trả lời trong đúng phiên bản, ngay trong thẻ đầu ở trạng thái mặc định. Báo số cặp được lợi hoặc mất căn cứ, tách câu yêu cầu bản 2021, bản 2026, câu chỉ nhắc năm học và câu không nêu năm. Hiệu quả của việc yêu cầu sinh viên chọn khóa là câu hỏi UX riêng.

```powershell
$env:PYTHONPATH = 'src'
& $d1Python -m experiments.application.compare_edition_display --output outputs/development/edition-display-replay
```

Lệnh cần corpus HCMUS và dùng điểm truy hồi đã lưu trong repo. Thư mục mới sẽ có `summary.json` và hai bản HTML cho mỗi câu trong `html/`. [Kết quả và các câu thay đổi](results/edition-display-pilot/comparison.md)

### Mô phỏng hai cách chọn khóa

Gói ngoại tuyến có hai giao diện dùng **cùng 17 câu**. Mẫu A yêu cầu chọn khóa ở màn hình đầu. Mẫu B nhận câu hỏi ngay và chỉ hỏi năm nhập học khi cần xác định quy chế áp dụng cho cá nhân. Hai mẫu dùng chung kết quả đã kiểm của 16 câu phát triển, kể cả thứ tự phiên bản và cảnh báo. Câu thứ 17 tra trực tiếp Điều 27 của quy chế 2026. Khi câu hỏi nêu rõ năm văn bản, lựa chọn khóa trong phiên vẫn cho phép mở đúng văn bản được hỏi. [Ba tình huống và câu hỏi chung](cohort_study/study.json)

Giải nén `mo-phong-chon-khoa.zip` và mở `huong-dan-mo-phong.html` để xem hai mẫu, ba tình huống và căn cứ đối chiếu. K24 và K26 dùng cùng một câu hỏi về quy chế áp dụng cho mình. Tình huống tra cứu chung hỏi về điểm chuyên cần của học phần thực hành. Các nguồn mở cục bộ. Lựa chọn khóa chỉ tồn tại trong trang đang mở.

Để dựng lại từ gốc repo, dùng Python có PyYAML. Bộ dựng kiểm SHA-256 của trang kết quả và các bản sao văn bản. Nếu thiếu thư mục phát lại, bộ dựng dùng quy trình ở mục trên với môi trường và corpus HCMUS của nhóm. Nguồn cục bộ gồm PDF 2021 trong `data/raw/d2/`, PDF 2026 `QD3087-official.pdf` và hai ảnh `qd-91-trang-1.png`, `qd-91-trang-2.png` trong `outputs/d2/e5-source-review/`. Có thể truyền `--documents "đường dẫn tới thư mục van-ban đã giải nén"` để dùng lại nguồn của một gói trước.

```powershell
$env:PYTHONPATH = 'src'
python -m experiments.application.cohort_study.build --output outputs/development/mo-phong-chon-khoa
```

Phép kiểm bên dưới cần Chrome và Python có Playwright. Nó giải nén ZIP vào thư mục tạm, ngắt mạng của trình duyệt, thử đủ ba nhiệm vụ ở cả hai mẫu, đối chiếu 16 cặp kết quả và kiểm tra liên kết nguồn. Thêm `--screenshots outputs/development/anh-thu-nghiem-chon-khoa` để tạo riêng bộ ảnh phục vụ đánh giá giao diện. Dùng thư mục đích mới cho mỗi lần đóng gói hoặc xuất ảnh.

```powershell
python -m experiments.application.cohort_study.check_ui outputs/development/mo-phong-chon-khoa/mo-phong-chon-khoa.zip
```

### Chạy sáu lượt mô phỏng

Lệnh mở gói trong Chrome ngoại tuyến, nhập câu của từng tình huống, kiểm đoạn căn cứ đầu tiên đang hiện và bấm mở văn bản nguồn. Mỗi tổ hợp giữa hai mẫu và ba tình huống dùng một phiên mới. Cần Chrome và Python có Playwright. [Kết quả, cách tính thao tác và lỗi đã sửa](results/cohort-walkthrough/comparison.md)

```powershell
python -m experiments.application.cohort_study.run_walkthrough outputs/development/mo-phong-chon-khoa/mo-phong-chon-khoa.zip --output outputs/development/kiem-tra-mo-phong-chon-khoa
```

Chọn thư mục đích mới khi chạy lại. Thư mục chứa bảng TSV ghi kết quả từng lượt, nhật ký sự kiện, sáu ảnh PNG và một ZIP để đối chiếu.
