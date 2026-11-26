Viết cho: Nhóm 14 và người giữ bộ câu hỏi xác nhận.

# So sánh cách chọn Khoản và cảnh báo ngoài phạm vi

**Quyết định cần đưa ra.** Sinh viên có thấy đúng Khoản thường xuyên hơn và có ít gặp kết quả được trình bày như đáng tin khi quy chế thiếu câu trả lời không? Chỉ xét thay bản hiện tại khi **cả hai** cải thiện trên cùng một lần xác nhận giữ kín, đồng thời sinh viên vẫn tra được các câu có căn cứ. Đây là thiết kế trước thí nghiệm ngày 26/11/2026. Đã có [16 câu phát triển kèm nhãn tham chiếu và trang PDF](../../data/development/clause-scope-pilot.jsonl).

## Bản đối chứng và ba bản thử

Ngày 26/11/2026 đã chạy bốn bản trên bộ phát triển mở. [Kết quả từng câu và giới hạn của lượt thử](results/clause-scope-pilot/comparison.md)

Bản đối chứng A là Hybrid đang dùng. Cố định trọng số BM25 **0,6**, ngưỡng cosine **0,6201629042625427**, checkpoint ở revision `608779b86741a8acd8c8d38132974ff04086b138`, tokenizer, cách chia đoạn và tập 273 đoạn thuộc 51 Điều, 26 chủ đề. Cả bốn bản nhận cùng câu và cùng các điểm BM25, cosine thô. Giữ thứ tự Điều, cách gộp chủ đề, thứ tự phiên bản và bộ hiển thị của A. Đối chiếu checksum cấu hình, corpus, bảng đối ứng với manifest. [Cấu hình D1-dev](../external_dataset/results/D1-dev-tuning/summary.json) · [Manifest đã công bố](results/D2/summary.json) · [Cách A chọn đoạn và xử lý đồng điểm](../../docs/application/PROJECT.md#52-vai-trò-từng-thành-phần-proposed)

| Bản | Chọn đoạn trong mỗi Điều | Khi nào kết quả được coi là tin cậy? |
| --- | --- | --- |
| A · Hiện tại | Quy tắc Hybrid đã công bố | Cosine của đoạn đã chọn trong Điều đứng đầu ≥ ngưỡng |
| K · Đổi cách chọn Khoản | Xếp lại các đoạn bên trong từng Điều theo quy tắc dưới bảng | Cùng phép so cosine trên đoạn K chọn |
| G · Thêm điều kiện cảnh báo | Như A | Đạt ngưỡng và hai phương pháp đồng ý về chủ đề đứng đầu |
| K+G · Ứng viên thay thế | Như K | Đạt ngưỡng trên đoạn K chọn và qua điều kiện của G |

- **K.** Trong mỗi Điều có đoạn mang mã Khoản, chỉ xét các đoạn có mã Khoản. Với từng đoạn, tính hai hạng nội bộ theo điểm BM25 và cosine giảm dần. Hạng bằng 1 cộng số đoạn có điểm cao hơn, nên các đoạn bằng điểm nhận cùng hạng. Chọn đoạn có giá trị `0.6 / rank_bm25 + 0.4 / rank_dense` lớn nhất. Khi hòa, dùng điểm đoạn Hybrid của A, sau đó lấy `chunk_id` nhỏ nhất. Điều chỉ có phần mở đầu dùng lựa chọn của A. Giả thuyết là một đoạn được cả hai cách tìm ủng hộ có thể trích đúng Khoản hơn.
- **G.** Lấy Điều đầu của BM25, SimCSE-VN và Hybrid theo quy tắc đồng điểm của A. Điều kiện bổ sung đạt khi điểm BM25 lớn nhất dương và cả ba Điều thuộc cùng một chủ đề. Nếu thiếu điều kiện, hiển thị cảnh báo ở tab tra cứu và thu gọn kết quả như khi cosine thấp. Một câu ngoài phạm vi vẫn có thể qua cả hai điều kiện, nên cần đo lỗi này trực tiếp.
- **So sánh chính** là K+G với A. Hai bản K và G cho biết phần nào gây thay đổi, kể cả khi K đổi cosine vì nó chọn đoạn khác. G giữ nguyên đoạn của bản mà nó bổ sung. Chỉ có một ứng viên được xét thay ở lần mở nhãn này.

## Dữ liệu phát triển và nhãn giữ kín

**Bộ thử phiếu.** Có 8 câu có căn cứ, 6 câu ngoài phạm vi nhưng dùng từ học vụ và 2 câu ngoài lĩnh vực. Ba câu gần phạm vi được diễn đạt lại từ những thắc mắc đã công bố trước thí nghiệm. Mỗi câu có đường dẫn và vị trí nguồn. Mười ba câu còn lại do Codex soạn. [Giải đáp của Khoa Toán – Tin học](https://www.math.hcmus.edu.vn/tin-tuc/tin-giao-vu/1278) · [Câu hỏi về ngành học trên Q&A FIT](https://courses.fit.hcmus.edu.vn/q2a/?qa=2440&qa_1=kh%C3%A1c-nhau-gi%E1%BB%AFa-chuy%C3%AAn-ng%C3%A0nh-t%E1%BB%95ng-th%E1%BB%83-cntt-c%C3%A1c-chuy%C3%AAn-ng%C3%A0nh-kh%C3%A1c)

Đã so với 1.143 câu hỏi cũ phân biệt được sau chuẩn hóa từ D1, D2, E4, hai thư viện ảnh, bộ hồi quy và câu mẫu giao diện. Một tình huống hỏi địa điểm trên thời khóa biểu bị loại vì trùng ý với D2. Cả 16 câu và các biến thể cùng ý chỉ dùng để phát triển.

Codex đã điền bộ nhãn tham chiếu theo yêu cầu của Huy, đối chiếu cả chín mã Khoản có đáp án và đọc các trang liên quan trong hai PDF gốc. Hai phiếu bàn giao cho Huy và Minh dùng chung lượt gán nhãn này. Mỗi câu ghi căn cứ đủ trả lời hoặc dữ kiện còn thiếu. Trường `checked_passages` lưu mã Khoản, trang PDF tính từ 1 và điểm khi cần. Với câu ngoài phạm vi, đây là phần văn bản đã rà, còn `gold_clause_ids` rỗng. Ba câu lấy ý từ nguồn công khai có thêm `external_note` ghi thông tin riêng của Khoa. [Câu hỏi, nhãn và căn cứ](../../data/development/clause-scope-pilot.jsonl)

Ví dụ, ở `pilot-03`, cả hai đoạn đều có thể hiện “Điều 8, Khoản 3” của bản 2021. Chỉ lần xuất hiện thứ hai nói về công khai ý kiến người học. Ở `pilot-02`, dù tìm đúng Điều có chữ “phúc tra”, ứng dụng vẫn phải cảnh báo vì sinh viên hỏi **mã bưu chính để gửi đơn**. Ở `pilot-15`, hai quy chế đều cho căn cứ về điểm chuyên cần của môn thực hành, nên chấp nhận hai mã Khoản khác nhau.

| Tập xác nhận cần thu mới | Số tình huống độc lập | Cách lấy mẫu |
| --- | ---: | --- |
| Có đáp án nằm trong một Khoản | 140 | Mỗi lần rút, chọn đều giữa ba nhóm cần bản 2021, cần bản 2026 và chấp nhận cả hai. Khung lấy mẫu bao phủ ít nhất 15 chủ đề, gồm cả Khoản gần nhau và đoạn dài |
| Ngoài phạm vi, gần chủ đề | 100 | Mỗi lần rút, chọn đều giữa thủ tục được dẫn sang văn bản khác, thông tin cá nhân hoặc theo thời điểm, quy định của đơn vị hoặc bậc học khác, và chi tiết nghiệp vụ cụ thể còn thiếu. Gán nhóm theo dữ kiện chính sinh viên cần |
| Ngoài lĩnh vực | 30 | Rút tình huống từ khung có ít nhất 5 lĩnh vực khác nhau, gồm cả những câu tình cờ có từ giống quy chế |

**Vì sao lấy cỡ mẫu này.** Giả sử trên câu có đáp án, ứng viên sửa đúng cho 15% số câu và làm sai thêm 5%. Với 140 tình huống, xác suất vượt cả mức tăng quan sát 5 điểm và phép kiểm ghép cặp ở dưới là 82,0%. Nếu ở nhóm gần phạm vi, hai tỷ lệ là 12% và 2%, 100 tình huống cho xác suất 83,1%. Đây là hai kịch bản thiết kế cho mức cải thiện thực 10 điểm, chưa tính các điều kiện bảo vệ còn lại. Tính bằng cách cộng xác suất của các cặp thắng/thua đạt tiêu chí. Số cặp bất đồng có phân phối nhị thức với xác suất bằng tổng hai tỷ lệ, còn xác suất thắng trong cặp bất đồng bằng tỷ lệ sửa đúng chia cho tổng đó.

1. Thu câu nguyên văn từ một đợt mới. Người đặt câu chưa xem câu mẫu, kết quả tìm kiếm hay câu bị sai. Người giữ bộ câu hỏi kiểm riêng D1, D2, E4, các ví dụ ứng dụng, lượt thử giao diện và bộ phát triển mở. So câu đã chuẩn hóa Unicode, chữ hoa, dấu câu, tiếp đến rà các câu gần nhất và ý định thực tế. Loại biến thể của cả tình huống đã dùng, kể cả đổi tên, con số, chính tả hoặc khóa tuyển sinh mà vẫn hỏi cùng một căn cứ. Ghi lý do loại. Có thể dùng chung kho quy chế để tra cứu.
2. Gán `family_id` theo điều sinh viên cần biết và phần văn bản tối thiểu đủ trả lời. Các cách hỏi lại và cặp câu chỉ đổi một điều kiện ở cùng tình huống ở chung nhóm. Giữ mọi thành viên của một nhóm trong cùng một tập. Tách người đặt câu phát triển với người đặt câu xác nhận. Mỗi tình huống và mỗi người gửi chỉ đóng góp một câu cho phép kiểm chính, các câu còn lại dùng để mô tả. Khi đã chốt khung đủ mẫu, bốc nhóm con theo bảng rồi lấy ngẫu nhiên một tình huống còn hợp lệ trong nhóm, lưu seed 42, danh sách đầu vào và thứ tự rút. Báo số thực rút mỗi nhóm con.
3. Hai người gán nhãn độc lập từ văn bản nguồn, chưa xem output máy hay nhãn của nhau. Với câu có đáp án, lưu mọi `article_id`, `clause_id` hợp lệ theo phiên bản, điểm hoặc đoạn đủ trả lời, khóa áp dụng và vị trí trong nguồn. Với câu ngoài phạm vi, ghi chính xác dữ kiện bị thiếu và những Điều gần nhất đã đối chiếu ở cả hai bản. Một Khoản dẫn sang văn bản khác chỉ đủ nếu người hỏi cần biết **tìm ở đâu**. Nếu họ hỏi **giá trị cụ thể**, phải có chính giá trị đó. Hai người đối chiếu bất đồng, ghi cách giải quyết và tỷ lệ nhất trí trước thảo luận. Dùng PDF gốc để xử lý lỗi chép, số Khoản lặp và văn bản sửa đổi. [Nguồn văn bản và sửa đổi](../../data/d2/documents.yaml) · [Quy ước mã Khoản](../../data/d2/README.md#mã-điều-và-khoản)
4. Câu mơ hồ do thiếu khóa, đòi hỏi nhiều Khoản cùng lúc hoặc có bất đồng chưa xử lý đi vào nhóm riêng có ghi lý do. Chốt đủ số tình huống trong từng hàng trước khi thấy dự đoán. Người giữ dữ liệu lưu riêng câu hỏi, nhãn, mã người viết ẩn danh, `family_id`, quyết định loại và SHA-256. Người viết bản thử chỉ thấy bộ phát triển mở. Cố định mã bốn bản, phép chấm và điều kiện dưới đây trước khi người giữ dữ liệu chạy xác nhận một lần. Lưu commit, phần thay đổi chưa commit ảnh hưởng tới A và checksum mã thực chạy của từng bản, kể cả bộ hiển thị. Chỉ người rà trùng cần đối chiếu văn bản câu hỏi test. Dùng tên tập riêng như `hcmus-development/confirm` và lưu kết quả riêng. [Kết quả lịch sử D2-test](results/D2/d2-test.md)

## Chấm từng câu

Ghép bốn kết quả theo `qid`. Lưu thứ tự Điều, `chunk_id`, `clause_id`, cosine của đoạn trong Điều đầu **trước khi gộp**, kết quả kiểm của G, trạng thái cảnh báo thực tế và phần văn bản người dùng đọc được mặc định ở chủ đề đầu tiên. Chụp hoặc lưu HTML đã hiển thị cùng phiên bản, Điều và Khoản. Hai người kiểm phần căn cứ nhìn thấy theo thứ tự ngẫu nhiên, ẩn tên bản và điểm, rồi giải quyết bất đồng. Cho phép cuộn khi đọc. Nếu phải mở bản đối chiếu hoặc bấm đọc tiếp mới thấy căn cứ thì ghi riêng.

| Chỉ số | Mẫu số | Một câu được tính khi… |
| --- | --- | --- |
| Khoản đúng hạng 1 (Clause@1) | 140 câu có đáp án | Mã Khoản của đoạn trong Điều hạng 1 thuộc tập nhãn. Đo cả câu bị cảnh báo. Đoạn chỉ có tiêu đề tính sai |
| Tự tin sai phạm vi | Từng nhóm 100 gần và 30 xa | Tab tra cứu trả kết quả như tin cậy dù thiếu căn cứ. Đọc quyết định cuối của từng bản, gồm cả điều kiện G khi có |
| Độ bao phủ trên câu có đáp án | 140 câu có đáp án | Tab tra cứu chấp nhận câu, giống trải nghiệm mặc định khi cosine đủ cao ở A |
| Có căn cứ đúng ngay trên giao diện | 140 câu có đáp án | Câu được chấp nhận và đoạn chính đang mở cung cấp đủ nội dung đúng Khoản, đúng phiên bản để trả lời. Một tiêu đề đúng hoặc một liên kết đến văn bản chưa đủ |

Báo riêng số câu sai Điều, tỷ lệ sai Khoản **trên các câu có Điều hạng 1 đúng**, số câu đúng Khoản nhưng căn cứ cần đọc bị ẩn, và số câu sai phiên bản dù đúng chủ đề. Ghi cả Hit@1 theo Điều và chủ đề, số lần A đúng nhưng ứng viên sai và chiều ngược lại. Cơ cấu 140/100/30 là cơ cấu đã chủ động lấy mẫu. Tần suất lỗi trong lưu lượng thực tế cần mẫu người dùng riêng.

## Điều kiện thay bản hiện tại

Các biên dưới đây là **mức chấp nhận đề xuất trước khi đo**. Năm điểm phần trăm tương ứng ít nhất một sinh viên được lợi trên mỗi 20 câu thuộc nhóm. Tính bằng số gốc trước khi làm tròn. K+G phải đạt **tất cả** các hàng trên bộ xác nhận.

| Điều kiện | Mức phải đạt của K+G so với A |
| --- | --- |
| Chọn Khoản | Clause@1 tăng ít nhất 5 điểm phần trăm **và** kiểm định McNemar chính xác một phía có p < 0,05 |
| Ngoài phạm vi gần chủ đề | Tỷ lệ tự tin sai giảm ít nhất 5 điểm phần trăm **và** cùng kiểm định có p < 0,05. Cận trên một phía 95% của tỷ lệ sai còn lại của K+G phải ≤ 5% |
| Ngoài lĩnh vực | 0 lần chấp nhận sai trên 30 câu. Báo riêng số mẫu và cận trên của tỷ lệ lỗi |
| Câu có đáp án | Với cả độ bao phủ và tỷ lệ có căn cứ đúng ngay trên giao diện, cận dưới một phía 95% của chênh lệch K+G trừ A phải ≥ −5 điểm phần trăm. Riêng tỷ lệ có căn cứ đúng ngay trên giao diện còn phải có chênh lệch quan sát ≥ 0 |
| Tính toàn vẹn | Bốn bản có đủ cùng `qid` và cùng thứ tự 51 Điều cho từng câu. Mỗi trích dẫn dẫn về đúng nguồn. Cảnh báo và trạng thái mở trên UI phải khớp quyết định đã lưu. Lỗi trả kết quả của ứng viên được ghi như một thất bại khi xét thay |

**Cách tính.** Với mỗi chỉ số, đặt “thành công” là chọn đúng Khoản, cảnh báo đúng câu ngoài phạm vi, hoặc đáp ứng điều kiện của chỉ số độ bao phủ tương ứng. Gọi W là số cặp chỉ K+G thành công, L là số cặp chỉ A thành công, N là toàn bộ tình huống của nhóm. Mức cải thiện quan sát là `(W − L) / N`. McNemar chính xác một phía dùng xác suất nhận ít nhất W lần thắng trong W+L phép thử nhị thức công bằng. Khi W+L bằng 0, lấy p bằng 1. Tất cả tiêu chí cùng bắt buộc ở lần so sánh chính. Hai bản chẩn đoán và các nhóm nhỏ không được dùng để chọn lại ứng viên sau khi xem kết quả. [Phép thử nhị thức chính xác](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html)

Với tỷ lệ lỗi còn lại, dùng cận trên Clopper–Pearson một phía 95%. Với chênh lệch độ bao phủ, lấy cận dưới một phía 97,5% của W/N trừ cận trên một phía 97,5% của L/N. Hai sai số đuôi cộng lại tối đa 5%, nên đây là cận dưới 95% bảo thủ trên các cặp tình huống độc lập. Khi W bằng 0, cận dưới của W/N bằng 0. [Cách tính cận nhị thức chính xác](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats._result_classes.BinomTestResult.proportion_ci.html)

**Ví dụ tính bằng số giả định.** Trên 140 câu có đáp án, sửa được 14 nhưng làm sai thêm 5 cho mức tăng 6,43 điểm và p = 0,0318. Trên 100 câu gần phạm vi, 9 câu được cảnh báo đúng thêm và 1 câu mất cảnh báo cho mức giảm lỗi 8 điểm và p = 0,0107. Nếu ứng viên còn sai 2/100 thì cận trên là 6,16%, phải giữ A. Với 1/100, cận là 4,66% và hàng này đạt. Ngay cả 0/30 lỗi ở nhóm xa vẫn có cận trên 9,50%, nên 30 câu dễ không thể thay cho 100 câu gần phạm vi.

**Ghi quyết định.** Đủ dữ liệu, qua mọi điều kiện và kiểm lại được từ từng cặp mới ghi “đủ căn cứ thay”. Có hồi quy vượt biên thì giữ A và ghi rõ lỗi. Thiếu tình huống độc lập, phát hiện rò rỉ, thiếu cặp hoặc khoảng tin cậy chưa đủ hẹp thì ghi “chưa đủ bằng chứng”, tiếp tục dùng A. Chỉ chạy lại cùng mã khi xác định lỗi hạ tầng và lưu cả lần lỗi. Khi đã xem kết quả rồi sửa ứng viên, lần quyết định tiếp theo cần một bộ xác nhận mới. Lưu manifest, phiếu chấm, bảng cặp thắng/thua và kết luận ở thư mục thí nghiệm riêng. Các kết quả E0–E5 tiếp tục gắn với cấu hình đã công bố.
