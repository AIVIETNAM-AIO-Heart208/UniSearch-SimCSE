# Dữ liệu

Với mỗi bộ dữ liệu, ghi tên và phiên bản, nguồn tải, điều kiện sử dụng, ngôn ngữ, số mẫu, định dạng đầu vào và ý nghĩa của nhãn. Ghi rõ bộ nào thuộc paper và bộ nào được dùng cho đánh giá bổ sung.

- `raw/<dataset>/` chứa bản gốc tải về.
- `processed/<dataset>/` chứa dữ liệu đã chuẩn bị cho huấn luyện, đánh giá hoặc demo.

Hai đường dẫn trên được tạo khi chuẩn bị dữ liệu và được Git bỏ qua. Đưa mã chuẩn bị dữ liệu, quy tắc chia tập, seed nếu có và lệnh chạy vào repo để thành viên khác tạo lại đúng tập mẫu. Với tập kiểm thử tự xây dựng, lưu quy trình gán nhãn và cách phát hiện trùng lặp. Nếu chia sẻ dữ liệu bằng liên kết ngoài, kiểm tra quyền truy cập trước khi nộp.

**D1** dùng bản con ViRHE4QA của ViRE. Script [prepare_virhe4qa.py](prepare_virhe4qa.py) kiểm tra SHA-256 của CSV, tạo mã đoạn từ nội dung context và chia câu hỏi theo nhóm context với seed 42. Bản gốc có 1.000 dòng và 297 context. Sau khi bỏ 17 dòng trùng nguyên văn, D1-dev có 224 câu thuộc 59 context và D1-test có 759 câu thuộc 238 context. Cả hai tập dùng cùng kho tra cứu gồm 297 context. Xem lệnh tải và chạy trong [hướng dẫn D1](../experiments/external_dataset/README.md).

**D2** (bộ test quy chế đào tạo HCMUS do nhóm tự xây dựng): mô tả, metadata văn bản và bảng đối ứng Điều ở [`d2/`](d2/README.md). Thư mục `d2/` có trong Git, gồm cả chữ QĐ 1175 (văn bản công khai). PDF 2021 và bản chép QĐ 3087 nằm ở `raw/d2/`, không có trong Git (D-18).

Nguồn chính thức của QĐ 3087 và văn bản sửa đổi bảng xếp loại của QĐ 1175 được ghi trong [metadata nguồn](d2/documents.yaml). Cách tạo đúng bản chép 2026 dùng để lập chỉ mục từ bản nhóm đã chia sẻ nằm ở [hướng dẫn D2](d2/README.md#file).
