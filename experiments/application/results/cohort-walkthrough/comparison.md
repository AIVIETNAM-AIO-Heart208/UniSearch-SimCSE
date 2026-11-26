Viết cho: Huy và Minh, đọc kết quả kiểm hai mẫu tra cứu quy chế.

# Chạy thử hai cách chọn khóa tuyển sinh

Ngày 26/11/2026, Codex chạy Chrome ngoại tuyến trên ba nhiệm vụ. Mỗi tổ hợp giữa mẫu và nhiệm vụ bắt đầu trong một phiên trình duyệt mới. Ở cả sáu lượt, đoạn căn cứ đầu tiên trên màn hình đủ để trả lời đúng theo phiếu chấm. Mẫu B bớt hai thao tác khi tra cứu chung. Hai nhiệm vụ cá nhân cần cùng số thao tác ở cả hai mẫu. [Phiếu đã điền cho sáu lượt mô phỏng](observations.tsv)

| Nhiệm vụ | Mẫu A, chọn khóa trước | Mẫu B, hỏi khóa khi cần | Căn cứ đầu tiên trình duyệt chỉ được ở cả hai mẫu |
| --- | --- | --- | --- |
| K24, hỏi quy chế áp dụng cho mình | 4 thao tác, chọn và xác nhận năm trước khi gửi | 4 thao tác, chọn và xác nhận năm sau khi gửi | Quy chế 2026, Điều 27 khoản 2. Với khóa tuyển từ năm 2025 trở về trước, Trường lựa chọn áp dụng quy định mới có lợi hơn cho người học |
| K26, cùng câu hỏi cá nhân | 4 thao tác, chọn và xác nhận năm trước khi gửi | 4 thao tác, chọn và xác nhận năm sau khi gửi | Quy chế 2026, Điều 27 khoản 1. Quy chế áp dụng từ khóa tuyển năm học 2026–2027 |
| Tra cứu chung, hỏi giúp bạn về điểm chuyên cần | 4 thao tác, phải nhập cả khóa của người tra giúp | 2 thao tác, nhập câu rồi gửi | Quy chế 2026, Điều 10 khoản 3 liệt kê điểm chuyên cần trong các thành phần điểm học phần thực hành |

Một thao tác ở đây là nhập cả câu bằng một lần điền, gửi câu, chọn một năm hoặc xác nhận năm. Sau khi kết quả hiện, trình duyệt bấm vào đoạn đầu tiên đang hiển thị. Lần bấm chỉ căn cứ được ghi vào thời gian đến căn cứ, còn cột số thao tác đếm đến lúc kết quả hiện. Mã chạy chọn đoạn theo thứ tự đọc trên màn hình. Bước chấm sau đó đối chiếu đoạn vừa chọn, kết luận và Điều/Khoản với đáp án trong hướng dẫn.

## Lỗi khi mở nguồn và kết quả kiểm lại

Trong cả hai lượt tra cứu chung, đoạn trích đúng nhưng liên kết mở đầu PDF 2026. Trang PDF chứa Điều 10 khoản 3 là **trang 10**. Cả hai mẫu đã dùng số trang đã đối chiếu trong dữ liệu phát triển để mở đúng trang đó. Khi mở bản 2021 trong cùng thẻ, liên kết đến **trang 8**, nơi có Điều 9 khoản 2. [Căn cứ và số trang đã kiểm ở câu pilot-15](../../../../data/development/clause-scope-pilot.jsonl)

Đã nhấn liên kết nguồn trong từng phiên và đọc địa chỉ ở thẻ PDF thực sự mở. Trước khi sửa, 4/6 liên kết của các căn cứ đầu tiên mở đúng trang. Sau khi sửa, kết quả là 6/6. Ở từng tổ hợp mẫu và nhiệm vụ, đoạn được chọn và trình tự thao tác đều khớp trước và sau sửa. Thanh công cụ PDF của Chrome hiển thị đúng trang 10/21 và 21/21 ở bản 2026, trang 8/18 ở bản 2021. [Địa chỉ PDF trước và sau của từng lượt](pdf-pages.tsv)

## Kiểm lại gói mô phỏng

Đã chạy lại sau khi bỏ phiếu dành cho người tham gia. Trên ZIP mô phỏng có SHA-256 `b32a6e1332534c11bde8fe6c47b97bf346ce2ff25fc88d927433df74326bf2cb`, cả sáu lượt vẫn tìm đúng căn cứ đầu, mở đúng trang PDF và có số thao tác như bảng trên. Cùng một bộ 16 cặp kết quả đã qua kiểm tra ở chiều rộng 1440, 390 và 320 px.

## Cách đọc thời gian

Đồng hồ trình duyệt bắt đầu khi trang đầu sẵn sàng, sau khi đọc tình huống và trước khi điền hay chọn khóa. Trên gói đã sửa liên kết PDF, trung vị từ lúc bắt đầu tới lần bấm vào căn cứ là **0,0951 giây ở A** và **0,0940 giây ở B**, mỗi mẫu có ba lượt đạt. Đây là thời gian Playwright điều khiển Chrome. Thời gian đọc hiểu, mức độ dễ dùng và tỷ lệ bỏ dở của sinh viên nằm ngoài phạm vi đo. [Hai mốc thời gian của từng lượt](observations.tsv)

Phiên chạy dùng Chrome 158.0.8127.88, Playwright 1.56.0, Python 3.14.0, khung nhìn 1440 × 900 và thứ tự gán ngẫu nhiên cố định bằng seed `20261126`. Hai mẫu dùng cùng bộ 17 câu. Xếp hạng của 16 câu phát triển vẫn dùng trọng số Hybrid 0,6 và ngưỡng 0,6201629042625427. Câu cá nhân tra trực tiếp Điều 27. Mã SHA-256 của ZIP trước sửa là `d93aaf0765656b169c4329c21aab04a1f3c3f8d046c3b9e382ec50260362ec44`, sau sửa là `c7eb17d38ec2d4251ce0e988d0cc7abdc819d36b2b8caddbeadffb804b63034e`. [Cách chạy lại và xuất ảnh](../../README.md#chạy-sáu-lượt-mô-phỏng)
