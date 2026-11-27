# Dữ liệu

Với mỗi bộ dữ liệu, ghi tên và phiên bản, nguồn tải, điều kiện sử dụng, ngôn ngữ, số mẫu, định dạng đầu vào và ý nghĩa của nhãn. Ghi rõ bộ nào thuộc paper và bộ nào được dùng cho đánh giá bổ sung.

- `raw/<dataset>/` chứa bản gốc tải về.
- `processed/<dataset>/` chứa dữ liệu đã chuẩn bị cho huấn luyện, đánh giá hoặc demo.

Hai đường dẫn trên được tạo khi chuẩn bị dữ liệu và được Git bỏ qua. Đưa mã chuẩn bị dữ liệu, quy tắc chia tập, seed nếu có và lệnh chạy vào repo để thành viên khác tạo lại đúng tập mẫu. Với tập kiểm thử tự xây dựng, lưu quy trình gán nhãn và cách phát hiện trùng lặp. Nếu chia sẻ dữ liệu bằng liên kết ngoài, kiểm tra quyền truy cập trước khi nộp.

**D1** dùng bản con ViRHE4QA của ViRE. Script [prepare_virhe4qa.py](prepare_virhe4qa.py) kiểm tra SHA-256 của CSV, tạo mã đoạn từ nội dung context và chia câu hỏi theo nhóm context với seed 42. Bản gốc có 1.000 dòng và 297 context. Sau khi bỏ 17 dòng trùng nguyên văn, D1-dev có 224 câu thuộc 59 context và D1-test có 759 câu thuộc 238 context. Cả hai tập dùng cùng kho tra cứu gồm 297 context. Xem lệnh tải và chạy trong [hướng dẫn D1](../experiments/external_dataset/README.md).

[Lượt đánh giá D1-test](../experiments/external_dataset/README.md#đánh-giá-d1-test) đã lưu 955 chunk, câu hỏi test và thống kê split trong `outputs/d1-test/inputs/` trên máy Huy.

**D2** là bộ test quy chế đào tạo HCMUS do nhóm xây dựng. Dùng [tệp nhãn đã chốt](d2/queries_d2.jsonl) để đánh giá D2 và xem nguồn câu hỏi cùng quy trình gán nhãn trong [README của D2](d2/README.md#câu-hỏi-và-nhãn-d2-đã-chốt). Thư mục `d2/` có trong Git, gồm cả chữ QĐ 1175 (văn bản công khai). PDF 2021 và bản ChatGPT chép QĐ 3087 từ scan nằm ở `raw/d2/`, không có trong Git (D-18).

Để tải bộ đánh giá dùng trong bài nộp, xem [thư mục Drive và SHA-256 của gói D2](d2/README.md#bộ-d2-công-khai). Nguồn chính thức của QĐ 3087 và văn bản sửa đổi bảng xếp loại của QĐ 1175 được ghi trong [metadata nguồn](d2/documents.yaml). Cách tạo đúng bản chép 2026 dùng để lập chỉ mục từ bản nhóm đã chia sẻ nằm ở [hướng dẫn D2](d2/README.md#file).

File [corpus HCMUS đã xử lý](d2/README.md#file) giữ [mã Điều/Khoản và offset nguồn](d2/README.md#mã-điều-và-khoản) để kiểm chứng trích dẫn và chấm D2 theo Khoản, kể cả khi văn bản lặp số Khoản.

**Dữ liệu phát triển HCMUS.** [Bộ thử chọn Khoản và xác định phạm vi](development/clause-scope-pilot.jsonl) có 16 câu kèm nhãn do Codex điền và vị trí đã đọc trong PDF gốc. Cách đọc các trường căn cứ, thu câu độc lập và giữ kín bộ dùng để quyết định thay phiên bản nằm trong [thiết kế so sánh](../experiments/application/clause-scope-comparison.md#dữ-liệu-phát-triển-và-nhãn-giữ-kín).

## Nguồn văn bản D1

Hai PDF về văn bằng và tiêu chuẩn giảng viên dùng bản lưu Internet Archive. Nếu bản lưu bị giới hạn lượt tải, mở bảng tính của tác giả theo dòng mà ứng dụng hiển thị. [Kiểm đường dẫn ngày 27/11/2026](../docs/reviews/workspace.md#kiểm-tra-ngày-27112026)

Mỗi kết quả D1 có tên văn bản của UIT và số dòng trong `raw_excel/train.xlsx` của tác giả ViRHE4QA. Cả 297 đoạn gốc, tương ứng 955 đoạn trích trong chỉ mục, tra được về 21 văn bản. Các bảng trích dẫn đi kèm mã nguồn để demo đọc ngoại tuyến. Tác giả công bố dữ liệu cho mục đích nghiên cứu. [Bản phát hành R2GQA](https://github.com/DoPhamPhucTinh/R2GQA/tree/0653933b6f28b8a05bb822997aed734f7590670e) · [Kết quả kiểm theo từng văn bản](../experiments/external_dataset/results/D1-sources/coverage.json)

- [Bảng nguồn](d1/sources.tsv) dùng mã SHA-256 của nguyên văn đoạn trong ViRE. Đã kiểm cả 1.000 dòng CSV theo mã câu, câu hỏi và nội dung ở ba bảng tác giả. Có 983 mã câu khác nhau. Khi so nội dung sau chuẩn hóa Unicode NFC và khoảng trắng, 297 đoạn ứng với 294 nội dung. Mỗi nội dung có đúng một tên văn bản trong bảng train. Mọi dòng cùng nội dung trong bảng val đều xác nhận tên đó. Bảng test của tác giả có các dòng ghi tên văn bản khác nhau cho cùng một nội dung nên chỉ dùng để đối chiếu câu hỏi. Các tên train, val, test ở đây là tên tệp của tác giả. Nhóm chia D1 theo quy trình riêng.
- [Danh mục văn bản](d1/documents.json) giữ nguyên tên tác giả và có nhãn ngắn dùng trên thẻ. Trường `track` ghi hệ khi tên văn bản nêu rõ chính quy hoặc từ xa. Văn bản thiếu trường này vẫn có trong Tra cứu chung. [Bảng trang PDF](d1/pdf_pages.tsv) ghi số trang tính từ 1 cho 132 đoạn. Với các đoạn này, toàn bộ dãy từ và số, gồm cả số Điều nếu có, khớp liên tiếp trong văn bản PDF hoặc phần chữ nhận dạng từ ảnh trang sau khi chuẩn hóa chữ hoa, dấu câu, khoảng trắng và bỏ số trang ở lề. Danh mục lưu URL và SHA-256 của PDF đã kiểm. Với 165 đoạn còn lại, căn cứ hiện có là dòng trong bảng tác giả. Tên văn bản tự nó chưa xác nhận số quyết định, phiên bản hay hiệu lực đối với sinh viên hiện tại.

Để kiểm lại bảng nguồn, tải [ViRHE4QA.zip của tác giả](https://github.com/DoPhamPhucTinh/R2GQA/blob/0653933b6f28b8a05bb822997aed734f7590670e/ViRHE4QA.zip) và [CSV của ViRE](https://github.com/longstnguyen/ViRE/blob/60ea7155134eaa426ab1d0a82d2bbbf327d1b470/data/ViRHE4QA_v2.csv) vào `data/raw/d1/`. Dùng Python có `openpyxl` và chạy ở gốc repo. Lệnh kiểm SHA-256 của cả hai đầu vào trước khi đối chiếu. Bỏ `--check` để dựng lại bảng.

```powershell
python -m data.build_d1_sources --subset data/raw/d1/ViRHE4QA_v2.csv --archive data/raw/d1/ViRHE4QA.zip --check
```
