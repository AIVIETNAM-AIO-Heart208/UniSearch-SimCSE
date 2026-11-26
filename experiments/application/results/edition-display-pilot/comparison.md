Viết cho: Huy và Minh, Nhóm 14.

# Mở đúng phiên bản quy chế khi sinh viên nêu năm

Trên 16 câu phát triển, số câu **đọc được ngay căn cứ đúng** tăng từ **3/8 lên 5/8 câu có đáp án**. Hai câu được lợi đều hỏi quy chế 2021. Đó là câu về bảng điểm kèm bằng và câu về giới hạn giờ giảng tập trung. Không có câu nào mất căn cứ đã nhìn thấy ở bản hiện tại. [Kết quả và mã đoạn của từng câu](summary.json)

## Kết quả theo cách sinh viên hỏi

“Thấy ngay” nghĩa là nội dung đủ trả lời nằm trong đúng Khoản, đúng phiên bản, ở thẻ đầu đang mở. Sinh viên có thể cuộn để đọc. Nếu còn phải bấm mở thẻ, mở bản đối chiếu hoặc đọc tiếp thì câu đó chưa đạt.

| Cách hỏi | Số câu | Có đáp án trong quy chế | Thấy ngay hiện tại | Thấy ngay khi ưu tiên năm |
| --- | ---: | ---: | ---: | ---: |
| Chỉ rõ quy chế 2021 | 3 | 3 | 0/3 | 2/3 |
| Chỉ rõ quy chế 2026 | 4 | 4 | 2/4 | 2/4 |
| Chỉ nhắc năm học 2025–2026 | 2 | 0 | Không áp dụng | Không áp dụng |
| Không nêu năm | 7 | 1 | 1/1 | 1/1 |
| **Tổng** | **16** | **8** | **3/8** | **5/8** |

- **Phiếu 13, `pilot-05`.** Câu hỏi yêu cầu quy chế 2021 về giấy phát kèm bằng. Trước thử nghiệm, thẻ mở ở Điều 19 Khoản 5 bản 2026 về thủ tục xét tốt nghiệp. Bản thử mở Điều 18 Khoản 4 bản 2021, cho thấy ngay quy định cấp bảng điểm theo từng học phần.
- **Phiếu 15, `pilot-01`.** Thẻ đầu chuyển sang Điều 6 Khoản 6 bản 2021. Sinh viên đọc được giới hạn 4 giờ giảng mỗi ngày cho một học phần xếp lịch tập trung.
- **Phiếu 10, `pilot-03`.** Bản thử đưa đúng Điều 8 Khoản 3, lần xuất hiện thứ hai của bản 2021, lên trước. Cosine 0,5831 vẫn thấp hơn ngưỡng. Sinh viên cần một lần mở thẻ để đọc căn cứ, trước đây cần mở thẻ rồi mở thêm bản 2021. Câu này vẫn chưa đạt tiêu chí “thấy ngay”.
- **Phiếu 03, `pilot-06`.** Câu nhắc năm học để hỏi lịch đăng ký bù. Cả hai cách hiển thị vẫn tự tin sai vì quy chế thiếu lịch cụ thể của Khoa. Cả chín câu chỉ nêu năm học hoặc không nêu năm có HTML giống hệt ở hai cách hiển thị. [Câu hỏi, nhãn và trang nguồn](../../../../data/development/clause-scope-pilot.jsonl)

Trong bảy câu yêu cầu rõ phiên bản, số thẻ đầu ghi đúng năm tăng từ **4/7 lên 7/7**. Số câu thấy đủ căn cứ trong nhóm này tăng từ **2/7 lên 4/7**. Riêng câu về ý kiến nhà tuyển dụng (`pilot-13`) vẫn cần Điều 26 Khoản 3 bản 2026 ở hạng 4.

## Điều kiện thử và giới hạn

Lượt thử ngoại tuyến phát lại điểm BM25 và cosine đã lưu của bản Hybrid, trọng số **0,6**, ngưỡng **0,6201629042625427**, trên cùng hai quy chế. Đã tính lại đủ thứ tự 51 Điều, điểm, đoạn trích và cosine hạng 1 ở từng câu. HTML của 16 trang đối chứng khớp từng byte với lượt A. Bản thử chỉ đổi thứ tự phiên bản trong cùng chủ đề khi nhận diện được duy nhất một bản sinh viên yêu cầu và chủ đề có bản đó.

Đã mở 32 trang trong Chrome khi tắt mạng, đọc phần chữ thực sự hiện ở trạng thái mặc định, so cảnh báo, trạng thái thẻ, số phiên bản và liên kết nguồn theo từng chủ đề. Bộ truy hồi đúng Khoản **7/8**, chấp nhận **5/8** câu có đáp án và tự tin sai **1/6** câu gần chủ đề, **0/2** câu ngoài lĩnh vực ở cả hai cách hiển thị. [Điểm và giao diện đối chứng](../clause-scope-pilot/comparison.md) · [Lệnh tái lập](../../README.md#thử-mở-phiên-bản-được-hỏi)

Bộ mở này đã được dùng để tìm lỗi ưu tiên bản 2026. Mức tăng quan sát là 25 điểm phần trăm trên tám câu có đáp án. Chỉ một câu có đáp án trong nhóm không nêu năm. Chưa đo hiệu quả trên câu hỏi độc lập ngoài bộ này. Bản chạy của ứng dụng tiếp tục dùng cách hiển thị đã công bố.

## Có nên chọn khóa trước khi hỏi?

**Đề xuất đặt “Khóa tuyển sinh (năm nhập học)” cạnh ô câu hỏi, cho phép tra cứu ngay hoặc chọn khóa trước.** Khi sinh viên chọn, giữ lựa chọn trong phiên và cho phép đổi. Cần phân biệt ba loại năm mà một sinh viên có thể nhắc trong cùng một câu.

| Sinh viên nói gì | Cách giao diện nên xử lý |
| --- | --- |
| “Em K24, muốn xem quy chế 2026” | Mở văn bản 2026 theo yêu cầu và dùng khóa 2024 để giải thích phạm vi áp dụng. Cho phép đối chiếu hai bản |
| “Quy định nào áp dụng cho em?” | Dùng năm tuyển sinh đã chọn. Nếu còn thiếu và câu trả lời phụ thuộc vào khóa, hỏi ngắn ngay tại kết quả |
| “Em đăng ký học kỳ 2 năm 2025–2026” | Dùng năm học làm bối cảnh thời gian. Khi câu hỏi cần lịch của Khoa, chỉ rõ nguồn thông báo cần đối chiếu |
| Muốn tra chung, so hai bản hoặc chưa biết khóa | Cho gửi câu hỏi ngay và giữ cả hai nguồn để đối chiếu |

Điều 27 khoản 1 của quy chế 2026 áp dụng bản mới cho các khóa tuyển từ năm học 2026–2027. Theo khoản 2, với khóa tuyển từ năm 2025 trở về trước, **Trường** lựa chọn áp dụng quy định mới có lợi hơn cho người học. Vì vậy, với sinh viên K24, thông tin khóa giúp giải thích điều khoản chuyển tiếp. Tự loại toàn bộ bản 2026 sau khi người dùng chọn K24 có thể làm mất căn cứ cần đọc. Với khóa trước năm học 2021–2022, cần thêm văn bản của giai đoạn tương ứng khi xác định quy định cũ. [QĐ 3087, Điều 27, trang PDF 21](https://www.hcmus.edu.vn/wp-content/uploads/2026/10/QD3087_QD-Quy-che-dao-tao-2026.pdf#page=21) · [QĐ 1175, Điều 24, trang PDF 18](https://www.ctda.hcmus.edu.vn/wp-content/uploads/2023/03/Quy-che-dao-tao-2021.pdf#page=18)

Chrome đã chạy cả hai luồng trên cùng ba tình huống K24, K26 và tra cứu chung. Phép thử ghi số thao tác và trang PDF mở được. Thời gian đọc hiểu và tỷ lệ bỏ dở của sinh viên chưa được đo. [Kết quả từng lượt](../cohort-walkthrough/comparison.md) · [Bộ mô phỏng](../../README.md#mô-phỏng-hai-cách-chọn-khóa)
