# Tra cứu quy chế đào tạo

Demo mở ở **HCMUS**. Khi có corpus ViRHE4QA, chọn tab **ViRHE4QA (D1)** để nhập câu hỏi trên bộ dữ liệu này. Mỗi nguồn có ô hỏi và kết quả riêng.

## Tra cứu ViRHE4QA

Chọn **Chính quy**, **Từ xa** hoặc **Tra cứu chung** trước khi nhập câu hỏi. Hai lựa chọn theo hệ chỉ tìm trong văn bản đã xác định hệ qua tên nguồn. Tra cứu chung tìm trên toàn bộ D1, kể cả các văn bản chưa xác định hệ.

Thử câu **Điều kiện xét công nhận tốt nghiệp là gì** rồi nhấn **Enter** hoặc **Tra cứu D1**. Khi chọn chính quy, Điều 33 ghi **Đào tạo đại học chính quy theo học chế tín chỉ**. Khi chọn từ xa, Điều 19 ghi **Đào tạo từ xa trình độ đại học**. Hai điều cùng tên thuộc hai quy chế khác nhau.

Mở thẻ để xem trích đoạn, tên văn bản và dòng trong bộ dữ liệu của tác giả. Nếu kết quả đầu tiên mở ra và chỉ khớp với tiêu đề Điều, thẻ mở luôn **Xem toàn bộ đoạn nguồn** để bạn đọc nội dung bên dưới. Điểm giải thích khi đó thuộc về tiêu đề. Bạn có thể thu gọn phần này hoặc mở **Mã đoạn trích** để lấy mã đối chiếu.

Chọn **Mở PDF UIT** để tới đúng trang đã kiểm. Với hai văn bản dùng Internet Archive, liên kết ghi **Mở bản lưu PDF UIT**. Nếu dịch vụ lưu trữ tạm ngừng cho tải, chọn **Bộ dữ liệu gốc ViRHE4QA** và tìm dòng được ghi trong `raw_excel/train.xlsx`. D1 tra cứu phiên bản văn bản trong bộ dữ liệu, gồm cả văn bản cũ. [Độ phủ theo văn bản](../data/README.md#nguồn-văn-bản-d1)

Từ gốc repo, chạy cùng lệnh mở app ở mục [Chạy cục bộ](#chạy-cục-bộ). App tự tìm corpus theo thứ tự `outputs/d1-test/inputs/corpus.jsonl`, `data/processed/d1/dense/corpus.jsonl`, rồi `data/processed/d1/corpus.jsonl`. Có thể chỉ định tệp bằng `--d1-corpus "đường-dẫn/corpus.jsonl"`. Nếu máy chưa có D1, app mở riêng HCMUS. Để bật D1 từ bản clone hoặc gói giải nén, tải CSV đã ghim và chạy `data/prepare_virhe4qa.py` theo [hướng dẫn dữ liệu D1](../experiments/external_dataset/README.md), rồi mở lại app. Khi khởi động, app lập hai chỉ mục độc lập trong bộ nhớ và dùng chung checkpoint.

## Tra cứu HCMUS

Chọn khóa tuyển sinh trước khi nhập câu hỏi. K21–K25 tra quy chế 2021 và có thể mở quy chế 2026 cùng chủ đề để đối chiếu theo Điều 27. Từ K26, cả hai tab kết quả chỉ tra quy chế 2026. Chọn **Trước K21** sẽ thấy ngay thông báo thiếu quy chế nền. Chọn **Tra cứu chung** để tham khảo cả hai bản hiện có. Đổi khóa rồi nhấn **Enter** để tra lại câu đang nhập.

Hỏi **Điều kiện xét công nhận tốt nghiệp là gì** để mở danh sách điều kiện trong **Điều 17 khoản 3** với K21–K25, hoặc **Điều 19 khoản 1** từ K26. Demo nhận diện các cách hỏi chung về điều kiện và kiểm tra câu dẫn cùng danh sách trong nguồn. Khi tìm thấy đúng một khoản như vậy ở phiên bản đang hiển thị, demo đưa khoản đó lên đầu và mở trọn danh sách từ điểm a đến điểm f. Các câu hỏi cụ thể về nộp hồ sơ, người ký hoặc xếp hạng vẫn dùng cách xếp hạng thông thường.

Nhập câu hỏi về quy chế đào tạo của HCMUS và nhấn **Enter** hoặc **Tra cứu**. Tab **Kết quả tra cứu** mở chủ đề đầu tiên khi độ khớp đạt ngưỡng hoặc khi chưa cấu hình ngưỡng. Nếu độ khớp thấp, tab này thu gọn các chủ đề và chỉ rõ Điều, Khoản cần đối chiếu. Với học bổng, học phí hoặc chính sách khác, liên kết **Tra văn bản khác của Trường** mở [danh mục của Phòng Thanh tra – Pháp chế](https://ttpc.hcmus.edu.vn/he-thong-van-ban-quan-ly-noi-bo/).

## Trích đoạn trên giao diện

- Cạnh số hạng trên cả HCMUS và UIT có **Điểm Hybrid** cho cách tra kết hợp từ khóa và ngữ nghĩa, hoặc **Điểm BM25** cho cách tra từ khóa. Demo hiển thị điểm của Điều dùng để xếp hạng, làm tròn ba chữ số thập phân. Ở chế độ chỉ tra ngữ nghĩa, nhãn là **Điểm SimCSE-VN**. Khi HCMUS gộp nhiều Điều vào một chủ đề và mở bản khác với Điều quyết định thứ hạng, dòng **Xếp theo Điều…** cho biết nguồn điểm. Dùng điểm để so các kết quả của cùng một lượt tra trên cùng nguồn và phương pháp.
- Với khoản tốt nghiệp được ưu tiên, sinh viên thấy **Chọn theo khóa** cạnh số hạng. Ở **Tra cứu chung**, nhãn tương ứng là **Chọn theo điều kiện tốt nghiệp**.
- Mở **Vì sao có kết quả này?** dưới đoạn trích trên HCMUS hoặc UIT để xem **Điểm khớp với câu hỏi**. Đây là độ tương đồng ngữ nghĩa (cosine) giữa câu hỏi và đoạn được chọn, trên thang từ −1 đến 1, làm tròn hai chữ số. Mỗi phiên bản có điểm riêng. Trên tab **Từ khóa (BM25)**, thứ tự vẫn dựa trên mức khớp từ khóa. Khi tra trực tiếp điều kiện tốt nghiệp HCMUS, mục này giải thích khóa đã chọn và khoản liệt kê điều kiện. Bản 2026 dành cho K21–K25 ghi rõ mục đích đối chiếu.
- Mỗi tab có tối đa ba chủ đề theo thứ tự truy hồi. Mỗi chủ đề ghi năm quy chế, Điều, Khoản nếu có và tên Điều. Trong chế độ tra cứu chung, bản 2026 đứng trước. Mở dòng của bản 2021 để so sánh. Số hiệu dưới trích đoạn dẫn đến văn bản gốc của Trường. Mục **Áp dụng theo khóa tuyển sinh** tập hợp tên văn bản, hiệu lực và quy định chuyển tiếp. Nếu một Điều có sửa đổi, đường dẫn đến quyết định sửa đổi nằm ngay trên đoạn cần đối chiếu.
- Tab **Từ khóa (BM25)** chỉ liệt kê chủ đề có ít nhất một Điều nhận điểm từ khóa khác 0. Khi chỉ bản đối chiếu có tín hiệu, dòng mở bản đó ghi **Khớp từ khóa**. Nếu không có chủ đề đủ điều kiện, tab gợi ý cách đổi từ khóa. Cảnh báo độ khớp của phương pháp tra cứu chỉ hiện ở tab đã tính cảnh báo.
- Khi sửa câu hỏi hoặc đổi lựa chọn, giao diện ẩn kết quả cũ. Cả hai nguồn hiện **Đang tra cứu…** trong lúc chờ. Nếu gửi thất bại, ô nhập giữ câu hỏi và thông báo chỉ rõ nút gửi lại.
- Dùng phím **Tab** để tới ô hỏi hoặc nhóm tab. Khi tiêu điểm nằm trên tên tab, dùng **←** hoặc **→** để đổi nguồn HCMUS/ViRHE4QA hoặc đổi phương pháp trong HCMUS.
- Giao diện nối các dòng của cùng đoạn, bỏ dấu dàn trang, trình bày danh sách, công thức và bảng bằng các phần tử riêng. Nếu đoạn khớp bắt đầu hoặc kết thúc giữa một đoạn văn hay bảng, ứng dụng dùng vị trí ký tự trùng khớp trong cùng Khoản để hiển thị trọn phần đó. Điểm truy hồi được giữ nguyên khi hiển thị trích đoạn. Với câu hỏi về điểm trung bình, mở **Xem bảng xếp loại** để đọc từng khoảng điểm.
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

Khi demo đang chạy với cấu hình trên, có thể kiểm hành trình sinh viên bằng Chrome và Python có Playwright (đã thử với Playwright 1.56.0). Thêm `--d1` khi đã nạp ViRHE4QA để kiểm đổi nguồn bằng bàn phím, mở nội dung khi khớp tiêu đề, đối chiếu điểm với bộ phát triển và khôi phục sau lỗi gửi ở cả hai nguồn. Lệnh dùng hai chiều rộng 1440 và 320 px. Để lưu ảnh PNG, thêm `--screenshots` và đường dẫn tới một thư mục mới.

```powershell
python -X utf8 tools/check_search_ui.py --url http://127.0.0.1:7860
```
