Viết cho: Huy và Minh, Nhóm 14.

# Chọn Khoản và cảnh báo ngoài phạm vi trên 16 câu phát triển

**Giữ bản Hybrid đang dùng.** Cả bốn bản chọn đúng Khoản ở 7/8 câu có đáp án và cùng tự tin sai ở một câu hỏi về đăng ký bù. Khi yêu cầu các phương pháp đồng ý về chủ đề, ba câu có đáp án bị cảnh báo thêm. Trên bộ này, thay đổi khiến sinh viên phải mở kết quả nhiều hơn.

## Kết quả của bốn bản

K thay cách chọn đoạn **bên trong** mỗi Điều. G chỉ chấp nhận khi cosine đủ ngưỡng, điểm BM25 cao nhất dương và BM25, SimCSE-VN, Hybrid dẫn đầu ở cùng chủ đề. Một câu được tính là **tự tin sai phạm vi** khi hai quy chế thiếu dữ kiện để trả lời nhưng tab tra cứu mở kết quả như đáng tin. “Thấy căn cứ ngay” yêu cầu đọc được nội dung đủ trả lời, đúng phiên bản, trong thẻ đầu mà không bấm mở.

| Chỉ số | A · Hiện tại | K · Chọn lại Khoản | G · Kiểm chủ đề | K+G |
| --- | ---: | ---: | ---: | ---: |
| Đúng Điều hạng 1, trong 8 câu có đáp án | 7/8 | 7/8 | 7/8 | 7/8 |
| Đúng chủ đề hạng 1 | 7/8 | 7/8 | 7/8 | 7/8 |
| Đúng Khoản hạng 1 | 7/8 | 7/8 | 7/8 | 7/8 |
| Sai Khoản khi Điều đứng đầu đã đúng | 0/7 | 0/7 | 0/7 | 0/7 |
| Chấp nhận câu có đáp án | 5/8 | 5/8 | 2/8 | 2/8 |
| Sinh viên thấy căn cứ đúng ngay | 3/8 | 3/8 | 2/8 | 2/8 |
| Đúng Khoản hạng 1 nhưng phải bấm mới đọc được căn cứ | 4/7 | 4/7 | 5/7 | 5/7 |
| Tự tin sai ở câu gần chủ đề | 1/6 | 1/6 | 1/6 | 1/6 |
| Tự tin sai ở câu ngoài lĩnh vực | 0/2 | 0/2 | 0/2 | 0/2 |

**So sánh ghép cặp K+G với A.** Về Khoản và cảnh báo câu gần chủ đề, số câu sửa đúng và số câu làm sai thêm đều bằng 0. Về độ bao phủ, K+G mất ba câu và không mở thêm câu nào, giảm 37,5 điểm phần trăm. Về căn cứ nhìn thấy ngay, K+G mất một câu, giảm 12,5 điểm phần trăm. Số liệu ghi nhận trên bộ phát triển do Codex gán nhãn. Bộ xác nhận độc lập 270 tình huống trong thiết kế vẫn chưa được chạy. [Số đếm và mã câu của từng cặp](summary.json) · [Thiết kế và điều kiện thay bản](../../clause-scope-comparison.md#điều-kiện-thay-bản-hiện-tại)

## Các lỗi ảnh hưởng trực tiếp tới sinh viên

1. **Câu 03 trên phiếu, `pilot-06` · Hiển thị kết quả đáng tin cho câu thiếu căn cứ.** Sinh viên hỏi đợt đăng ký bù khi điểm môn tiên quyết chưa lên hệ thống. Cả bốn bản xếp QĐ 2021, Điều 18 Khoản 5, về điều kiện xét tốt nghiệp ở hạng 1. Trên giao diện, đoạn mở đầu là QĐ 2026, Điều 19 Khoản 3, về xếp hạng tốt nghiệp. Cosine đạt 0,6928 và cả ba cách tìm cùng chọn chủ đề tốt nghiệp. Điều kiện G vì thế vẫn cho qua. Để trả lời cần thông báo của Khoa trong đúng học kỳ. [Nhãn, nguồn ngoài quy chế và các Khoản đã rà](../../../../data/development/clause-scope-pilot.jsonl)
2. **Câu 07, `pilot-13` · Xếp sai Điều nên cả bốn bản trượt Khoản.** Câu hỏi chỉ rõ góp ý của **nơi tuyển dụng**. Điều 8 Khoản 1 bản 2021 xếp đầu, nói về phản hồi của **người học**. Điều 26 Khoản 3 bản 2026 mới nêu ý kiến người sử dụng lao động. Điều này xếp hạng 4 và cả A lẫn K đều chọn đúng Khoản 3 ở hạng đó. Đổi đoạn trong cùng Điều không đưa căn cứ lên hạng 1. Cả bốn bản đều có cảnh báo.
3. **Câu 05, 13 và 15 trên phiếu · G cảnh báo thêm dù đã trúng Khoản.** Ba câu lần lượt hỏi điểm chuyên cần của môn thực hành, bảng điểm kèm bằng và giới hạn giờ giảng tập trung. Với câu thực hành, A và K mở sẵn đúng căn cứ, cosine 0,7764. BM25 chọn chủ đề chương trình đào tạo, còn SimCSE-VN và Hybrid chọn đánh giá học phần. G và K+G thu gọn thẻ dù căn cứ đủ trả lời.
4. **Ba câu nêu đích danh bản 2021 · Phải mở phần đối chiếu để đọc đúng bản.** Ở câu 10, 13 và 15 trên phiếu, bộ truy hồi lấy đúng Khoản năm 2021 nhưng thẻ đầu đưa bản 2026 lên trước. Điều này giải thích vì sao số Khoản đúng ở hạng 1 cao hơn số căn cứ nhìn thấy ngay. Trên cả 8 câu có đáp án, số lần chọn sai phiên bản ở hạng 1 khi chủ đề đúng là 0. Việc sắp bản ở giao diện mới làm đoạn người dùng đọc đầu tiên khác đoạn hạng 1.

## Đối chiếu cả 16 câu

Cột đầu giữ số thứ tự trên hai phiếu Huy và Minh. Mã `pilot-xx` dùng để tra nguyên văn trong dữ liệu. “Mở” nghĩa là thẻ kết quả đầu mở sẵn. “Cảnh báo” nghĩa là thẻ thu gọn và ứng dụng yêu cầu đối chiếu thêm. Bảng gộp các bản có cùng quyết định cho từng câu. Cosine lấy từ đoạn của Điều hạng 1, trước khi giao diện gộp chủ đề. Bảng làm tròn bốn chữ số, phép quyết định dùng điểm gốc. [Câu hỏi, nhãn và trang PDF](../../../../data/development/clause-scope-pilot.jsonl) · [Xếp hạng, cosine gốc và kết quả riêng của từng bản](predictions.jsonl)

### Tám câu có đáp án

| Câu trên phiếu · mã | Sinh viên cần biết | Khoản chuẩn và đoạn hạng 1 của A, K | Cosine | A và K | G và K+G | Căn cứ sinh viên đọc được |
| --- | --- | --- | ---: | --- | --- | --- |
| 04 · pilot-07 | Trường có quản lý dữ liệu việc làm sau tốt nghiệp? | Đúng 2026, Điều 9 Khoản 2 | 0,5440 | Cảnh báo | Cảnh báo | Mở thẻ đầu để đọc |
| 05 · pilot-15 | Điểm chuyên cần của môn thực hành có được tính? | Đúng 2026, Điều 10 Khoản 3. Cũng chấp nhận 2021, Điều 9 Khoản 2 | 0,7764 | Mở | Cảnh báo | A, K cho thấy ngay. G, K+G yêu cầu mở thẻ |
| 06 · pilot-11 | Phòng nào phụ trách quy định về bảo quản bài thi? | Đúng 2026, Điều 10 Khoản 4 | 0,6313 | Mở | Mở | Cả bốn cho thấy ngay tên phòng |
| 07 · pilot-13 | Trường có dùng góp ý của nơi tuyển dụng? | Sai 2021, Điều 8 Khoản 1. Chuẩn là 2026, Điều 26 Khoản 3, ở hạng 4 | 0,5160 | Cảnh báo | Cảnh báo | Chủ đề đầu thiếu căn cứ về nơi tuyển dụng |
| 08 · pilot-09 | Có quyền được biết điều kiện chuyển ra khỏi chương trình tích hợp? | Đúng 2026, Điều 24 Khoản 2 | 0,6341 | Mở | Mở | Cả bốn cho thấy ngay quyền được cung cấp thông tin |
| 10 · pilot-03 | Ai quyết định mức công khai ý kiến của người học? | Đúng 2021, Điều 8 Khoản 3 **lần xuất hiện thứ hai**, điểm b | 0,5831 | Cảnh báo | Cảnh báo | Mở thẻ rồi mở bản 2021. Cả bốn phân biệt đúng hai Khoản trùng số |
| 13 · pilot-05 | Bảng điểm kèm bằng có ghi kết quả từng môn? | Đúng 2021, Điều 18 Khoản 4 | 0,6776 | Mở | Cảnh báo | Mở bản 2021. G, K+G còn yêu cầu mở thẻ đầu |
| 15 · pilot-01 | Một ngày được xếp bao nhiêu giờ giảng cho một môn học tập trung? | Đúng 2021, Điều 6 Khoản 6 | 0,6374 | Mở | Cảnh báo | Mở bản 2021. G, K+G còn yêu cầu mở thẻ đầu |

### Sáu câu gần chủ đề và hai câu ngoài lĩnh vực

Cả tám câu đều có nhãn cần cảnh báo. Cột Khoản ghi **đoạn thực tế được chọn ở hạng 1** để có thể tái hiện cả những lần ứng dụng cảnh báo đúng.

| Câu trên phiếu · mã | Dữ kiện sinh viên hỏi | Đoạn hạng 1 của A và K | Cosine A / K | Cả bốn bản |
| --- | --- | --- | ---: | --- |
| 01 · pilot-08 | Khoa có xem xét mở thêm lớp đã kín trong đợt đăng ký cụ thể? | 2026, Điều 6 Khoản 1 | 0,5548 | Cảnh báo đúng. Cần thông báo của Khoa |
| 02 · pilot-10 | Cách bảo quản rau húng | 2026, Điều 14. A chọn Khoản 5, K chọn Khoản 2 | 0,2038 / 0,1711 | Cảnh báo đúng. Đây là câu duy nhất K đổi đoạn hạng 1 |
| **03 · pilot-06** | **Đợt đăng ký bù khi điểm môn tiên quyết chưa lên hệ thống** | **2021, Điều 18 Khoản 5** | **0,6928** | **Cả bốn tự tin sai. Cần lịch điều chỉnh học phần của Khoa** |
| 09 · pilot-02 | Mã bưu chính gửi đơn phúc tra | 2021, Điều 13 Khoản 1 | 0,5376 | Cảnh báo đúng. Cần địa chỉ bưu chính nơi tiếp nhận |
| 11 · pilot-14 | Số điện thoại nội bộ để mượn micro | 2021, Điều 11 Khoản 3 | 0,4260 | Cảnh báo đúng. Cần thông tin liên hệ của đơn vị cho mượn |
| 12 · pilot-16 | Mệnh giá tem gửi bưu thiếp sang Nhật | 2026, Điều 2 Khoản 6 | 0,2257 | Cảnh báo đúng. Cần biểu cước bưu chính |
| 14 · pilot-12 | Được ghép môn tự chọn giữa các hướng chuyên ngành CNTT? | 2026, Điều 3 Khoản 3 | 0,5026 | Cảnh báo đúng. Cần danh mục môn của chương trình cụ thể |
| 16 · pilot-04 | Phí dịch bảng điểm tiếng Đức mỗi trang | 2026, Điều 14 Khoản 3 | 0,3436 | Cảnh báo đúng. Cần biểu phí dịch |

## Điều kiện chạy và kiểm lại

Mỗi câu được gửi riêng như khi sinh viên tra cứu. Bốn bản dùng chung điểm BM25 và cosine của 273 đoạn, cùng thứ tự đầy đủ của 51 Điều thuộc 26 chủ đề. Trọng số BM25 là **0,6**, ngưỡng cosine là **0,6201629042625427** chọn trên D1-dev. Lượt chạy dùng CPU, 4 luồng, seed 42, checkpoint ở revision `608779b86741a8acd8c8d38132974ff04086b138`. Đầu vào đã đối chiếu SHA-256 của cấu hình, corpus, bảng đối ứng, bộ 16 câu và bảy tệp của checkpoint. [Manifest, phiên bản phần mềm và checksum mã thực chạy](summary.json) · [Lệnh tái lập](../../README.md#so-sánh-trước-khi-thay-bản-truy-hồi)

Các tệp HTML trong thư mục `html/` của lượt chạy lưu đoạn chính, bản đối chiếu, liên kết nguồn và cảnh báo của từng trường hợp. Đã so cả HTML của tab tra cứu và thông báo của A với endpoint Gradio thật trên đủ 16 câu. Đã mở 64 trang bằng Chrome, kiểm trạng thái mở mặc định, liên kết nguồn và các thao tác cần để đọc căn cứ. Hai lần chạy cho cùng byte dự đoán và HTML.

Phần chấm căn cứ dùng đúng phiên bản, mã Khoản và cụm từ cần thiết trong câu nguồn. Codex thực hiện lượt rà ý nghĩa và hiển thị trên bộ mở này. Thiết kế dành hai lượt chấm độc lập cho giai đoạn xác nhận.
