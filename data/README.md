# Dữ liệu

Với mỗi bộ dữ liệu, ghi tên và phiên bản, nguồn tải, điều kiện sử dụng, ngôn ngữ, số mẫu, định dạng đầu vào và ý nghĩa của nhãn. Ghi rõ bộ nào thuộc paper và bộ nào được dùng cho đánh giá bổ sung.

- `raw/<dataset>/` chứa bản gốc tải về.
- `processed/<dataset>/` chứa dữ liệu đã chuẩn bị cho huấn luyện, đánh giá hoặc demo.

Hai đường dẫn trên được tạo khi chuẩn bị dữ liệu và được Git bỏ qua. Đưa mã chuẩn bị dữ liệu, quy tắc chia tập, seed nếu có và lệnh chạy vào repo để thành viên khác tạo lại đúng tập mẫu. Với tập kiểm thử tự xây dựng, lưu quy trình gán nhãn và cách phát hiện trùng lặp. Nếu chia sẻ dữ liệu bằng liên kết ngoài, kiểm tra quyền truy cập trước khi nộp.
