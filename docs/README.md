# Tài liệu đồ án

- [Checklist theo yêu cầu Lab 03 và phân công Huy – Minh](PLAN.md)
- [Tổng quan ứng dụng](application/README.md) và [thiết kế chi tiết](application/PROJECT.md)
- [Checklist rà soát workspace và phép kiểm](reviews/workspace.md)

## Báo cáo và video

- **Báo cáo** viết theo [IEEE Conference Template trên Overleaf](https://www.overleaf.com/latex/templates/ieee-conference-template/grfzhhncsfqn) và build trên máy bằng pdfLaTeX. Trình bày Abstract, Introduction, Related Work, Proposed Model/Method, Experimental Setup, Results and Discussion/Application, Conclusion và References. Nguồn, lệnh build và người viết từng mục: [report/](report/README.md).
- **Minh quay video chính thức** trên cấu hình demo đã đánh giá. Link Google Drive trong tin nhắn bàn giao mở bộ PowerPoint 13 trang có ghi chú thuyết trình, PDF cùng nội dung và ZIP giữ sáu slide gốc cùng 67 khung hình thao tác. Bản lưu trên máy dựng nằm ở `outputs/video-minh/`. Phần demo có câu chuyển trường để so Hybrid với BM25, công thức và bảng điểm, phạm vi theo khóa, một cảnh báo và một câu ngoài phạm vi lọt cảnh báo. [Cấu hình demo](../apps/README.md#chạy-cục-bộ)
- **Hồ sơ chờ video** ở `outputs/submission/Ho-so-cho-video.zip` gồm PDF báo cáo, mã nguồn, hướng dẫn, corpus và bảng SHA-256. `source/BASE_COMMIT.txt` ghi commit nền. Gói cuối mang tên `[Group14].zip` sau khi thêm bản ghi của Minh. Phụ đề WebVTT là tùy chọn và phải khớp bản ghi được chọn. [Quyết định bàn giao dữ liệu](../data/d2/README.md#file)
- **Chạy từ ZIP.** Sau khi giải nén, vào `source/`, cài môi trường demo, tải checkpoint đúng phiên bản rồi mở app với corpus đi kèm. Muốn dựng lại corpus từ hai nguồn để đối chiếu, dùng một thư mục mới như `data/processed/rebuilt`. [Cài đặt và chạy demo](../apps/README.md#chạy-cục-bộ) · [Lệnh dựng corpus](../experiments/external_dataset/README.md#lệnh-chuẩn-bị-hcmus-và-đánh-giá-d2)
- **Đóng gói.** Hai lệnh đầu tạo và kiểm hồ sơ đang có. Sau khi có video, truyền đường dẫn MP4 của Minh cho lệnh `build`. Nếu có phụ đề cùng bản, thêm `--captions` và đường dẫn VTT. Lệnh `verify` kiểm đủ các tệp trước khi nộp. Dữ liệu công khai cần duy trì truy cập ít nhất hai năm. [Checklist và hạn nộp](PLAN.md#phase-4--hoàn-thiện-và-nộp-bài)

```powershell
python -X utf8 tools/package_submission.py prepare
python -X utf8 tools/package_submission.py verify --prepared "outputs/submission/Ho-so-cho-video.zip"
python -X utf8 tools/package_submission.py build --video "duong-dan/Video-cua-Minh.mp4"
python -X utf8 tools/package_submission.py verify "outputs/submission/[Group14].zip"
```
