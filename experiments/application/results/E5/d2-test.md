# Phân tích lỗi trên D2-test (E5)

Lượt đối chiếu ngày 26/11/2026 dùng [nhãn đã chốt trước khi chạy](../../../../data/d2/queries_d2.jsonl) và ba bảng xếp hạng đủ 51 Điều trong `outputs/d2-test/runs/`. SHA-256 của nhãn, corpus và các bảng xếp hạng khớp [kết quả E2/E3](../D2/summary.json). Trọng số BM25 trong Hybrid là 0,6 và ngưỡng cảnh báo là 0,6201629042625427, theo [cấu hình chốt trên D1-dev](../../../external_dataset/results/D1-dev-tuning/handoff.md).

Đối chiếu Khoản của từng đoạn được chọn với hai PDF chính thức có SHA-256 khớp [metadata D2](../../../../data/d2/documents.yaml). Số trang trong bảng tính từ trang đầu của tệp PDF. Corpus 2026 dùng bản ChatGPT chép từ scan, được nhóm làm sạch và hiệu đính. [QĐ 1175/2021](https://www.ctda.hcmus.edu.vn/wp-content/uploads/2023/03/Quy-che-dao-tao-2021.pdf) · [QĐ 3087/2026](https://www.hcmus.edu.vn/wp-content/uploads/2026/10/QD3087_QD-Quy-che-dao-tao-2026.pdf)

Các bộ ba trong bảng theo thứ tự **BM25 / SimCSE-VN / Hybrid**. Mã `2021.13.1` chỉ Khoản 1 Điều 13 của bản 2021. Hạng Điều chuẩn là vị trí sớm nhất của một Điều có trong nhãn. Dùng [bảng đối ứng](../../../../data/d2/article_map.tsv) để suy ra chủ đề chuẩn từ nhãn Điều, rồi tính hạng sau khi gộp các Điều, giữ lần xuất hiện đầu tiên của mỗi chủ đề. Khoản ở hạng 1 là Khoản chứa trích đoạn được chọn từ Điều đứng đầu. Hybrid ghi tin cậy khi cosine của trích đoạn đó đạt ngưỡng.

## Ba câu ngoài phạm vi được đánh dấu tin cậy

Cả ba câu dưới đây có nhãn Điều và Khoản rỗng. Dấu `—` là hạng Điều và chủ đề chuẩn không xác định. Hai quy chế dùng để chấm D2 không có lịch ngày hội tuyển dụng, thủ tục xin giấy xác nhận để mua vé xe buýt ưu đãi hay bảng mức thu học phí mỗi tín chỉ theo ngành và năm. Chẳng hạn, QĐ 3087 nhắc đến học phí khi quy định điều kiện hoãn thi và việc cung cấp thông tin cho sinh viên chương trình tích hợp.

| Mã câu và ý hỏi | Hạng chuẩn của ba phương pháp | Khoản ở hạng 1 | Cosine Hybrid | Đối chiếu nguyên văn |
|---|---|---|---:|---|
| `d2-huy-review-016` · Khi nào tổ chức ngày hội tuyển dụng cho sinh viên năm cuối? | — / — / — | `2021.12.4` / `2021.18.8` / `2021.18.8` | 0,636530 | `2021.18.8` nói về thông báo xét tốt nghiệp vào cuối học kỳ (tr. 15). `2021.12.4` nói về kiểm tra bù trước ngày thi cuối học kỳ (tr. 10). Mốc thời gian trong cả hai Khoản dành cho sự kiện khác. |
| `d2-huy-review-029` · Xin giấy xác nhận để mua vé xe buýt ưu đãi như thế nào? | — / — / — | `2021.13.1` / `2021.13.1` / `2021.13.1` | 0,689995 | `2021.13.1` nói về giấy xác nhận đề cương, số tiết, số tín chỉ và điểm để xin miễn học phần đã học ở trường khác (tr. 10–11). Giấy xác nhận có mục đích khác với giấy dùng để mua vé xe buýt. |
| `d2-huy-review-052` · Học phí một tín chỉ ngành Công nghệ thông tin năm nay là bao nhiêu? | — / — / — | `2026.21.1` / `2026.22.2` / `2026.11.3` | 0,625617 | `2026.21.1` nói về chuyển ngành hoặc chương trình (tr. 19). `2026.22.2` nói về trao đổi sinh viên và công nhận tín chỉ (tr. 20). `2026.11.3` quy định điểm đạt và việc tích lũy tín chỉ (tr. 11). Cả ba đoạn đều thiếu mức thu được hỏi. |

## Năm ca trượt hạng 1 theo Điều

Hybrid trượt hạng 1 ở **18/86 câu trong phạm vi theo Điều** và **17/86 theo chủ đề**. Trong 18 ca theo Điều, 12 được đánh dấu tin cậy và 6 có cảnh báo. Điều chuẩn đầu tiên của Hybrid đứng hạng 2 ở 9 ca, hạng 3 ở 6 ca và hạng 4 ở 3 ca. BM25 đưa một Điều chuẩn lên đầu ở 1 ca, SimCSE-VN ở 3 ca và cả hai đều xếp sai ở 14 ca.

Chọn có chủ đích 5 ca để phủ ba vị trí của Điều chuẩn, tình huống mỗi phương pháp đối chứng xếp đúng Điều ở hạng 1, tình huống cả ba xếp sai và ca Hybrid chỉ khớp ở cấp chủ đề. Mẫu này dùng để minh họa các dạng sai. Tổng số ca lỗi đã đọc trong E5 là 28, gồm 8 ca D2 và [20 ca D1-test](d1-test.md).

| Mã câu và ý hỏi | Khoản chuẩn | Hạng Điều chuẩn | Hạng chủ đề chuẩn | Khoản ở hạng 1 | Hybrid | Đối chiếu nguyên văn |
|---|---|---|---|---|---|---|
| `d2-minh-review-008` · Đề cương có ghi cách kiểm tra học phần không? | `2021.3.2`, `2021.9.1`, `2026.10.1` | 11 / 1 / 2 | 9 / 1 / 2 | `2021.13.1` / `2021.3.1` / `2021.13.1` | 0,534052 · Cảnh báo | Các Khoản chuẩn quy định thông tin đánh giá trong đề cương (2021 tr. 3, 8 và 2026 tr. 10). BM25 và Hybrid xếp đầu đoạn nói về đề cương dùng để xin miễn học phần (2021 tr. 10–11). SimCSE-VN xếp Điều 3 ở hạng 1 với đoạn định nghĩa học phần ở Khoản 1 (2021 tr. 2–3). Hybrid có đúng Khoản `2021.3.2` ở hạng 2. |
| `d2-minh-review-019` · Đã đủ tín chỉ thì còn điều kiện nào để được xét tốt nghiệp? | `2021.17.3`, `2026.19.1`, `2026.19.5` | 2 / 3 / 2 | 1 / 3 / 1 | `2021.18.5` / `2026.22.2` / `2021.18.5` | 0,739511 · Tin cậy | Các Khoản chuẩn nêu điều kiện chung như hoàn tất giáo dục thể chất, đạt chuẩn ngoại ngữ và nộp hồ sơ sau khi đủ điều kiện (2021 tr. 14 và 2026 tr. 17). Hybrid và BM25 đưa lên đầu trường hợp đã hết thời gian học tối đa và được hoàn thiện một số điều kiện còn thiếu trong 3 năm kể từ khi thôi học (2021 tr. 15). Cả hai vẫn đúng chủ đề vì Điều 18 và Điều 17 của bản 2021 cùng thuộc `T16`. SimCSE-VN trả đoạn công nhận tín chỉ trao đổi (2026 tr. 20). |
| `d2-minh-review-026` · Có thể chuyển đổi tối đa bao nhiêu tín chỉ? | `2021.13.4`, `2026.18.3` | 4 / 7 / 4 | 3 / 6 / 3 | `2021.7.2` / `2026.22.2` / `2021.7.2` | 0,674622 · Tin cậy | `2021.13.4` nêu giới hạn 25% khối lượng học tập tối thiểu của chương trình (tr. 11). `2026.18.3` điểm c nêu mức 25% và mức tối đa 50% cho các học phần tích lũy tại Trường (tr. 16). Hybrid và BM25 trả giới hạn đăng ký mỗi học kỳ (2021 tr. 6), còn đoạn SimCSE-VN chọn nói về trao đổi sinh viên (2026 tr. 20). |
| `d2-huy-review-044` · Các môn ghi BL hoặc M có tính vào điểm trung bình không? | `2021.13.3`, `2026.18.3` | 1 / 9 / 2 | 1 / 6 / 2 | `2021.13.3` / `2021.15.2` / `2026.16.2` | 0,672790 · Tin cậy | `2021.13.3` và `2026.18.3` điểm b loại BL và M khỏi điểm trung bình học kỳ và tích lũy (2021 tr. 11 và 2026 tr. 16). BM25 chọn đúng Khoản. SimCSE-VN chọn công thức tính chung (2021 tr. 12), còn đoạn Hybrid đứng đầu liệt kê các học phần được loại trừ khi tính trung bình mà chưa giải đáp BL/M (2026 tr. 14). Hybrid xếp đúng Điều 13 của bản 2021 ở hạng 2 với đoạn định nghĩa BL và M tại Khoản 2 (2021 tr. 11). |
| `d2-huy-review-047` · Sau khi lỡ buổi thi cuối kỳ, hạn nộp đơn hoãn thi là bao lâu? | `2021.12.2`, `2026.14.2`, `2026.14.3` | 3 / 3 / 3 | 2 / 2 / 2 | `2026.11.4` / `2026.11.4` / `2026.11.4` | 0,668789 · Tin cậy | Cả ba chọn đoạn nói về điểm khi vắng thi và dẫn sang Điều 14 (2026 tr. 11). Thời hạn **05 ngày làm việc kể từ ngày thi** nằm ở `2021.12.2` và `2026.14.2` (2021 tr. 10 và 2026 tr. 13). `2026.14.3` cho phép xem xét gia hạn nộp hồ sơ trong trường hợp đặc biệt bất khả kháng (tr. 13). Hybrid chọn đúng Khoản có thời hạn ở hạng 3. |

## Hướng kiểm tra tiếp theo

- Với đoạn chỉ dẫn chiếu sang Điều khác, thử truy hồi thêm Khoản được dẫn chiếu và đo xem đoạn đứng đầu có chứa thông tin được hỏi hay không. Câu hoãn thi minh họa trường hợp phù hợp để thiết kế phép kiểm.
- Với cảnh báo, thử kiểm xem đoạn đã chọn có đủ căn cứ trả lời nội dung được hỏi. Ba ca ngoài phạm vi cho thấy cosine có thể đạt ngưỡng khi đoạn chỉ gần về chủ đề hoặc từ ngữ. Đánh giá các thay đổi trên tập phát triển riêng và giữ D2 làm tập kiểm thử.

Các lý do trong bảng mô tả chỗ lệch giữa câu hỏi và nội dung được trả về. Ảnh hưởng riêng của tách từ, độ dài đoạn, điểm kết hợp và các hướng cải thiện trên cần phép đối chứng.
