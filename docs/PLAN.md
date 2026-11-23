# Checklist Lab 03 · Trợ lý tra cứu quy chế học vụ

**Nhóm 14** · Deadline: **23:59 ngày 11/12/2026** · Hạn từng phase: [PROJECT.md §7.2](application/PROJECT.md#72-lịch-theo-planmd)

**Thái Quang Huy** phụ trách phương pháp SimCSE và so sánh thực nghiệm. **Nguyễn Văn Minh** phụ trách dữ liệu tiếng Việt, đánh giá truy hồi bằng SimCSE-VN và ứng dụng. Mỗi ô ghi người chủ trì và đầu ra cần kiểm tra. [Thiết kế kỹ thuật](application/PROJECT.md)

## Phase 1 – Nghiên cứu paper

*Mục 3.1–3.2 · Hai người đọc cùng paper, mỗi người viết một phần.*

- [ ] **Huy** — Viết phần bài toán, lý do chọn SimCSE, thông tin xuất bản và hạng CORE. Giải thích hai cách huấn luyện bằng ví dụ về dropout, cặp dương, mẫu âm và contrastive loss. *Bản nháp 23/11 (`introduction.tex`, `method.tex`):*
  - *Đã có:* bài toán, lý do chọn, thông tin xuất bản và hạng CORE, SimCSE khác cách làm trước thế nào.
  - *Đã có ví dụ tính tay cho cả hai cách huấn luyện* (§Worked Example). Câu lấy từ Figure 1 của paper; cosine là giá trị minh hoạ; số liệu kiểm bằng `tests/test_worked_example.py`.
  - *Còn thiếu:* ví dụ lexical gap lấy từ D1/D2, chờ dữ liệu của Minh.
- [ ] **Minh** — Lập bảng tóm tắt dữ liệu, cách chia tập, baseline, chỉ số Spearman và kết quả chính. Giải thích một hạn chế khi dùng kết quả STS tiếng Anh để dự đoán chất lượng tra cứu quy chế tiếng Việt.
- [ ] **Cả hai** — Đọc chéo hai phần. Huy giải thích cách tính một kết quả trong bảng, Minh diễn giải được cách tạo cặp huấn luyện.

## Phase 2 – Triển khai và tái hiện

*Mục 3.3 · Hai thí nghiệm độc lập, mỗi người tự chạy được từ dữ liệu đến kết quả.*

- [x] **Huy** — Chạy checkpoint supervised SimCSE gốc trên 7 tác vụ STS. Lưu môi trường, commit, checkpoint, cấu hình, lệnh chạy và bảng Spearman đối chiếu với số công bố. *Xong 23/11: TB 81,58, khớp README; chạy thêm unsup (76,25) và BERT thô (56,70), đều khớp paper. Xem [experiments/reproduction/](../experiments/reproduction/README.md).*
- [x] **Huy** — Giải thích luồng nạp dữ liệu, huấn luyện và suy luận. Tự cài InfoNCE, kiểm thử cả trường hợp có hard negative. *Xong 23/11:*
  - *Phần giải thích luồng code mới là bản nháp, ở §Execution Flow của `docs/report/sections/method.tex`.*
  - *InfoNCE (R4): 689 test pass, ở float64 lệch ≤ 1,4e-9 so với `cl_forward`. Xem [experiments/reproduction/](../experiments/reproduction/README.md).*
- [ ] **Minh** — Chuẩn bị ViRHE4QA (D1): xuất corpus, câu hỏi và mã đoạn đúng. Chia **câu hỏi** theo nhóm đoạn nguồn để cùng một đoạn không xuất hiện làm đáp án ở cả dev và test. Giữ chung corpus tra cứu.
- [ ] **Minh** — Mã hóa câu hỏi và các đoạn bằng SimCSE-VN, xếp hạng theo cosine và gộp về mã Điều/đoạn nguồn. Kiểm tra Hit@1, Hit@3, MRR@10 bằng ví dụ tính tay. Cố định cấu hình, lưu lệnh chạy, xếp hạng top 20 theo từng câu và bảng điểm D1-test. Các lần chỉnh cấu hình dùng D1-dev.

## Phase 3 – Xây dựng ứng dụng

*Mục 3.4 · Option 1. Minh xây ứng dụng trong lúc Huy chuẩn bị phép so sánh trên đầu ra Phase 2.*

- [ ] **Minh** — Chọn 1–3 văn bản quy chế. Minh họa hạn chế của Ctrl+F hoặc FAQ bằng một câu hỏi thực tế. Tách Điều/Khoản, kiểm tra nguyên văn, số hiệu và phiên bản với bản gốc.
- [ ] **Huy** — Ngay đầu phase, dùng xếp hạng SimCSE-VN từ Phase 2 để chuẩn bị bảng so sánh, kiểm thử khoảng tin cậy 95% cho chênh lệch giữa hai phương pháp và phép đo cảnh báo bằng ví dụ tính tay.
- [ ] **Minh** — Thêm BM25 và Hybrid vào phần truy hồi tiếng Việt. Giao cho Huy lệnh chạy ba phương pháp trên D1, cho phép đổi trọng số Hybrid và xuất cosine của Khoản tốt nhất trong Điều đứng đầu. Dựng giao diện Gradio song song với việc Huy chọn cấu hình.
- [ ] **Minh tổng hợp, Huy kiểm tra chéo** — Khi đã chọn văn bản, mỗi người soạn 40–50 câu trong phạm vi và 10 câu ngoài phạm vi. Chốt nhãn bộ test quy chế trường (D2) trước khi xem dự đoán trên D2.
- [ ] **Huy** — Chọn trọng số Hybrid và ngưỡng cảnh báo trên D1-dev, gửi cấu hình cố định cho Minh. So sánh ba phương pháp trên D1-test và D2 đã chốt nhãn. Báo riêng hiệu quả với câu ít trùng từ và tỷ lệ câu ngoài phạm vi bị gắn mức tin cậy cao.
- [ ] **Minh** — Áp dụng cấu hình cố định vào demo CPU: hiển thị top 3 Điều, Khoản trích dẫn, nguồn, phiên bản, cảnh báo và kết quả BM25 để đối chiếu. Lưu độ trễ p50/p95 của ba phương pháp.
- [ ] **Huy tổng hợp, Minh đối chiếu văn bản** — Phân loại 20–30 truy vấn sai trên D1 và D2. Chọn ví dụ cho thấy khi nào Hybrid hữu ích, khi nào xếp sai Điều và hướng cải thiện.

## Phase 4 – Hoàn thiện và nộp bài

*Mục 4 · Huy tổng hợp báo cáo trong lúc Minh hoàn thiện bản chạy và video.*

- [ ] **Huy** — Dùng bảng số liệu đã chốt để viết phương pháp, kết quả và thảo luận theo mẫu IEEE. Ghép phần ứng dụng của Minh rồi xuất PDF. *Khung LaTeX và lệnh build đã có ở [docs/report/](report/README.md) từ 23/11.*
- [ ] **Minh** — Bàn giao phần viết về ứng dụng, đối chứng và đóng góp của nhóm (có thể viết thẳng vào `docs/report/sections/application.tex` và `contributions.tex`). Hoàn thiện README với các lệnh cài đặt, dựng chỉ mục và chạy demo. Quay video tối đa 30 phút trên cấu hình đã đánh giá.
- [ ] **Huy kiểm tra, Minh đóng gói** — Huy chạy lại theo README từ bản clone sạch. Khi PDF, video và mã nguồn đã sẵn sàng, Minh kiểm tra link và tạo `[Group14].zip`; một đại diện nộp lên Moodle.
