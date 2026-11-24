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
- [ ] **Minh** — Chuẩn bị ViRHE4QA (D1): xuất corpus, câu hỏi và mã đoạn đúng. Chia **câu hỏi** theo nhóm đoạn nguồn để cùng một đoạn không xuất hiện làm đáp án ở cả dev và test. Giữ chung corpus tra cứu.
  - Không dùng cột `split` gốc: cách chia này bị rò rỉ, cùng một đoạn có câu hỏi ở cả train và test.
  - **Bắt buộc:** nhóm đoạn "Điều 6. Báo cáo tiến độ thực hiện KLTN" (chứa câu index 9542, 4 câu hỏi) phải vào D1-dev, vì câu 9542 đã dùng làm ví dụ trong Introduction.
- [ ] **Minh** — Mã hóa câu hỏi và các đoạn bằng SimCSE-VN, xếp hạng theo cosine và gộp về mã Điều/đoạn nguồn. Kiểm tra Hit@1, Hit@3, MRR@10 bằng ví dụ tính tay. Lưu lệnh chạy, top 20 theo từng câu và bảng điểm D1-dev. Bảng D1-test làm ở E1 sau khi chốt tiền xử lý, λ và θ.

## Phase 3 – Xây dựng ứng dụng

*Mục 3.4 · Option 1. Minh xây ứng dụng trong lúc Huy chuẩn bị phép so sánh trên đầu ra Phase 2.*

- [x] **Huy** — Duyệt bảng đối ứng Điều 2021 ↔ 2026 ([`data/d2/article_map.tsv`](../data/d2/article_map.tsv), gồm ba chủ đề gộp hai Điều cùng phiên bản T02/T09/T16) và quy tắc viết câu D2. *Xong 24/11 (D-18): đã đối chiếu nội dung, giữ T02/T09/T16; câu D2 viết kiểu gập sách; bản 2026 hiển thị trước.*
- [x] **Huy** — Rà toàn văn bản chép QĐ 3087 tìm lỗi OCR còn sót, sửa có ghi nhật ký và cập nhật sha256 trong `documents.yaml`. *Xong 24/11: lượt 2 sửa thêm 7 lỗi dấu (vd. "đơn vi" → "đơn vị"); sau đó đối chiếu các đoạn sai với PDF đã ký. Xem [cách tạo bản dùng để lập chỉ mục](../data/d2/README.md#file).*
- [ ] **Minh** — Dựng corpus của ứng dụng từ hai quy chế đào tạo HCMUS trong [`data/d2/`](../data/d2/README.md): QĐ 1175/2021 (24 Điều) và QĐ 3087/2026 (27 Điều). Chữ QĐ 1175 có trong `data/d2/`; bản chép QĐ 3087 nằm trên máy, chạy `python data/d2/prepare_2026.py` với bản nhóm đã chia sẻ.
  - Tách Điều/Khoản, kiểm tra số Điều (24 và 27) và kiểm tra mỗi chunk khớp đúng văn bản trong `data/raw/d2/`.
  - Gắn metadata từ `documents.yaml`: văn bản, số hiệu, ngày ban hành, phạm vi áp dụng.
  - Khi minh họa hạn chế của Ctrl+F bằng câu 9542 trong Introduction, chạy trên các đoạn quy chế của D1.
- [x] **Huy** — Kiểm thử khoảng tin cậy 95% cho chênh lệch giữa hai phương pháp và phép đo cảnh báo bằng ví dụ tính tay. *Xong 24/11, giao diện ở [PROJECT.md §5.4](application/PROJECT.md#54-interface--định-dạng-dữ-liệu).*
- [ ] **Huy** — Khi có xếp hạng SimCSE-VN từ Phase 2, chuẩn bị bảng so sánh trên D1-dev.
- [ ] **Minh** — Thêm BM25 và Hybrid vào phần truy hồi tiếng Việt. Giao cho Huy lệnh chạy ba phương pháp trên D1 và trên corpus HCMUS (D2), cho phép đổi trọng số Hybrid. Runs theo định dạng [PROJECT.md §5.4](application/PROJECT.md#54-interface--định-dạng-dữ-liệu), gồm Khoản tốt nhất và cosine của Khoản tốt nhất trong Điều đứng đầu. Dựng giao diện Gradio song song với việc Huy chọn cấu hình.
- [ ] **Cả hai viết, kiểm tra chéo câu của nhau; Minh tổng hợp file** — Viết bộ test D2 trên hai quy chế đào tạo HCMUS: mỗi người 40–50 câu trong phạm vi và 10 câu ngoài phạm vi. Bắt đầu ngay, không chờ Phase 2. Nếu kịp, Huy thu thêm khoảng 20 câu thật qua Google Form ẩn danh (`origin: form`). Chốt nhãn trước 02/12 và trước khi xem dự đoán trên D2. Quy tắc viết và gán nhãn (gồm cách ghi gold khi hai phiên bản cùng trả lời): [PROJECT.md §6.2](application/PROJECT.md#62-tiền-xử-lý-gán-nhãn-và-chia-dữ-liệu).
- [ ] **Huy** — Chọn trọng số Hybrid và ngưỡng cảnh báo trên D1-dev, gửi cấu hình cố định cho Minh. So sánh ba phương pháp trên D1-test và D2 đã chốt nhãn; với D2 báo cả mức theo Điều và theo chủ đề. Báo riêng hiệu quả với câu ít trùng từ và tỷ lệ câu ngoài phạm vi bị gắn mức tin cậy cao.
- [ ] **Minh** — Áp dụng cấu hình cố định vào demo CPU: hiển thị top 3 kết quả (các Điều cùng chủ đề gộp làm một, bản 2026 đứng trước), Khoản trích dẫn, tên văn bản, số hiệu, ngày ban hành, phạm vi áp dụng (ghi "bản chép từ bản scan" với QĐ 3087), cảnh báo và kết quả BM25 để đối chiếu. Lưu độ trễ p50/p95 của ba phương pháp.
- [ ] **Huy tổng hợp, Minh đối chiếu văn bản** — Phân loại 20–30 truy vấn sai trên D1-test và D2. Chọn ví dụ cho thấy khi nào Hybrid hữu ích, khi nào xếp sai Điều và hướng cải thiện.

## Phase 4 – Hoàn thiện và nộp bài

*Mục 4 · Huy tổng hợp báo cáo trong lúc Minh hoàn thiện bản chạy và video.*

- [ ] **Huy** — Dùng bảng số liệu đã chốt để viết phương pháp, kết quả và thảo luận theo mẫu IEEE. Ghép phần ứng dụng của Minh rồi xuất PDF. *Khung LaTeX và lệnh build đã có ở [docs/report/](report/README.md) từ 23/11.*
- [ ] **Minh** — Bàn giao phần viết về ứng dụng, đối chứng và đóng góp của nhóm (có thể viết thẳng vào `docs/report/sections/application.tex` và `contributions.tex`). Hoàn thiện README với các lệnh cài đặt, dựng chỉ mục và chạy demo. Quay video tối đa 30 phút trên cấu hình đã đánh giá.
- [ ] **Huy kiểm tra, Minh đóng gói** — Huy chạy lại theo README từ bản clone sạch. Khi PDF, video và mã nguồn đã sẵn sàng, Minh kiểm tra link và tạo `[Group14].zip`; một đại diện nộp lên Moodle.
