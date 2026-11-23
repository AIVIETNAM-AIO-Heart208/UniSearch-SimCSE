# Dữ liệu

Với mỗi bộ dữ liệu, ghi tên và phiên bản, nguồn tải, điều kiện sử dụng, ngôn ngữ, số mẫu, định dạng đầu vào và ý nghĩa của nhãn. Ghi rõ bộ nào thuộc paper và bộ nào được dùng cho đánh giá bổ sung.

- `raw/<dataset>/` chứa bản gốc tải về.
- `processed/<dataset>/` chứa dữ liệu đã chuẩn bị cho huấn luyện, đánh giá hoặc demo.

Hai đường dẫn trên được tạo khi chuẩn bị dữ liệu và được Git bỏ qua. Đưa mã chuẩn bị dữ liệu, quy tắc chia tập, seed nếu có và lệnh chạy vào repo để thành viên khác tạo lại đúng tập mẫu. Với tập kiểm thử tự xây dựng, lưu quy trình gán nhãn và cách phát hiện trùng lặp. Nếu chia sẻ dữ liệu bằng liên kết ngoài, kiểm tra quyền truy cập trước khi nộp.

**D2** (bộ test quy chế đào tạo HCMUS do nhóm tự xây dựng): mô tả, metadata văn bản và bảng đối ứng Điều ở [`d2/`](d2/README.md). Thư mục `d2/` có trong Git; toàn văn hai quy chế nằm ở `raw/d2/`, không có trong Git.
