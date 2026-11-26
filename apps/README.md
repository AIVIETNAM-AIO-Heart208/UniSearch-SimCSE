# Tra cứu quy chế đào tạo HCMUS

Nhập câu hỏi về quy chế đào tạo của HCMUS và nhấn **Enter** hoặc **Tra cứu**. Tab **Kết quả tra cứu** mở chủ đề đầu tiên khi độ khớp đạt ngưỡng hoặc khi chưa cấu hình ngưỡng. Nếu độ khớp thấp, tab này thu gọn các chủ đề và chỉ rõ Điều, Khoản cần đối chiếu. Với học bổng, học phí hoặc chính sách khác, liên kết **Tra văn bản khác của Trường** mở [danh mục của Phòng Thanh tra – Pháp chế](https://ttpc.hcmus.edu.vn/he-thong-van-ban-quan-ly-noi-bo/).

## Trích đoạn trên giao diện

- Mỗi tab có tối đa ba chủ đề theo thứ tự truy hồi. Mỗi chủ đề ghi năm quy chế, Điều, Khoản nếu có và tên Điều. Bản 2026 đứng trước. Mở dòng của bản 2021 để so sánh. Số hiệu dưới trích đoạn dẫn đến văn bản gốc của Trường. Mục **Áp dụng theo khóa tuyển sinh** tập hợp tên văn bản, hiệu lực và quy định chuyển tiếp. Nếu một Điều có sửa đổi, đường dẫn đến quyết định sửa đổi nằm ngay trên đoạn cần đối chiếu.
- Tab **Từ khóa (BM25)** chỉ liệt kê chủ đề có ít nhất một Điều nhận điểm từ khóa khác 0. Khi chỉ bản đối chiếu có tín hiệu, dòng mở bản đó ghi **Khớp từ khóa**. Nếu không có chủ đề đủ điều kiện, tab gợi ý cách đổi từ khóa. Cảnh báo độ khớp của phương pháp tra cứu chỉ hiện ở tab đã tính cảnh báo.
- Sửa câu hỏi sẽ ẩn kết quả cũ. Trong lúc chờ, app hiện **Đang tra cứu…**. Nếu gửi thất bại, ô nhập giữ câu đang hỏi để người dùng nhấn **Tra cứu** lần nữa.
- Dùng phím **Tab** để tới ô hỏi hoặc nhóm kết quả. Khi tiêu điểm nằm trên tên tab, dùng **←** hoặc **→** để xem phương pháp kia.
- Giao diện nối các dòng của cùng đoạn, bỏ dấu dàn trang, trình bày danh sách, công thức và bảng bằng các phần tử riêng. Nếu đoạn khớp bắt đầu hoặc kết thúc giữa một đoạn văn hay bảng, ứng dụng dùng vị trí ký tự trùng khớp trong cùng Khoản để hiển thị trọn phần đó. Xếp hạng vẫn dùng đoạn do bộ truy hồi chọn. Với câu hỏi về điểm trung bình, mở **Xem bảng xếp loại** để đọc từng khoảng điểm.
- Bản ChatGPT chép từ bản scan của QĐ 3087 được nhóm hiệu đính theo PDF chính thức. Thông tin ghi công nằm trong [hồ sơ dữ liệu](../data/d2/README.md#file). Sinh viên thấy số hiệu, ngày ban hành và liên kết đến PDF khi tra cứu. [Checklist rà giao diện](../docs/reviews/workspace.md#kiểm-tra-giao-diện-tra-cứu)

## Chạy cục bộ

Ứng dụng dùng corpus có đủ hai phiên bản, tiêu đề Điều, thông tin hiệu lực và liên kết sửa đổi QĐ 91/2023 của Điều 15 bản 2021.

Nếu mở từ hồ sơ chờ video hoặc gói nộp đã giải nén, chạy các lệnh dưới trong thư mục `source`. Corpus đã có tại `data/processed/d2/corpus.jsonl`. Khi đã có checkpoint và môi trường, app chạy được ngoại tuyến.

Trên Windows, tạo môi trường Python 3.11 từ gốc mã nguồn. Nếu đã có môi trường demo, đặt `$d1Python` thành đường dẫn Python của môi trường đó.

```powershell
py -3.11 -m venv outputs/demo-venv
$d1Python = '.\outputs\demo-venv\Scripts\python.exe'
```

Cài môi trường của bản demo và tải bảy tệp checkpoint theo phiên bản đã ghim. Lần tải đầu cần khoảng 520 MiB. Nếu đã có checkpoint đúng phiên bản ở `outputs/d1-model`, chuyển sang bước mở app.

```powershell
& $d1Python -m pip install -e ".[test,retrieval,demo]" "torch==2.5.1" "transformers==4.46.3" "huggingface-hub==0.36.2" "numpy==1.23.5" "scikit-learn==1.2.2"
& $d1Python -c "from huggingface_hub import snapshot_download; from simcse_lab.model.encoders import MODEL_ID, REVISION, SNAPSHOT_HASHES; snapshot_download(MODEL_ID, revision=REVISION, allow_patterns=list(SNAPSHOT_HASHES), local_dir='outputs/d1-model')"
```

Với bản clone, [chuẩn bị corpus HCMUS](../experiments/external_dataset/README.md#lệnh-chuẩn-bị-hcmus-và-đánh-giá-d2) sau khi có đủ hai nguồn. Với bản giải nén, mở app ngay bằng lệnh dưới rồi vào địa chỉ cục bộ Gradio in ra.

```powershell
& $d1Python apps/app.py --model-path outputs/d1-model --corpus data/processed/d2/corpus.jsonl `
  --weight '0.6' --threshold '0.6201629042625427'
```

Hai tham số lấy từ [cấu hình đã chốt trên D1-dev](../experiments/external_dataset/results/D1-dev-tuning/handoff.md). Khi bỏ trọng số, tab tra cứu dùng dense SimCSE-VN. Khi bỏ ngưỡng, tab này báo chưa cấu hình cảnh báo. Kiểm thử endpoint Gradio với corpus giả lập bằng lệnh sau.

```powershell
& $d1Python -m pytest -q tests/test_retrieval_app.py
```

Khi demo đang chạy với cấu hình trên, có thể kiểm riêng hành trình sinh viên bằng Chrome và Python có Playwright (đã thử với Playwright 1.56.0). Lệnh dùng hai chiều rộng 1440 và 320 px, mô phỏng hỏng một lượt gửi rồi thử lại. Nếu cần ảnh PNG, thêm `--screenshots` và đường dẫn tới một thư mục mới.

```powershell
python -X utf8 tools/check_search_ui.py --url http://127.0.0.1:7860
```
