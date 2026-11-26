# Checklist Lab 03 · Trợ lý tra cứu quy chế học vụ

**Nhóm 14** · Deadline: **23:59 ngày 11/12/2026** · Hạn từng phase: [PROJECT.md §7.2](application/PROJECT.md#72-lịch-theo-planmd)

**Thái Quang Huy** phụ trách phương pháp SimCSE và so sánh thực nghiệm. **Nguyễn Văn Minh** phụ trách dữ liệu tiếng Việt, đánh giá truy hồi bằng SimCSE-VN và ứng dụng. Mỗi ô ghi người chủ trì và đầu ra cần kiểm tra. [Thiết kế kỹ thuật](application/PROJECT.md)

## Phase 1 – Nghiên cứu paper

*Mục 3.1–3.2 · Hai người đọc cùng paper, mỗi người viết một phần.*

- [x] **Huy** — Viết phần bài toán, lý do chọn SimCSE, thông tin xuất bản và hạng CORE. Giải thích hai cách huấn luyện bằng ví dụ về dropout, cặp dương, mẫu âm và contrastive loss. *Bản nháp xong 23/11 (`introduction.tex`, `method.tex`), đã đọc chéo.*
  - *Bài toán, kèm ví dụ lexical gap thật từ D1:* câu index 9542, hỏi "bị dừng giữa chừng" trong khi Điều 6 dùng "đình chỉ".
  - *Lý do chọn SimCSE, thông tin xuất bản, hạng CORE, SimCSE khác cách làm trước thế nào.*
  - *Ví dụ tính tay cho cả hai cách huấn luyện* (§Worked Example). Câu lấy từ Figure 1 của paper; cosine là giá trị minh hoạ; số liệu kiểm bằng `tests/test_worked_example.py`.
- [x] **Minh** — Lập bảng tóm tắt dữ liệu, cách chia tập, baseline, chỉ số Spearman và kết quả chính. Giải thích một hạn chế khi dùng kết quả STS tiếng Anh để dự đoán chất lượng tra cứu quy chế tiếng Việt. [Experimental Setup](report/sections/experimental-setup.tex) · [Results and Discussion](report/sections/results.tex)
- [x] **Huy** — Related Work (mục 3.2.2), biểu diễn câu trước SimCSE và học tương phản. Bản nháp ngày 24/11 đối chiếu các phương pháp và kết quả STS với bài gốc. [Mục II-A](report/sections/related-work.tex)
- [x] **Minh** — Related Work (mục 3.2.2), BM25 và truy hồi bằng vector cho tiếng Việt. [Mục II-B](report/sections/related-work.tex)
- [x] **Cả hai** — Đọc chéo hai phần. Huy giải thích cách tính một kết quả trong bảng, Minh diễn giải được cách tạo cặp huấn luyện. Minh xác nhận đã trao đổi xong.

## Phase 2 – Triển khai và tái hiện

*Mục 3.3 · Hai thí nghiệm độc lập, mỗi người tự chạy được từ dữ liệu đến kết quả.*

- [x] **Huy** — Chạy checkpoint supervised SimCSE gốc trên 7 tác vụ STS. Lưu môi trường, commit, checkpoint, cấu hình, lệnh chạy và bảng Spearman đối chiếu với số công bố. *Xong 23/11: TB 81,58, khớp README; chạy thêm unsup (76,25) và BERT thô (56,70), đều khớp paper. Xem [experiments/reproduction/](../experiments/reproduction/README.md).*
- [x] **Huy** — Giải thích luồng nạp dữ liệu, huấn luyện và suy luận. Tự cài InfoNCE, kiểm thử cả trường hợp có hard negative. *Xong 23/11:*
  - *Phần giải thích luồng code mới là bản nháp, ở §Execution Flow của `docs/report/sections/method.tex`.*
  - *InfoNCE (R4): 689 test pass, ở float64 lệch ≤ 1,4e-9 so với `cl_forward`. Xem [experiments/reproduction/](../experiments/reproduction/README.md).*
- [x] **Minh** — Chuẩn bị ViRHE4QA (D1): xuất corpus, câu hỏi và mã đoạn đúng. Chia **câu hỏi** theo nhóm đoạn nguồn để cùng một đoạn không xuất hiện làm đáp án ở cả dev và test. Giữ chung corpus tra cứu. *Đã xác minh 224 câu dev, 759 câu test và 297 context sau khi bỏ 17 dòng trùng.* [Thống kê split](../experiments/external_dataset/results/D1-dev/metrics.json)
  - Không dùng cột `split` gốc: cách chia này bị rò rỉ, cùng một đoạn có câu hỏi ở cả train và test.
  - **Bắt buộc:** nhóm đoạn "Điều 6. Báo cáo tiến độ thực hiện KLTN" (chứa câu index 9542, 4 câu hỏi) phải vào D1-dev, vì câu 9542 đã dùng làm ví dụ trong Introduction.
- [x] **Minh** — Mã hóa câu hỏi và các đoạn bằng SimCSE-VN, xếp hạng theo cosine và gộp về mã Điều/đoạn nguồn. Kiểm tra Hit@1, Hit@3, MRR@10 bằng ví dụ tính tay. Đã lưu lệnh chạy, top 20 theo từng câu và bảng điểm D1-dev. [Hướng dẫn và kết quả](../experiments/external_dataset/README.md)

## Phase 3 – Xây dựng ứng dụng

*Mục 3.4 · Option 1. Minh xây ứng dụng trong lúc Huy chuẩn bị phép so sánh trên đầu ra Phase 2.*

- [x] **Huy** — Duyệt bảng đối ứng Điều 2021 ↔ 2026 ([`data/d2/article_map.tsv`](../data/d2/article_map.tsv), gồm ba chủ đề gộp hai Điều cùng phiên bản T02/T09/T16) và quy tắc viết câu D2. *Xong 24/11 (D-18): đã đối chiếu nội dung, giữ T02/T09/T16; câu D2 viết kiểu gập sách; bản 2026 hiển thị trước.*
- [x] **Huy** — Rà toàn văn bản chép QĐ 3087 tìm lỗi OCR còn sót, sửa có ghi nhật ký và cập nhật sha256 trong `documents.yaml`. *Xong 24/11: lượt 2 sửa thêm 7 lỗi dấu (vd. "đơn vi" → "đơn vị"); sau đó đối chiếu các đoạn sai với PDF đã ký. Xem [cách tạo bản dùng để lập chỉ mục](../data/d2/README.md#file).*
- [x] **Minh** — Dựng corpus của ứng dụng từ hai quy chế đào tạo HCMUS trong [`data/d2/`](../data/d2/README.md): QĐ 1175/2021 (24 Điều) và QĐ 3087/2026 (27 Điều). Chữ QĐ 1175 có trong `data/d2/`; bản chép QĐ 3087 nằm trên máy, chạy `python data/d2/prepare_2026.py` với bản nhóm đã chia sẻ.
  - Tách Điều/Khoản, kiểm tra số Điều (24 và 27) và kiểm tra mỗi chunk khớp đúng văn bản trong `data/raw/d2/`.
  - Gắn metadata từ `documents.yaml`: văn bản, số hiệu, ngày ban hành, phạm vi áp dụng.
  - Đã xuất và kiểm file corpus hai phiên bản trên máy Huy ngày 25/11. [Cách tạo lại corpus](../data/d2/README.md#file). Việc chạy demo được theo dõi ở mục riêng phía dưới.
  - Khi minh họa hạn chế của Ctrl+F bằng câu 9542 trong Introduction, chạy trên các đoạn quy chế của D1.
- [x] **Huy** — Kiểm thử khoảng tin cậy 95% cho chênh lệch giữa hai phương pháp và phép đo cảnh báo bằng ví dụ tính tay. *Xong 24/11, giao diện ở [PROJECT.md §5.4](application/PROJECT.md#54-interface--định-dạng-dữ-liệu).*
- [x] **Huy** — Kiểm chứng phép xếp hạng BM25 trên D1-dev (E0). Tính lại điểm từng chunk cho câu 9542 và đối chiếu thứ tự của 20 đoạn đầu với gói bàn giao. [Ghi chú E0](../experiments/external_dataset/results/E0/d1-dev.md)
- [x] **Huy** — Chuẩn bị bảng so sánh trên D1-dev từ điểm của BM25, SimCSE-VN và Hybrid. [Bảng so sánh](../experiments/external_dataset/results/D1-dev-tuning/handoff.md#kết-quả-trên-224-câu-d1-dev)
- [x] **Minh** — Thêm BM25 và Hybrid vào phần truy hồi tiếng Việt. Giao cho Huy lệnh chạy ba phương pháp trên D1 và trên corpus HCMUS (D2), cho phép đổi trọng số Hybrid. Runs theo định dạng [PROJECT.md §5.4](application/PROJECT.md#54-interface--định-dạng-dữ-liệu), gồm Khoản tốt nhất và cosine của Khoản tốt nhất trong Điều đứng đầu. Dựng giao diện Gradio song song với việc Huy chọn cấu hình.
  - Đã kiểm chứng gói D1-dev trên 224 câu. Cả ba bảng xếp hạng khớp SHA-256, mã câu, thứ tự xếp hạng và chỉ số tính lại. Đã kiểm demo trên 51 Điều với checkpoint thật. [Lệnh bàn giao](../experiments/external_dataset/README.md#bàn-giao-cho-huy)
- [ ] **Cả hai viết, kiểm tra chéo câu của nhau; Minh tổng hợp file** — Viết bộ test D2 trên hai quy chế đào tạo HCMUS: mỗi người 40–50 câu trong phạm vi và 10 câu ngoài phạm vi. Bắt đầu ngay, không chờ Phase 2. Nếu kịp, Huy thu thêm khoảng 20 câu thật qua Google Form ẩn danh (`origin: form`). Chốt nhãn trước 02/12 và trước khi xem dự đoán trên D2. Quy tắc viết và gán nhãn (gồm cách ghi gold khi hai phiên bản cùng trả lời): [PROJECT.md §6.2](application/PROJECT.md#62-tiền-xử-lý-gán-nhãn-và-chia-dữ-liệu).
  - Huy xác nhận đã tự soạn phần của mình, gồm 45 câu trong phạm vi và 10 câu ngoài phạm vi. Bản câu hỏi gửi Minh gán nhãn độc lập đã được kiểm nguyên văn.
  - Bản nháp của Minh có 41 câu trong phạm vi và 10 câu ngoài phạm vi do trợ lý soạn. Phía Minh đã chuẩn bị nhãn cho cả 106 câu theo hai quy chế. Hai thành viên còn đối chiếu lượt nhãn độc lập, tính tỷ lệ đồng ý và chốt bất đồng.
- [x] **Huy** — Chọn trọng số Hybrid và ngưỡng cảnh báo trên D1-dev. [Cấu hình đã chốt](../experiments/external_dataset/results/D1-dev-tuning/handoff.md)
- [x] **Huy** — Chạy BM25, SimCSE-VN và Hybrid trên D1-test với cấu hình chốt từ dev. Xuất bảng truy hồi, khoảng tin cậy Hybrid so với BM25 và số liệu cảnh báo ở ngưỡng cố định. [Kết quả D1-test](../experiments/external_dataset/results/E1/d1-test.md)
- [x] **Huy** — So sánh ba phương pháp theo mức trùng từ trên D1-test. Báo số câu, chỉ số và khoảng tin cậy ghép cặp trong từng nhóm. [Kết quả E2 trên D1-test](../experiments/application/results/E2/d1-test.md)
- [x] **Huy** — Vẽ đường cong risk–coverage của Hybrid trên D1-test và đánh dấu ngưỡng cảnh báo đã chốt. [Biểu đồ E3 trên D1-test](../experiments/external_dataset/results/E3/d1-test-risk-coverage.png)
- [x] **Huy** — Chuẩn bị mã Khoản ổn định và bộ chấm ba bảng xếp hạng D2 cho E2 và E3. Kiểm tra bằng nhãn và xếp hạng giả. [Cách chấm D2](../experiments/application/README.md#chấm-d2-test)
- [ ] **Huy** — Gửi cấu hình cho Minh. So sánh ba phương pháp trên D2 đã chốt nhãn, báo cả mức theo Điều và theo chủ đề. Báo kết quả theo mức trùng từ, đường cong risk–coverage và tỷ lệ câu ngoài phạm vi bị gắn mức tin cậy cao trên D2.
- [x] **Minh** — Áp dụng cấu hình cố định vào demo CPU: hiển thị top 3 kết quả (các Điều cùng chủ đề gộp làm một, bản 2026 đứng trước), Khoản trích dẫn, tên văn bản, số hiệu, ngày ban hành, phạm vi áp dụng (ghi "bản chép từ bản scan" với QĐ 3087), cảnh báo và kết quả BM25 để đối chiếu. Đã lưu [kết quả E4 và mẫu đo](../experiments/application/results/E4/cpu-latency.md).
- [x] **Huy** — Đối chiếu 20 câu Hybrid trượt Hit@1 trên D1-test và chọn ví dụ cho E5. [Bảng phân loại và ví dụ](../experiments/application/results/E5/d1-test.md)
- [ ] **Huy tổng hợp, Minh đối chiếu văn bản** — Kiểm chéo các ví dụ E5, bổ sung trường hợp D2 vào bộ 20–30 truy vấn và nêu hướng cải thiện dựa trên các lỗi đã đối chiếu.
  - Minh đã kiểm chéo văn bản 20/20 câu lỗi và 2 ví dụ xếp đúng trên D1-test. Còn đối chiếu ba run gốc để xác minh thứ hạng, rồi bổ sung ví dụ D2 sau khi chốt nhãn. [Kết quả kiểm chéo](../experiments/application/results/E5/d1-test.md)

## Phase 4 – Hoàn thiện và nộp bài

*Mục 4 · Huy tổng hợp báo cáo trong lúc Minh hoàn thiện bản chạy và video.*

- [ ] **Huy** — Dùng bảng số liệu đã chốt để viết phương pháp, kết quả và thảo luận theo mẫu IEEE. Ghép phần ứng dụng của Minh rồi xuất PDF. *Khung LaTeX và lệnh build đã có ở [docs/report/](report/README.md) từ 23/11.*
- [ ] **Minh** — Bàn giao phần viết về ứng dụng, đối chứng và đóng góp của nhóm (có thể viết thẳng vào `docs/report/sections/application.tex` và `contributions.tex`). Hoàn thiện README với các lệnh cài đặt, dựng chỉ mục và chạy demo. Quay video tối đa 30 phút trên cấu hình đã đánh giá.
- [ ] **Huy kiểm tra, Minh đóng gói** — Huy chạy lại theo README từ bản clone sạch. Khi PDF, video và mã nguồn đã sẵn sàng, Minh kiểm tra link và tạo `[Group14].zip`; một đại diện nộp lên Moodle.
