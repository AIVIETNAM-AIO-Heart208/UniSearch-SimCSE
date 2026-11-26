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
