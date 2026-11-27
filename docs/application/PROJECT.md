# PROJECT – Trợ lý tra cứu quy chế học vụ tiếng Việt (SimCSE)

> Tài liệu trung tâm (Single Source of Truth) về đặc tả và trạng thái dự án. Tài liệu trong repo:
> - `README.md` ở thư mục gốc: bản đồ repo.
> - `docs/PLAN.md`: checklist và **phân công**. Đây là nguồn duy nhất về ai làm gì.
> - `docs/application/README.md`: tổng quan ứng dụng.
> - File này: đặc tả, quyết định, trạng thái.
> Mỗi thông tin chi tiết chỉ đặt ở **một** mục; các mục khác dùng link tới đó.

**Quy ước nhãn**

| Nhãn | Ý nghĩa |
|---|---|
| **[Confirmed]** | Đã kiểm chứng từ nguồn gốc: đề Lab 03, paper, code tại commit cố định, file dữ liệu, model card |
| **[Proposed]** | Đề xuất hoặc quyết định thiết kế của nhóm, chưa có bằng chứng thực nghiệm |
| **[Unverified]** | Chưa kiểm chứng được; cần nhóm kiểm tra trước khi dựa vào |
| `[ ]` / `[x]` | Chưa làm / đã xong, kèm bằng chứng (file, commit, kết quả) |

**Thứ tự ưu tiên nguồn:** Đề Lab 03 > Paper + code tại commit `235f89e` > Research đã chọn ý tưởng.
Kết quả lấy từ tài liệu bên ngoài **không phải** kết quả của nhóm. Mọi số liệu của nhóm phải trỏ tới file trong `results/`.

**Mục lục**

1. [Current Status](#1-current-status)
2. [Project Definition & Scope](#2-project-definition--scope)
3. [Lab 03 Requirements](#3-lab-03-requirements)
4. [SimCSE Research Foundation](#4-simcse-research-foundation)
5. [Application Architecture & Implementation](#5-application-architecture--implementation)
6. [Datasets & Experimental Evaluation](#6-datasets--experimental-evaluation)
7. [Development Plan & Team Workflow](#7-development-plan--team-workflow)
8. [Risks, Decisions & Definition of Done](#8-risks-decisions--definition-of-done)

---

## 1. Current Status

**Nhóm 14** · **Deadline: 23:59 ngày 11/12/2026** · Cập nhật lần cuối: 2026-11-27 (Codex)

**Repo GitHub:** <https://github.com/AIVIETNAM-AIO-Heart208/UniSearch-SimCSE>. Minh tạo ngày 23/11.

**Giai đoạn hiện tại.** Nhóm đã hoàn tất tái hiện R1–R4, chọn cấu hình trên D1-dev và đánh giá trên D1-test, D2-test. Phase 4 đã có báo cáo PDF, hồ sơ mã nguồn và tư liệu để Minh quay video. Gói nộp cuối sẽ dùng bản ghi của Minh. [Danh sách việc và người phụ trách](../PLAN.md#phase-4--hoàn-thiện-và-nộp-bài)

**Đã hoàn thành**

- [x] Thêm [tab tra cứu ViRHE4QA](../../apps/README.md#tra-cứu-virhe4qa) cho demo cục bộ và ghi nguồn cho toàn bộ kết quả theo D-34, D-35.
- [x] Đối chiếu cách mở khoản điều kiện tốt nghiệp theo khóa trên [bộ phát triển](../../experiments/application/README.md#kiểm-tra-khoản-điều-kiện-tốt-nghiệp).
- [x] Giải thích kết quả ngay dưới đoạn trích ở cả HCMUS và UIT theo D-38.
- [x] Hiện điểm của Điều quyết định thứ hạng và đánh dấu khoản ưu tiên theo khóa ở tiêu đề thẻ theo D-39.
- [x] Rà luồng chuyển nguồn, thử lại sau lỗi, đọc tiêu đề UIT và kiểm video trong hồ sơ nộp. [Checklist ngày 27/11](../reviews/workspace.md#kiểm-tra-ngày-27112026)

- [x] Chuẩn bị split D1 theo nhóm đoạn nguồn và lưu xếp hạng SimCSE-VN trên D1-dev. Xem cấu hình, điểm và file kết quả ở [§6.7](#67-bảng-theo-dõi-kết-quả).
- [x] Kiểm thử khoảng tin cậy cho chênh lệch giữa hai phương pháp và phép đo cảnh báo bằng ví dụ tính tay. Giao diện dùng với xếp hạng ở [§5.4](#54-interface--định-dạng-dữ-liệu).
- [x] Chọn bài báo SimCSE (EMNLP 2021) và mã nguồn tại commit cố định `235f89e` (release 0.4, ngày 2021-05-12).
- [x] Chọn Option 1 và đề tài "Trợ lý tra cứu quy chế học vụ" (từ Research).
- [x] Rà soát tĩnh mã nguồn tại commit (đọc file, chưa chạy). Kết quả ở [§4.4](#44-bản-đồ-mã-nguồn-tại-commit-235f89e).
- [x] Xác nhận bộ đánh giá chính truy cập được công khai: bản con ViRHE4QA trong repo ViRE. Chi tiết ở [§6.1](#61-datasets).
- [x] Tạo `README.md` và `PROJECT.md`.
- [x] Tạo repo GitHub với khung thư mục (Minh).
- [x] Viết script tái hiện `experiments/reproduction/run_r1.py`, `run_r1.bat` và `requirements-r1.txt` ([§4.5](#45-kế-hoạch-tái-hiện-kết-quả-paper)).
  - Đã chạy thử toàn bộ pipeline trên dữ liệu STS giả với model tí hon để kiểm tra code. Lần chạy này **không phải** kết quả R1 và không được lưu.
- [x] **R1 (23/11, laptop Huy):** trung bình 7 STS = **81,58**, khớp README (81,58) ở cả 7 task. So với paper (81,57) chỉ lệch +0,01, do STS-B ra 84,26 so với 84,25.
  - Chạy CPU, AMD 16 luồng, Windows; phần đánh giá mất 868 giây.
  - File: `experiments/reproduction/results/R1/` ([§6.7](#67-bảng-theo-dõi-kết-quả)).
- [x] **R2:** unsup SimCSE ra trung bình **76,25**, khớp paper ở cả 7 task.
- [x] **R3:** BERT-base chưa fine-tune ra trung bình **56,70**, khớp paper; hai task lệch ±0,01.
  - Kết luận: tái hiện được đúng khoảng cách của paper, từ 56,70 (BERT thô) lên 76,25 (unsup SimCSE) rồi 81,58 (sup SimCSE).
- [x] **R4 (23/11):** tự cài InfoNCE ở `src/simcse_lab/model/infonce.py`, cho cả unsup và sup có hard negative với log-weight.
  - Kiểm thử: 689/689 test pass. Ở float64, độ lệch lớn nhất so với `cl_forward` là khoảng 1,4e-9 và so với vòng lặp Eq. 4/8 là khoảng 8,4e-15.
  - File: `experiments/reproduction/results/R4/` ([§6.7](#67-bảng-theo-dõi-kết-quả)).
- [x] Introduction và Proposed Method của báo cáo IEEE (bản nháp ban đầu ở commit `652fa4e`), gồm cả phần giải thích luồng code gốc. Hai thành viên đã đọc chéo.
  - Bổ sung ngày 23/11 cho phần Phase 1 của Huy:
    - đoạn so sánh SimCSE với các cách làm trước (post-processing, các phương pháp contrastive khác, SBERT);
    - §Worked Example: ví dụ tính loss cho cả hai cách huấn luyện, dùng câu của Figure 1 và cosine minh hoạ, kiểm bằng `tests/test_worked_example.py`;
    - ví dụ lexical gap thật trong Introduction: câu D1 index 9542 ("bị dừng giữa chừng" và "đình chỉ" trong Điều 6). Nhóm đoạn của câu này phải vào D1-dev ([§6.2](#62-tiền-xử-lý-gán-nhãn-và-chia-dữ-liệu)).
- [x] Bản nháp [Related Work, mục II-A](../report/sections/related-work.tex) về biểu diễn câu và học tương phản. Mục II-A đối chiếu các baseline trong Bảng 5 của SimCSE với nghiên cứu gốc.
- [x] [Related Work, mục II-B](../report/sections/related-work.tex) về BM25 và truy hồi bằng vector tiếng Việt. Phần của Minh cũng đã có bảng dữ liệu, giao thức STS, kết quả gốc và giới hạn khi áp dụng sang tra cứu quy chế. [Experimental Setup](../report/sections/experimental-setup.tex) · [Results and Discussion](../report/sections/results.tex)
- [x] **Corpus D2 (23/11, D-17):** quy chế đào tạo của Trường ĐH KHTN, gồm hai văn bản.
  - QĐ 1175/QĐ-KHTN (2021): 24 Điều, PDF có lớp chữ, công khai.
  - QĐ 3087/QĐ-KHTN ngày 29/9/2026: 27 Điều. ChatGPT chép từ bản scan; nhóm làm sạch 165 lỗi OCR có kiểm chứng (158 ở lượt 1, 7 ở lượt 2 ngày 24/11). Bản dùng để lập chỉ mục đã hiệu đính tiếp theo ảnh PDF chính thức, gồm Điều 12, 13, 16 và 17.
  - Mô tả và metadata ở [`data/d2/`](../../data/d2/README.md). Chữ QĐ 1175 (văn bản công khai) có trong Git ở `data/d2/`; bản chép QĐ 3087 chỉ ở `data/raw/d2/`, không đăng công khai (D-18).
  - Bảng đối ứng Điều 2021 ↔ 2026 (`data/d2/article_map.tsv`, 26 chủ đề): đã duyệt ngày 24/11 sau khi đối chiếu nội dung (D-18).
  - Rà soát lại ngày 24/11: sha256 khớp, URL công khai của QĐ 1175 vẫn tải được, hai đoạn có độ giống thấp của bản chép 2026 đã đọc tay đối chiếu.
  - Ngày 25/11 đã xuất corpus hai quy chế trên máy Huy bằng checkpoint đã ghim và kiểm file đầu ra với hai nguồn. [Đường dẫn và cách tạo lại](../../data/d2/README.md#file).

- [x] **E0 trên D1-dev (25/11):** kiểm ba bảng xếp hạng bàn giao và đối chiếu điểm BM25 của câu 9542 bằng phép tính độc lập. [Kết quả E0](../../experiments/external_dataset/results/E0/d1-dev.md)
- [x] **D1-test (25/11):** chạy BM25, SimCSE-VN và Hybrid với cấu hình đã chốt trên D1-dev, tính khoảng tin cậy Hybrid so với BM25 và đánh giá cảnh báo ở ngưỡng cố định. [Bảng kết quả và khoảng tin cậy](../../experiments/external_dataset/results/E1/d1-test.md)
- [x] **E2 trên D1-test (25/11):** so sánh ba phương pháp theo ba mức trùng từ, báo chỉ số và khoảng tin cậy trong mỗi nhóm. [Kết quả E2](../../experiments/application/results/E2/d1-test.md)
- [x] **E3 trên D1-test (25/11):** vẽ đường cong risk–coverage từ xếp hạng Hybrid đã lưu, đánh dấu ngưỡng cố định từ D1-dev. [Biểu đồ E3](../../experiments/external_dataset/results/E3/d1-test-risk-coverage.png)
- [x] **E5 trên D1-test (26/11)** Đã đối chiếu nội dung và kiểm chéo thứ hạng của 20 ca Hybrid trượt Hit@1 cùng 2 ca xếp đúng. [Bảng E5 D1-test](../../experiments/application/results/E5/d1-test.md)
- [x] **Bộ chấm D2 (25/11):** gắn mã riêng cho các Khoản lặp số và kiểm bằng dữ liệu giả rằng lệnh chấm đọc được ba bảng xếp hạng, xuất chỉ số theo Điều, chủ đề và Khoản, khoảng tin cậy, bảng theo mức trùng từ và đánh giá cảnh báo. [Lệnh và đầu ra](../../experiments/application/README.md#chấm-d2-test)
- [x] **Nhãn D2 (26/11):** Huy và Minh đã thống nhất nhãn sau hai lượt gán độc lập. Tệp hợp nhất đã qua rà trùng, kiểm định dạng và đối chiếu mã Điều/Khoản với corpus. [Bộ đánh giá D2](../../data/d2/README.md#câu-hỏi-và-nhãn-d2-đã-chốt)
- [x] **E2 và E3 trên D2-test (26/11):** chạy ba phương pháp với cấu hình D1-dev trên nhãn đã chốt. Đã kiểm lại xếp hạng, chỉ số theo Điều, chủ đề, Khoản và điểm cảnh báo. [Kết quả D2-test](../../experiments/application/results/D2/d2-test.md)
- [x] **E5 trên D2-test (26/11):** đối chiếu thứ hạng, nhãn và văn bản gốc của các ca sai được chọn, gồm toàn bộ câu ngoài phạm vi bị đánh dấu tin cậy. [Bảng E5 D2-test](../../experiments/application/results/E5/d2-test.md)
- [x] **Demo và E4 (26/11):** Minh đã kiểm demo trên corpus hai phiên bản và đo độ trễ truy hồi trên CPU. [Cấu hình và kết quả E4](../../experiments/application/results/E4/cpu-latency.md)
- [x] **Báo cáo IEEE (26/11)** Đã hoàn thành [các mục của báo cáo](../report/README.md), gồm ứng dụng, đóng góp của từng thành viên và giới hạn rút ra từ E5. [Checklist rà soát và tái lập](../reviews/workspace.md).
- [x] **Công bố D2 (26/11).** Đã tải ẩn danh bộ D2 từ thư mục Drive dành cho bài nộp và đối chiếu SHA-256. [Đường dẫn và nội dung gói](../../data/d2/README.md#bộ-d2-công-khai)
- [x] **Tư liệu quay và hồ sơ chờ video (26/11).** Đã bàn giao slide chỉnh sửa được, PDF xem nhanh và ảnh gốc cho các cảnh demo. Hồ sơ đóng gói sẵn gồm mã nguồn, corpus và báo cáo. [Nội dung và cách kiểm ZIP](../README.md#báo-cáo-và-video)
- [x] **Hiển thị trích đoạn (26/11).** Đã đối chiếu công thức, bảng, thông tin sửa đổi và phạm vi áp dụng. Đã thử sửa câu, gửi lại sau lỗi mạng và tra cứu khi chỉ một phần các chủ đề có tín hiệu từ khóa. [Checklist giao diện](../reviews/workspace.md#kiểm-tra-giao-diện-tra-cứu)
- [x] **Đối chứng tiếp nối E5 (26/11).** Đã chạy bốn bản trên 16 câu phát triển do Codex điền nhãn cho Huy và Minh. [Kết quả và từng lỗi](../../experiments/application/results/clause-scope-pilot/comparison.md) · [Thiết kế và tiêu chí](../../experiments/application/clause-scope-comparison.md)
- [x] **Mở phiên bản được hỏi (26/11).** Đã thử ngoại tuyến trên cùng xếp hạng Hybrid và kiểm đủ 32 trang ở trạng thái mặc định. [Kết quả và nhận xét về khóa tuyển sinh](../../experiments/application/results/edition-display-pilot/comparison.md)
- [x] **Hai mẫu chọn khóa ngoại tuyến (26/11).** Hai mẫu dùng chung câu hỏi và căn cứ cho ba tình huống K24, K26 và tra cứu chung. [Gói mô phỏng](../../experiments/application/README.md#mô-phỏng-hai-cách-chọn-khóa)
- [x] **Chạy thử hai mẫu (26/11).** Chrome đã thực hiện sáu lượt mô phỏng từ gói bàn giao. Đã sửa đích PDF cho căn cứ thực hành trong cả hai bản quy chế. [Phiếu và đối chiếu trước/sau](../../experiments/application/results/cohort-walkthrough/comparison.md)

**Đã hoàn tất các mục Phase 3.** Nhóm có CLI truy hồi, [demo Gradio](../../apps/README.md) và kết quả E0–E5.

**Việc ưu tiên tiếp theo**

1. Minh quay video chính thức từ [tư liệu đã chuẩn bị](../README.md#báo-cáo-và-video).
2. Khi có bản ghi, Codex kiểm video và đóng gói theo [checklist Phase 4](../PLAN.md#phase-4--hoàn-thiện-và-nộp-bài).

Bản hiện tại tiếp tục phục vụ. Phép thử trên bộ mở đã chỉ ra một trường hợp cả ba cách tìm đồng ý về chủ đề sai. Việc xét thay phiên bản cần bằng chứng trên bộ xác nhận độc lập đã khóa nhãn. [Quy trình xác nhận](../../experiments/application/clause-scope-comparison.md#dữ-liệu-phát-triển-và-nhãn-giữ-kín)

---

## 2. Project Definition & Scope

### 2.1 Problem statement

Quy chế học vụ (đào tạo, cảnh báo học tập, xét tốt nghiệp…) được ban hành dưới dạng văn bản dài, chia theo Điều/Khoản. Sinh viên hỏi bằng ngôn ngữ đời thường, khác cách viết của văn bản (lexical gap). Vì vậy tìm kiếm theo từ khóa dễ bỏ sót, còn đọc toàn văn thì tốn thời gian.

**Bài toán ML** [Proposed]: *semantic retrieval*. Cho câu hỏi tiếng Việt $q$ và tập đoạn văn bản quy chế $C$, xếp hạng các Điều theo mức độ liên quan. Biểu diễn câu bằng sentence embeddings học theo contrastive learning (SimCSE), kết hợp với BM25.

### 2.2 Người dùng và use cases

| Người dùng | Use case chính |
|---|---|
| Sinh viên | Hỏi tự nhiên và nhận Điều/Khoản liên quan kèm trích đoạn để tự đọc căn cứ |
| Cố vấn học tập | Tra nhanh căn cứ khi tư vấn; dẫn chiếu chính xác số Điều, văn bản và phiên bản |

### 2.3 Giải pháp hiện có và hạn chế

Các nhận định trong bảng là đánh giá định tính [Proposed]; cần minh họa bằng ví dụ trong báo cáo.

| Giải pháp | Hạn chế |
|---|---|
| Ctrl+F / tìm từ khóa trong PDF | Chỉ khớp đúng chuỗi; người dùng phải đoán từ văn bản dùng; không xếp hạng |
| FAQ tĩnh trên website trường | Phạm vi hẹp, không phủ câu hỏi mới, thường không dẫn Điều/Khoản |
| Hỏi phòng đào tạo | Chậm, phụ thuộc giờ làm việc |
| Chatbot LLM tổng quát | Có thể sinh sai ("hallucination"), không chắc dẫn đúng văn bản của trường |
| Demo trong repo SimCSE (`demo/gradiodemo.py`, `demo/flaskdemo.py`) [Confirmed có trong commit] | Chỉ là UI bọc mô hình để tìm câu tương tự; đề Lab nói rõ dạng này **không đủ** làm đóng góp |

### 2.4 Phương án được chọn

Truy hồi lai **BM25 + SimCSE-VN** trên corpus quy chế đào tạo của Trường ĐH KHTN (QĐ 1175/2021 và QĐ 3087/2026; D-17), chia theo Điều/Khoản.
- **Kết quả hiển thị:** trích đoạn kèm tên văn bản, số hiệu, ngày ban hành và phạm vi áp dụng, có cảnh báo khi độ tin cậy thấp.
- **D1** (ViRHE4QA) dùng để đánh giá trên các đoạn quy chế đi kèm bộ dữ liệu.
- Ứng dụng **không** sinh câu trả lời bằng LLM.

### 2.5 Phạm vi

**MVP (bắt buộc)**

1. Corpus của ứng dụng gồm 2 văn bản trong [`data/d2/documents.yaml`](../../data/d2/documents.yaml): QĐ 1175/2021 (24 Điều) và QĐ 3087/2026 (27 Điều).
   - Tách Điều/Khoản và lưu metadata: văn bản, số hiệu, ngày ban hành, hiệu lực, phạm vi áp dụng.
   - Bản 2026 do ChatGPT chép từ scan, nhóm hiệu đính theo PDF chính thức. [Hồ sơ nguồn](../../data/d2/README.md#file)
   - Khi đánh giá D1, dùng corpus 297 đoạn của D1. Demo đọc tên văn bản từ bảng nguồn sau khi xếp hạng.
2. Ba phương pháp truy hồi chạy trên cùng pipeline: BM25, SimCSE-VN (dense) và Hybrid.
3. Giao diện Gradio gồm:
   - ô nhập câu hỏi;
   - tối đa ba chủ đề, mỗi chủ đề kèm Điều/Khoản theo phiên bản, trích đoạn, tên văn bản, số hiệu và phạm vi áp dụng;
   - nhãn "Độ tin cậy thấp" khi cần;
   - tab BM25 để so sánh kết quả theo từ khóa cho cùng câu hỏi.
4. Đánh giá định lượng trên D1 và D2 ([§6](#6-datasets--experimental-evaluation)) và đo latency trên CPU.
5. Tái hiện R1 ([§4.5](#45-kế-hoạch-tái-hiện-kết-quả-paper)) và tự cài lại InfoNCE kèm kiểm thử.

**Thí nghiệm nâng cao** gồm O1 tinh chỉnh theo miền và O3–O5 tách ảnh hưởng từng thành phần. [Điều kiện thực hiện](#66-thí-nghiệm-tùy-chọn)

**Ngoài phạm vi:** văn bản khác ngoài hai quy chế đào tạo trên, tự xác định phiên bản nào áp dụng cho từng khóa (ứng dụng chỉ hiển thị phạm vi áp dụng ghi trong văn bản), sinh câu trả lời bằng LLM, hội thoại nhiều lượt, OCR tự động trong ứng dụng (bản chép QĐ 3087 được chuẩn bị một lần, ngoài ứng dụng), so sánh khác biệt giữa các phiên bản văn bản, đăng nhập, database server, triển khai cloud, Option 2.

### 2.6 Đóng góp riêng của nhóm

| Tái sử dụng (có trích dẫn) | Nhóm tự phát triển |
|---|---|
| Mã nguồn và checkpoint SimCSE chính thức (tái hiện) | Pipeline tách Điều/Khoản, giữ metadata văn bản, phiên bản và vị trí ký tự để trích đúng đoạn |
| Checkpoint `VoVanPhuc/sup-SimCSE-VietNamese-phobert-base`, PhoBERT | Truy hồi lai, gộp điểm theo Điều, chọn λ trên dev |
| pyvi, rank_bm25, NumPy, Gradio | Cơ chế cảnh báo độ tin cậy cùng cách chọn và đánh giá ngưỡng |
| Bộ ViRHE4QA (bản con trong ViRE) | Chia lại D1 theo nhóm đoạn nguồn, vì cột `split` gốc bị rò rỉ (cùng một đoạn có câu hỏi ở cả train và test) |
| Quy chế đào tạo HCMUS (QĐ 1175/2021, QĐ 3087/2026); bản chép QĐ 3087 từ scan do ChatGPT tạo | Bộ test D2: câu hỏi kiểu sinh viên kèm câu ngoài phạm vi. Làm sạch bản chép QĐ 3087 (165 chỗ sửa trong hai lượt đầu), đối chiếu với OCR và hiệu đính theo PDF đã ký. Bảng đối ứng Điều 2021 ↔ 2026 |
| `evaluation.py` + SentEval của repo | Tự cài lại InfoNCE (unsup/sup + hard negative) và kiểm thử khớp với `cl_forward` |
| — | Thiết kế đánh giá công bằng: group split, bootstrap CI, phân tích theo mức trùng từ vựng, phân tích lỗi |

### 2.7 Tiêu chí thành công [Proposed]

- Ứng dụng chạy từ một bản clone sạch theo README, trên CPU.
- R1 khớp số trong README của repo: chênh lệch trung bình STS ≤ 0,5 điểm. Nếu lệch hơn, phải giải thích được nguyên nhân.
- Có bảng kết quả đầy đủ cho BM25 / SimCSE-VN / Hybrid trên D1-test và D2, kèm 95% CI cho các so sánh chính.
- Có bằng chứng cải thiện so với tìm kiếm từ khóa ở ít nhất một chiều: chất lượng truy hồi trên câu hỏi diễn đạt khác văn bản, hoặc chức năng trích dẫn và cảnh báo. Thành công **không** đòi hỏi thắng BM25 ở mọi metric; kết quả âm vẫn hợp lệ nếu được phân tích rõ.
- Đo được latency p50/p95 trên CPU.

---

## 3. Lab 03 Requirements

Nguồn: đề Lab 03 [Confirmed]. Rubric: Research Paper Understanding **40**, Implementation and Evaluation **20**, Experimental Analysis and Discussion **40**.

Mục Bonus Model Improvement (+10) **không áp dụng** cho nhóm: giảng viên xác nhận không xét bonus. Nhóm không làm việc gì nhắm tới bonus.

**Loại yêu cầu:** **B** = bắt buộc, **T** = tùy chọn.

| Mục đề | Yêu cầu | Loại | Công việc trong dự án | Bằng chứng nộp | Owner / Phase (PLAN.md) |
|---|---|---|---|---|---|
| 3.1 | Paper peer-reviewed, nêu title/authors/năm/venue/DOI, lý do chọn | B | SimCSE đăng tại EMNLP 2021. Hội nghị hạng A theo CORE2021, A\* theo CORE2023 và ICORE2026. [Bài báo](https://aclanthology.org/2021.emnlp-main.552/) · [Lịch sử xếp hạng](https://portal.core.edu.au/conf-ranks/448/) | Báo cáo §Introduction | Huy / 1 |
| 3.2.1–6 | Phân tích: problem & method, related work, model & theory, metrics, datasets & experiments, results & limitations | B | Đọc paper theo [§4](#4-simcse-research-foundation) | Báo cáo §Related Work, §Method; vấn đáp | Huy + Minh (mỗi người một phần) / 1 |
| 3.3.1 | Implement/reproduce thuật toán chính (được dùng code/weights công khai, có trích dẫn) | B | Chạy code chính thức tại commit; tự cài lại InfoNCE; tự xây pipeline truy hồi | `experiments/reproduction/`, `src/` | Huy (tái hiện, InfoNCE), Minh (pipeline tiếng Việt) / 2–3 |
| 3.3.2 | Giải thích code: execution flow, data loading, kiến trúc, training/inference, output | B | Bản đồ code [§4.4](#44-bản-đồ-mã-nguồn-tại-commit-235f89e) | Báo cáo, video | Huy / 2 |
| 3.3.3 | Đánh giá: train/val/test, chống leakage, metrics, kết quả định lượng, ví dụ, phân tích lỗi | B | [§6.2–6.5](#62-tiền-xử-lý-gán-nhãn-và-chia-dữ-liệu) | `results/`, báo cáo §Experiments | Minh (D1, metrics), Huy (so sánh, CI) / 2–3 |
| 3.3.4 | Tái hiện ≥1 kết quả (hoặc đánh giá tương đương); **đánh giá trên dataset mới** và nêu rõ khi không so sánh trực tiếp được | B | R1 ([§4.5](#45-kế-hoạch-tái-hiện-kết-quả-paper)); D1 + D2 ([§6.1](#61-datasets)) | Bảng R1; bảng E1/E2 | Huy (R1 ✓), Minh (D1), cả hai (D2) / 2–3 |
| 3.3.5 | Tái lập: dependencies, hyperparameters, seed, môi trường, hướng dẫn chạy | B | `pyproject.toml`, `configs/`, `experiments/*/results/*/env.txt`, README | Repo | Minh (README), Huy (chạy lại từ clone sạch) / 4 |
| 3.4.1 | Bài toán thực tế, người dùng, giá trị | B | [§2.1–2.2](#21-problem-statement) | Báo cáo §Application | Minh / 3 |
| 3.4.2 | Khảo sát giải pháp hiện có và hạn chế | B | [§2.3](#23-giải-pháp-hiện-có-và-hạn-chế) | Báo cáo | Minh / 3 |
| 3.4.3 | Ứng dụng chạy được: input thực, chạy model, hiển thị output thật | B | Gradio app ([§5](#5-application-architecture--implementation)) | Video demo | Minh / 3 |
| 3.4.4 | Cải thiện ≥1 chiều so với giải pháp hiện có; tách bạch phần mới và phần tái sử dụng | B | [§2.6](#26-đóng-góp-riêng-của-nhóm), E1–E3 | Bảng so sánh với BM25; bảng đóng góp | Cả hai / 3 |
| 3.4.5 | Bằng chứng theo đề gồm chỉ số, thời gian đáp ứng, mức hoàn thành tác vụ hoặc phản hồi có cấu trúc | B | Chỉ số E1–E4, độ trễ truy hồi và kết quả chạy tác vụ trong trình duyệt | `results/` | Huy (so sánh), Minh (độ trễ) / 3 |
| 3.4.6 | Thảo luận: tính hữu ích, hạn chế, khi nào thất bại, hướng phát triển | B | E5 phân tích lỗi; [§8.1](#81-rủi-ro-và-dự-phòng) | Báo cáo §Discussion | Huy / 3–4 |
| 4 | Nộp `[Group14].zip` theo mẫu của đề, gồm code/GitHub, README, video ≤ 30 phút và báo cáo PDF mẫu IEEE | B | [§8.4](#84-definition-of-done) | Bản nộp | Huy (báo cáo), Minh (video), Codex (kiểm và đóng gói) / 4 |
| 4 | Link dataset/code phải truy cập được (nếu không, **trừ 50%**). Dataset được nộp bằng link (giảng viên cho phép) | B | Kiểm tra link ở chế độ ẩn danh trước khi nộp | Checklist DoD | Minh / 4 |

**Ánh xạ rubric:** 40 điểm Paper Understanding ← [§4](#4-simcse-research-foundation) và vấn đáp. 20 điểm Implementation & Evaluation ← R1, InfoNCE, pipeline, metrics. 40 điểm Experimental Analysis & Discussion ← E1–E5, CI, phân tích lỗi, thảo luận.

---

## 4. SimCSE Research Foundation

Nguồn: paper (PDF nhóm cung cấp) và code tại commit `235f89e` [Confirmed]. Mục này chỉ tóm tắt đủ để triển khai và vấn đáp. Chi tiết đọc trong paper.

### 4.1 Bài toán và ý tưởng

- **Sentence embedding:** ánh xạ câu thành vector sao cho câu cùng nghĩa có cosine similarity cao. Paper đánh giá chủ yếu trên STS.
- **Ý tưởng:** contrastive learning với in-batch negatives. Mỗi câu $x_i$ có một positive $x_i^+$; các câu khác trong batch là negative. Encoder là BERT/RoBERTa pretrained, fine-tune toàn bộ.

### 4.2 Thành phần phương pháp

| Thành phần | Nội dung [Confirmed] |
|---|---|
| InfoNCE (Eq. 1) | $\ell_i=-\log \frac{e^{\mathrm{sim}(h_i,h_i^+)/\tau}}{\sum_{j=1}^{N} e^{\mathrm{sim}(h_i,h_j^+)/\tau}}$, với sim là cosine và τ là temperature (mặc định 0,05 trong `train.py`) |
| Unsupervised (Eq. 4) | $x_i^+=x_i$. Cùng một câu đi qua encoder 2 lần với **dropout mask khác nhau** (dropout chuẩn p = 0,1) → 2 embedding làm positive pair. Dropout đóng vai trò data augmentation tối thiểu |
| Bằng chứng về dropout | Table 3 (STS-B dev): p = 0,1 → 82,5; p = 0 → 71,1; "fixed 0.1" (cùng mask) → 43,6. Table 1: dropout tốt hơn crop, word deletion, synonym replacement, MLM. Table 2: một encoder tốt hơn hai encoder |
| Supervised (Eq. 5) | Dùng NLI (SNLI+MNLI): entailment làm positive, contradiction làm **hard negative**. Table 4: 84,9 → 86,2 khi thêm hard negative. Trong Table 7, α = 1 và α = 2 cùng đạt 86,2 trên STS-B dev ở độ chính xác công bố |
| Pooling (Table 6) | Unsup: [CLS] + MLP **chỉ khi train**, bỏ MLP khi test. Sup: [CLS] + MLP |
| Alignment / uniformity (Eq. 2–3) | Alignment: positive pair gần nhau. Uniformity: embedding trải đều trên hypersphere. Unsup SimCSE cải thiện uniformity mà vẫn giữ alignment (Fig. 2–3) |
| Anisotropy (§5) | Với vector đã chuẩn hóa, khi các phần tử ma trận Gram đều dương, tổng các phần tử chặn trên trị riêng lớn nhất. Đây là lập luận giải thích xu hướng. Phụ lục F đo được phổ giá trị kỳ dị phẳng hơn trên các câu STS-B được khảo sát |
| Đánh giá (§6.1, App. B) | 7 STS task (STS12–16, STS-B, SICK-R). Lấy cosine trực tiếp, **không** dùng regressor. Báo **Spearman**, gộp theo setting "all" |
| Kết quả chính (Table 5) | Trung bình 7 STS, BERT-base: unsup SimCSE **76,25**, sup SimCSE **81,57**. Baseline BERT first-last avg 56,70; SBERT 74,89 |
| Training (App. A) | Unsup: 10⁶ câu Wikipedia, 1 epoch, BERT-base bs 64, lr 3e-5. Sup: SNLI+MNLI (314k), 3 epoch, bs 512, lr 5e-5. Đánh giá STS-B dev mỗi 250 step và giữ checkpoint tốt nhất. Theo [README của tác giả](https://github.com/princeton-nlp/SimCSE/blob/235f89e0244b23673b69fbbc4a1cd9868c5a5c24/README.md#training), các kết quả trong paper được chạy trên GPU NVIDIA 3090 với CUDA 11. |

### 4.3 Training và inference

- **Training:** batch N câu (hoặc cặp/bộ ba) → encoder (dropout bật) → pooler [CLS] (+ MLP) → ma trận cosine N×N (hoặc N×2N khi có hard negative) chia τ → cross-entropy với nhãn là đường chéo.
- **Inference:** encoder ở chế độ eval (dropout tắt) → [CLS] (unsup: `cls_before_pooler`; sup: `cls`, tức `pooler_output`) → chuẩn hóa L2 → cosine.

### 4.4 Bản đồ mã nguồn tại commit `235f89e`

Rà soát tĩnh ngày 2026-11-23 [Confirmed]. Nhóm vẫn phải tự đọc lại để giải thích được.

| File / hàm | Vai trò | Nhóm làm gì |
|---|---|---|
| `train.py` – `ModelArguments` | `temp` = 0.05; `pooler_type` = "cls" (cls, cls_before_pooler, avg, avg_top2, avg_first_last); `hard_negative_weight` = 0 (là **log** của trọng số); `do_mlm` = False; `mlm_weight` = 0.1 | Đọc, giải thích |
| `train.py` – đọc dữ liệu | `.txt` = 1 cột (câu được nhân đôi làm cặp); `.csv` 2 cột = cặp; 3 cột = cặp + hard negative. `prepare_features` tokenize rồi gom thành list `num_sent` câu cho mỗi ví dụ | Giải thích luồng dữ liệu |
| `train.py` – data collator | Pad rồi reshape thành `(bs, num_sent, len)` | Giải thích |
| `simcse/models.py` – `Pooler` | `cls`/`cls_before_pooler` đều lấy `last_hidden[:,0]`; MLP được áp riêng trong `cl_forward` khi `pooler_type == "cls"`. `avg_first_last` dùng `hidden_states[0]` (output lớp embedding) và lớp cuối (R3 xác nhận số 56,70 của paper dùng đúng cách này) | Giải thích; liên hệ Table 6 |
| `MLPLayer`, `Similarity` | Linear + Tanh; cosine / temp | `Similarity`: tự viết lại (cosine / τ) trong `src/simcse_lab/model/infonce.py` ✓. `MLPLayer`: chỉ giải thích, vì nhóm không huấn luyện lại |
| `cl_forward` | Flatten `(bs·num_sent, len)` → encoder → pooler → MLP (nếu `cls`) → tách z1, z2, (z3) → all_gather khi chạy distributed → `cos_sim` (bs×bs) → nối cột z1·z3 (bs×2bs) → cộng `hard_negative_weight` vào logit của hard negative tương ứng → `CrossEntropyLoss` với `labels = arange(bs)` (+ MLM loss nếu bật) | **Tự cài lại loss** và test khớp ([§4.5](#45-kế-hoạch-tái-hiện-kết-quả-paper), R4) |
| `sentemb_forward` | Inference: pooler (+ MLP nếu `cls`) | Giải thích |
| `simcse/trainers.py` – `CLTrainer.evaluate` | SentEval (fast mode) trên STS-B dev và SICK-R dev trong lúc train; dùng `stsb_spearman` để chọn checkpoint tốt nhất | Giải thích |
| `evaluation.py` | `--pooler` {cls, cls_before_pooler, avg, avg_top2, avg_first_last}; `--mode` {dev, test, fasttest}; `--task_set` {sts, transfer, full, na}. STS12–16 lấy Spearman "all"; STS-B, SICK-R lấy Spearman trên test. `cls` = `pooler_output` của HF | **Dùng nguyên** cho R1–R3 |
| `simcse_to_huggingface.py` | Đổi tên `mlp`→`pooler`, bỏ tiền tố `bert.`/`roberta.` → checkpoint HF chuẩn | Giải thích vì sao `cls` khi eval = MLP lúc train |
| `simcse/tool.py` – `SimCSE` | `encode` (chuẩn hóa L2, `max_length` = 128), `similarity`, `build_index` (faiss `IndexFlatIP`, hoặc IVF nếu `faiss_fast`), `search` (threshold = 0.6, top_k = 5). Tự chọn `cls_before_pooler` khi tên model chứa "unsup" | Tham khảo khi viết `encoders.py`/`retrieval.py` |
| `run_unsup_example.sh` | bert-base-uncased, wiki1m, 1 epoch, bs 64, lr 3e-5, max_seq_length 32, `--pooler_type cls`, temp 0.05, eval_steps 125, fp16 | Dùng cho O3 (tùy chọn) |
| `run_sup_example.sh` | 4 GPU × bs 128, lr 5e-5, 3 epoch, max_seq_length 32, `--pooler_type cls`, temp 0.05 | Chỉ đọc |
| `data/download_*.sh`; `SentEval/data/downstream/download_dataset.sh` | Tải wiki1m, NLI, `senteval.tar` từ HF `princeton-nlp/datasets-for-simcse` | Dùng cho R1 |
| `requirements.txt` | `transformers==4.2.1`, `scipy==1.5.4`, `datasets==1.2.1`… README khuyên PyTorch 1.7.1 | Xem rủi ro môi trường ở [§8.1](#81-rủi-ro-và-dự-phòng) |

**Khác biệt cần ghi vào báo cáo** [Confirmed]

- Tại commit này **không có** cờ `--mlp_only_train`. "MLP chỉ khi train" được thực hiện bằng cách train với `cls` rồi đánh giá với `cls_before_pooler`.
- Script dùng `eval_steps` = 125, còn paper ghi đánh giá mỗi 250 step.
- README báo trung bình **81,58** cho `sup-simcse-bert-base-uncased`, còn paper Table 5 ghi **81,57**: STS-B trong README là 84,26, trong paper là 84,25.

### 4.5 Kế hoạch tái hiện kết quả paper

| ID | Thí nghiệm | Mốc so sánh [Confirmed] | Loại | Tài nguyên [Unverified] |
|---|---|---|---|---|
| R1 | `evaluation.py --model_name_or_path princeton-nlp/sup-simcse-bert-base-uncased --pooler cls --task_set sts --mode test` | README: 75,30 / 84,67 / 80,19 / 85,40 / 80,82 / 84,26 / 80,39; TB 81,58 | **Bắt buộc** | CPU laptop; thời gian thực ghi trong `results/R1/env.txt` |
| R2 | Như R1 với `unsup-simcse-bert-base-uncased --pooler cls_before_pooler` | TB 76,25 | Khuyến nghị (rẻ) — **đã chạy** | như R1 |
| R3 | `bert-base-uncased --pooler avg_first_last` (không fine-tune) | Paper: 56,70 (BERT first-last avg). R3 thu được cùng điểm trung bình với cách tính tại commit, dùng `hidden_states[0]` (lớp embedding) và lớp cuối | Khuyến nghị (rẻ) — **đã chạy** | như R1 |
| R4 | Tự cài InfoNCE (unsup + sup có hard negative, log-weight) trong `src/simcse_lab/model/infonce.py`. Test: so với bản cài vòng lặp ngây thơ theo Eq. 4/8 (Eq. 8 ở §6.3 là Eq. 5 có trọng số α) và với đoạn tính loss trích từ `cl_forward` (ghi trích dẫn) trên tensor ngẫu nhiên; sai số < 1e-6 (float64) | — | **Bắt buộc** | CPU, khoảng 1 phút |
| R5 | (O3) Train unsup mini bằng code tự viết, tập con wiki1m, p ∈ {0; 0,1}, đo STS-B dev | Chỉ tái hiện **xu hướng** của Table 3 | Tùy chọn | GPU T4 |
| R6 | Đo alignment/uniformity (Eq. 2–3) cho R2 và R3 | Xu hướng định tính của Fig. 2–3 | Tùy chọn | CPU/GPU, ngắn |

**Cách chạy R1–R3** [Confirmed – script đã chạy thử]

- Trên Windows: double-click `experiments\reproduction\run_r1.bat`, hoặc chạy `experiments\reproduction\run_r1.bat R2` / `R3`.
- Trên máy khác: `python experiments/reproduction/run_r1.py --exp R1`, dùng Python 3.9–3.11.
- Bảng kết quả và môi trường chi tiết: [experiments/reproduction/README.md](../../experiments/reproduction/README.md).
- Script tự làm từng bước và bỏ qua bước đã xong:
  1. Kiểm tra `experiments/reproduction/SimCSE` đúng commit; nếu thiếu thì tải zip của commit.
  2. Tạo `.venv-repro` ở thư mục gốc và cài `experiments/reproduction/requirements-r1.txt`.
  3. Kiểm SHA-256 của các đầu vào STS. Nếu cần tải, dùng bản SentEval cố định và kiểm SHA-256 của gói trước khi giải nén.
  4. Gọi `evaluation.py` gốc với đường dẫn đến đúng revision checkpoint ghi trong kết quả đã công bố.
  5. Mỗi lần chạy ghi log, điểm và môi trường vào thư mục riêng dưới `outputs/reproduction/`. Số liệu đã công bố ở [§6.7](#67-bảng-theo-dõi-kết-quả).

**Môi trường đã chốt (D-12)**

- Python 3.11 venv với các bản pin `numpy==1.23.5`, `scipy==1.10.1`, `scikit-learn==1.2.2`, `torch==2.5.1` (CPU), `transformers==4.46.3`.
- [Confirmed bằng thử nghiệm] SentEval tại commit tạo `np.array` từ list các câu có độ dài khác nhau trong `STSEval.loadFile`, nên **lỗi với numpy ≥ 1.24**. Vì vậy cần numpy < 1.24, kéo theo Python ≤ 3.11.
- **Sai lệch so với repo:** repo pin `transformers==4.2.1` và khuyên dùng torch 1.7.1. Hai bản này không có wheel cho Python hiện đại trên Windows. Nhóm dùng bản mới hơn và ghi rõ trong báo cáo. [Confirmed bằng R1] Với các bản này, R1 ra đúng số trong README ở cả 7 task, nên khác biệt phiên bản không ảnh hưởng tới kết quả inference.

### 4.6 SimCSE gốc và checkpoint tiếng Việt dùng trong ứng dụng

| | SimCSE gốc (paper) | SimCSE-VN (ứng dụng) |
|---|---|---|
| Checkpoint | `princeton-nlp/{unsup,sup}-simcse-bert-base-uncased` | `VoVanPhuc/sup-SimCSE-VietNamese-phobert-base` |
| Ngôn ngữ / backbone | Tiếng Anh, BERT/RoBERTa | Tiếng Việt, PhoBERT (kiến trúc RoBERTa, 135M tham số) [Confirmed, model card] |
| Dữ liệu train | wiki1m / SNLI+MNLI [Confirmed] | Model card không nêu [Unverified] |
| Tiền xử lý | Không | **Bắt buộc tách từ bằng pyvi** (`ViTokenizer.tokenize`); dùng `pooler_output` [Confirmed, model card] |
| Độ dài tối đa | — | 256 subword tokens (giới hạn PhoBERT) [Confirmed, README PhoBERT] |
| License | MIT (repo) | Model card không nêu [Unverified]. PhoBERT-base: MIT; PhoBERT-base-v2: AGPL-3.0 [Confirmed] |
| Dùng cho | R1–R3 (tái hiện) | Ứng dụng, E1–E5 |

Kết quả của SimCSE-VN **không** phải kết quả của paper. Trong báo cáo phải gọi đúng là "checkpoint cộng đồng huấn luyện theo phương pháp SimCSE".

### 4.7 Câu hỏi vấn đáp cả hai phải trả lời được

1. Vì sao dropout tạo được positive pair? Vì sao p = 0 và "fixed 0.1" thất bại?
2. Vai trò của τ và in-batch negatives. Vì sao paper thấy SimCSE ít nhạy với batch size (App. A)?
3. Eq. 5 và Eq. 8 (§6.3): hard negative là gì? Vì sao `hard_negative_weight` là log của trọng số α?
4. Alignment, uniformity và anisotropy liên quan với nhau thế nào?
5. Khác biệt giữa `cls`, `cls_before_pooler` và `pooler_output` trong code.
6. Vì sao báo Spearman và setting "all"? Vì sao kết quả giữa các paper khó so sánh (App. B)?
7. Đi qua luồng dữ liệu từ file `.txt`/`.csv` đến loss.
8. Vì sao PhoBERT cần tách từ? Rủi ro khi tách từ không nhất quán giữa index và query.
9. Vì sao BM25 mạnh trên D1? Khi nào dense retrieval có lợi?
10. Vì sao cosine không phải xác suất đúng? Ngưỡng cảnh báo được chọn và đánh giá thế nào?

---

## 5. Application Architecture & Implementation

### 5.1 Luồng xử lý

**Ký hiệu** (giống báo cáo): λ là trọng số fusion của Hybrid, θ là ngưỡng cảnh báo độ tin cậy. τ và α chỉ dùng cho SimCSE (temperature và trọng số hard negative, [§4](#4-simcse-research-foundation)).

```
[Offline – build index]  (mỗi corpus một index riêng)
Corpus HCMUS (ứng dụng, D2): data/raw/d2/* + data/d2/documents.yaml (metadata)
Corpus D1: 297 đoạn trong ViRHE4QA_v2.csv cho truy hồi; bảng nguồn bổ sung tên văn bản khi hiển thị
  → ingest: tách Điều / Khoản → chunk ≤ 256 token → corpus.jsonl
  → preprocess: Unicode NFC → chuẩn hóa dấu thanh (khoá→khóa) → tách từ pyvi
  → BM25 index (token thường hóa)  +  SimCSE-VN embeddings (chuẩn hóa L2) → NumPy cosine

[Online – mỗi câu hỏi]
Câu hỏi → preprocess (cùng hàm) → điểm BM25 và cosine cho mọi chunk
  → gộp chunk về Điều (MaxP: lấy max) → min-max normalize theo từng phương pháp
  → Hybrid: s = λ·BM25_norm + (1−λ)·Dense_norm   (λ chọn trên D1-dev)
  → xếp hạng Điều (D1 lưu top-20, D2 lưu đủ 51 Điều)
  → corpus HCMUS: gộp các Điều cùng chủ đề theo data/d2/article_map.tsv thành một kết quả theo khóa đã chọn
  → tối đa 3 chủ đề (kèm Điều/Khoản và trích đoạn theo phiên bản)
  → Confidence: cosine SimCSE của chunk tốt nhất trong Điều đứng đầu < θ  ⇒  cảnh báo "Độ tin cậy thấp"
  → UI: Điều/Khoản · trích đoạn · văn bản · số hiệu · ngày ban hành · phạm vi áp dụng · so sánh BM25
```

### 5.2 Vai trò từng thành phần [Proposed]

| Thành phần | Vai trò | Lý do |
|---|---|---|
| SimCSE-VN | Khớp ngữ nghĩa, xử lý câu hỏi diễn đạt khác văn bản | Thành phần ML chính, gắn trực tiếp với paper |
| BM25 (`rank_bm25`) | Khớp từ khóa, số liệu, thuật ngữ, viết tắt | Đại diện giải pháp hiện có; rất mạnh trên D1 theo tham chiếu ngoài ([§6.1](#61-datasets)) |
| Hybrid λ-fusion | Kết hợp hai loại tín hiệu; chỉ 1 tham số | Đơn giản, chọn trên dev, dễ giải thích |
| NumPy | Tính tích vô hướng trên toàn bộ vector đã chuẩn hóa L2, tương đương cosine | Quét toàn bộ chunk ở quy mô corpus hiện tại (D-24). Sai số dấu phẩy động có thể ảnh hưởng thứ tự các điểm rất sát nhau |
| Gộp MaxP theo Điều | Điều dài phải chia chunk vì giới hạn 256 token; hiển thị và đánh giá ở mức Điều | Nhãn gold của D1 ở mức Điều |

Min-max theo từng câu hỏi làm mất thang điểm tuyệt đối. Nếu mọi Điều có cùng điểm cho một phương pháp, thành phần chuẩn hóa của phương pháp đó bằng 0. Cảnh báo dùng cosine của SimCSE-VN.

**Chọn đoạn trích sau khi xếp hạng Điều.** Với BM25 và dense, lấy chunk có điểm thô cao nhất theo phương pháp tương ứng. Hybrid ở λ = 1 hoặc λ = 0 dùng đúng quy tắc BM25 hoặc dense. Với 0 < λ < 1, áp dụng cho từng chunk trong Điều cùng hai phép chuẩn hóa đã dùng khi xếp hạng Điều (min và max lấy trên các điểm MaxP của mọi Điều cho câu hỏi đó). Giữ cả giá trị âm khi điểm chunk thấp hơn min, cho thành phần bằng 0 nếu max = min, rồi chọn chunk có tổng có trọng số λ và 1−λ lớn nhất. Khi bằng điểm, chọn theo ID tăng dần: `article_id` cho Điều và `chunk_id` cho đoạn, theo kiểu ID của corpus. `top1_dense_cos` là cosine thô của chính đoạn đã chọn trong Điều đầu tiên, trước khi gộp chủ đề.

### 5.3 Metadata, trích dẫn, phiên bản và trường hợp không chắc chắn

- **Corpus HCMUS (ứng dụng, D2):** [`data/d2/documents.yaml`](../../data/d2/documents.yaml), mỗi văn bản một mục.
  - Các trường: `doc_id`, `title`, `so_hieu`, `ngay_ban_hanh`, `hieu_luc`, `trang_thai`, nguồn, `file`, `sha256`, `nguyen_van`.
  - Index **cả hai phiên bản** (2021 và 2026). Lý do: theo Điều 27 quy chế 2026, quy chế mới áp dụng cho khóa tuyển từ năm học 2026–2027; với khóa tuyển từ 2025 trở về trước, Trường lựa chọn áp dụng quy định mới có lợi hơn cho người học.
  - Chỉ index các Điều của quy chế, không index ba Điều của QĐ 3087 (file 2026 có kèm Quyết định ban hành; file PDF 2021 chỉ có phần quy chế).
- **Corpus D1:** Chỉ mục giữ mã và nguyên văn từng đoạn từ CSV ViRE. Demo tra mã đoạn trong [bảng nguồn](../../data/README.md#nguồn-văn-bản-d1) để hiện tên văn bản theo tác giả, dòng đối chiếu và trang PDF UIT khi đã xác minh. Khi đoạn khớp chỉ là tiêu đề, kết quả giải thích điểm của tiêu đề và mở đoạn nguồn nếu thẻ đầu được mở tự động.
- **Index:** mỗi chunk giữ `doc_id` (D1: `virhe4qa`), `article_id`, `article`, `article_title`, `clause`, offset ký tự để trích đúng đoạn.
- **Hiển thị (corpus HCMUS):**
  - Mỗi kết quả ghi năm quy chế, Điều, Khoản nếu có và tên Điều. Số hiệu dưới trích đoạn mở văn bản gốc. Ngày ban hành nằm cạnh liên kết. Đường dẫn sửa đổi đi cùng Điều liên quan.
  - [Trích đoạn trên cả hai tab](../../apps/README.md#trích-đoạn-trên-giao-diện) dùng phần văn bản mà bộ truy hồi chọn, với ngoại lệ tra trực tiếp danh sách điều kiện tốt nghiệp theo D-37. Khi ranh giới cắt qua đoạn văn, bảng hay công thức, giao diện lấy đủ phần đó theo vị trí ký tự trong cùng Khoản.
  - Mục **Áp dụng theo khóa tuyển sinh** ghi tên và hiệu lực mỗi văn bản một lần trong mỗi danh sách kết quả. Nguồn của bản ChatGPT chép từ scan và phần hiệu đính của nhóm nằm ở [hồ sơ dữ liệu](../../data/d2/README.md#file).
  - Giao diện dùng khóa tuyển sinh đã chọn và hiển thị phạm vi áp dụng ghi trong văn bản.
  - Các Điều cùng chủ đề (theo `data/d2/article_map.tsv`, mỗi chủ đề có 1–3 Điều) hiển thị thành **một** kết quả, kèm các phiên bản có trong chủ đề đó.
  - Người dùng chọn khóa HCMUS hoặc hệ UIT trước khi tra. Hai tab lọc theo lựa chọn trước khi lấy ba kết quả. Với K21–K25, tra bản 2021 và cho đối chiếu bản 2026 cùng chủ đề theo Điều 27. [Các lựa chọn và giới hạn](../../apps/README.md).
- **Độ tin cậy thấp:** với kết quả xếp hạng thông thường, tab tra cứu thu gọn các chủ đề. Khi mở trực tiếp danh sách theo D-37, thẻ đầu ghi căn cứ chọn khoản. Cảnh báo ngay trên tab ghi phương pháp, phiên bản và Điều/Khoản xếp đầu, kèm gợi ý đối chiếu văn bản hoặc liên hệ Phòng Đào tạo. Ngưỡng θ được chọn và đánh giá theo E3 ([§6.4](#64-thí-nghiệm-thiết-yếu)).
- **Tab từ khóa:** chỉ chủ đề có ít nhất một Điều nhận điểm BM25 khác 0 mới được hiển thị, tối đa ba chủ đề, gồm cả bản đối chiếu trong cùng chủ đề. Khi không có tín hiệu, tab hướng dẫn đổi từ khóa. Quy tắc hiển thị này cũng áp dụng cho tab chính nếu chạy với λ = 1. Các bảng xếp hạng dùng để chấm D1/D2 vẫn bao gồm các Điều theo quy tắc của thí nghiệm.

### 5.4 Interface & định dạng dữ liệu

Trong HTML kết quả, mỗi đoạn có mục **Vì sao có kết quả này?**. Kết quả tìm kiếm đọc cosine theo mã đoạn đang hiển thị. Khoản được mở trực tiếp theo D-37 giải thích căn cứ chọn khoản và ghi khóa khi sinh viên đã chọn. [Cách đọc trên giao diện](../../apps/README.md#trích-đoạn-trên-giao-diện)

Tiêu đề thẻ hiển thị điểm từ bản xếp hạng của phương pháp đang dùng. Với HCMUS, Điều đầu tiên đủ điều kiện trong phạm vi tra quyết định vị trí chủ đề trước khi sắp bản hiển thị và thêm bản đối chiếu. Với UIT, điểm thuộc về đoạn nguồn trong danh sách đã lọc theo hệ. Khi quy tắc tốt nghiệp quyết định vị trí, thẻ hiển thị căn cứ ưu tiên theo D-39.

Dùng định dạng dưới đây cho dữ liệu và kết quả truy hồi.

```text
corpus.jsonl   {chunk_id, doc_id, article_id, article, article_title, clause|null, text, char_start, char_end}
               # D2 thêm clause_id|null; các cửa sổ trong cùng một Khoản có chung mã.
queries.jsonl  {qid, question, gold_article_ids: [..], gold_clause_ids: [..], split: dev|test, source: virhe4qa|d2, origin: team|form|null, in_scope: bool}
               # D2: article_id = "<doc_id>:dieu-<n>"; gold_clause_ids lấy từ clause_id của corpus.
               # Mã Khoản: "<article_id>:khoan-<m>", thêm ":1", ":2", ... theo thứ tự nếu số Khoản lặp.
               # Câu ngoài phạm vi có hai danh sách gold rỗng.
               # D2: origin = team (nhóm viết) hoặc form (câu thu qua Google Form); D1: origin = null
               # D1: chỉ có split dev|test, gold_clause_ids rỗng; D2 luôn là test
runs/<method>.jsonl  {qid, ranked: [[article_id, score, best_chunk_id], ...], top1_dense_cos}
               # D1: top-20 Điều. D2: cả 51 Điều để tính đủ 10 chủ đề sau khi gộp.
               # Clause@1 tra clause_id của best_chunk_id trong Điều hạng 1 trước khi gộp chủ đề.
               # Chọn best_chunk_id và top1_dense_cos theo quy tắc trích đoạn ở §5.2.
```

CLI truy hồi nhận corpus, split và danh sách phương pháp. Endpoint Gradio `/search` nhận câu hỏi và khóa (hoặc Tra cứu chung), trả về HTML của tab tra cứu, HTML của tab BM25 và thông báo trạng thái. [Lệnh truy hồi](../../experiments/external_dataset/README.md) · [Giao diện](../../apps/README.md). Khi nạp D1, endpoint `/search_d1` nhận câu hỏi và hệ đào tạo (hoặc Tra cứu chung) và trả HTML chứa trích đoạn, ngữ cảnh và căn cứ văn bản của ViRHE4QA. Manifest E1 lưu đường dẫn và SHA-256 của câu hỏi để [E2](../../experiments/application/README.md#e2-trên-d1-test) và E3 đọc trực tiếp từng lượt chạy.

Xem [cách xác định mã khi số Khoản lặp](../../data/d2/README.md#mã-điều-và-khoản). Bộ chấm hỗ trợ corpus cũ bằng cách tra Khoản từ offset trong nguồn đã kiểm SHA-256.

Phiếu phát triển HCMUS có thêm vị trí từng đoạn đã đối chiếu với PDF và ghi chú cho thông tin đến từ bên ngoài hai quy chế. [Định dạng và phạm vi sử dụng của phiếu](../../experiments/application/clause-scope-comparison.md#dữ-liệu-phát-triển-và-nhãn-giữ-kín)

| Module (vị trí trong repo) | Input → Output | Owner | Tái sử dụng / Mới |
|---|---|---|---|
| `data/prepare_virhe4qa.py` | CSV ViRE → corpus/queries D1 + group split | Minh | Mới |
| `src/simcse_lab/retrieval/hcmus.py` và `ingest.py` | Metadata và nguồn HCMUS đã kiểm SHA-256, hoặc context D1 → Điều/Khoản, chunk có offset | Minh | Mới |
| `src/simcse_lab/retrieval/preprocess.py` | text → text chuẩn hóa / tách từ / token BM25 | Minh | Mới (dùng pyvi) |
| `src/simcse_lab/model/encoders.py` | list[str] → ndarray (L2-norm) | Minh | Model tái sử dụng; code mới (tham khảo `simcse/tool.py`) |
| `src/simcse_lab/retrieval/search.py` | Câu hỏi → điểm từng chunk → xếp hạng Điều và cosine của đoạn trích đầu tiên | Minh | Mới (dùng rank_bm25, NumPy) |
| `src/simcse_lab/evaluation/metrics.py` | D1: câu hỏi + xếp hạng → Hit@1, Hit@3, MRR@10 | Minh | Đã có |
| [`src/simcse_lab/evaluation/stats.py`](../../src/simcse_lab/evaluation/stats.py) | Câu hỏi và xếp hạng theo `qid`. Tính CI theo cặp, chọn θ trên D1-dev và đánh giá cảnh báo. Đã kiểm bằng [ví dụ tính tay](../../tests/test_stats.py) | Huy | Đã có |
| `experiments/external_dataset/` | Chạy 3 phương pháp trên D1 (Minh); chọn λ, θ trên D1-dev (Huy) → `results/` | Minh, Huy | Mới |
| [`experiments/external_dataset/evaluate_d1_test.py`](../../experiments/external_dataset/evaluate_d1_test.py) | CSV, checkpoint và cấu hình đã chốt → corpus D1, xếp hạng D1-test, chỉ số, CI theo cặp và độ bao phủ | Huy | Đã có |
| [`experiments/external_dataset/plot_d1_risk_coverage.py`](../../experiments/external_dataset/plot_d1_risk_coverage.py) | Xếp hạng Hybrid và nhãn D1-test đã lưu → điểm đường cong và hình risk–coverage tại cấu hình đã chốt | Huy | Đã có |
| `experiments/application/` | So sánh trên D1-test và D2, phân tích lỗi (Huy); đo latency (Minh) → `results/` | Huy, Minh | Mới |
| [`experiments/application/analyze_d1_overlap.py`](../../experiments/application/analyze_d1_overlap.py) | CSV và kết quả E1 đã lưu → mã câu, Hit@k, MRR@10 và CI theo mức Jaccard trên D1-test | Huy | Đã có |
| [`experiments/application/evaluate_d2.py`](../../experiments/application/evaluate_d2.py) | Nhãn D2 đã chốt, corpus và ba xếp hạng đã lưu → E2 theo Điều, chủ đề và Khoản, CI theo cặp và biểu đồ E3. [Lệnh](../../experiments/application/README.md#chấm-d2-test) | Huy | [Đã chấm D2-test](../../experiments/application/results/D2/d2-test.md) |
| [`experiments/application/compare_clause_scope.py`](../../experiments/application/compare_clause_scope.py) | 16 câu phát triển và cấu hình đóng băng. Xuất điểm thô, thứ tự Điều, Khoản, cảnh báo và HTML của bốn bản. [Lệnh](../../experiments/application/README.md#so-sánh-trước-khi-thay-bản-truy-hồi) | Huy | [Đã chạy](../../experiments/application/results/clause-scope-pilot/summary.json) |
| [`experiments/application/compare_edition_display.py`](../../experiments/application/compare_edition_display.py) | Phát lại điểm của A để so hai cách hiển thị phiên bản. Xuất HTML từng cặp, đường dẫn mở căn cứ và số câu thấy ngay theo nhóm năm. [Lệnh](../../experiments/application/README.md#thử-mở-phiên-bản-được-hỏi) | Huy | [Đã chạy ngoại tuyến](../../experiments/application/results/edition-display-pilot/summary.json) |
| [Bộ dựng mẫu chọn khóa](../../experiments/application/cohort_study/build.py) | Hai trang HTML dùng chung câu hỏi và nguồn cục bộ. ZIP có hướng dẫn mở và ba tình huống. [Chạy sáu tổ hợp](../../experiments/application/README.md#chạy-sáu-lượt-mô-phỏng) để xuất kết quả, nhật ký và ảnh | Codex | [Lệnh dựng và kiểm](../../experiments/application/README.md#mô-phỏng-hai-cách-chọn-khóa) |
| [Đóng gói và đối chiếu](../../tools/package_submission.py) | `prepare` đóng gói mã, corpus và PDF. `verify --prepared` kiểm hồ sơ này. `build --video` thêm bản ghi của Minh, có thể kèm phụ đề cùng bản. `verify` kiểm gói cuối theo SHA-256 | Codex | [Hướng dẫn bàn giao](../README.md#báo-cáo-và-video) |
| `experiments/reproduction/` | Chạy R1–R4 vào `outputs/reproduction/`. Kết quả đã công bố ở [§6.7](#67-bảng-theo-dõi-kết-quả) | Huy | Code gốc + mới |
| `src/simcse_lab/model/infonce.py` + `tests/test_infonce.py` | R4: InfoNCE tự cài + test khớp `cl_forward` | Huy | Mới |
| [app.py](../../apps/app.py), [search.js](../../apps/search.js), [search.css](../../apps/search.css) và [regulation_excerpts.py](../../src/simcse_lab/regulation_excerpts.py) | Gradio gọi bộ truy hồi, nhóm kết quả, quản lý trạng thái câu đang hỏi và trình bày trích đoạn theo cấu trúc văn bản | Minh | [Giao diện](../../apps/README.md) |

Ba hàm của `stats.py` nhận các bản ghi JSONL đã giải mã. Mỗi lần gọi dùng một tập dữ liệu và một split. Lọc câu hỏi và từng bảng xếp hạng theo cùng tập `qid` khi đánh giá một nhóm con.

- `paired_bootstrap(queries, baseline, candidate)` trả về chênh lệch *candidate trừ baseline* và hai đầu khoảng tin cậy cho từng chỉ số trong `levels`. Hàm ghép theo `qid` và lấy mẫu lại các câu trong phạm vi.
- `select_threshold(queries, run, min_coverage=0.8)` chọn θ lớn nhất đạt độ bao phủ yêu cầu trên D1-dev. `warning_metrics(queries, run, threshold=theta)` dùng θ đã chọn. Câu có `top1_dense_cos >= theta` được đánh dấu tin cậy, kể cả khi bằng ngưỡng. Cả hai hàm đưa sai số dấu phẩy động tối đa `1e-6` ở hai đầu miền cosine về −1 hoặc 1 và báo lỗi nếu vượt dung sai.
- Với D2, truyền `article_to_topic` cho `paired_bootstrap` và `warning_metrics`. Từ mỗi dòng của [article_map.tsv](../../data/d2/article_map.tsv), ghép khóa `<doc_id>:dieu-<dieu>` với giá trị `topic_id`. Kết quả có cả mức Điều và mức chủ đề.

### 5.5 Cấu trúc thư mục

Các đường dẫn công khai và thư mục làm việc cục bộ của dự án:

```
├── README.md · pyproject.toml · .gitignore
├── data/                             # README + prepare_virhe4qa.py; raw/ processed/ bị gitignore
│   └── d2/                           # ✓ README.md, documents.yaml, article_map.tsv, chữ QĐ 1175, queries_d2.jsonl. Bản chép QĐ 3087 ở raw/d2/
├── src/simcse_lab/
│   ├── model/                        # encoders.py, infonce.py ✓
│   ├── retrieval/                    # hcmus.py, ingest.py, preprocess.py, search.py
│   ├── regulation_excerpts.py         # trình bày trích đoạn của hai quy chế
│   └── evaluation/                   # metrics.py (D1), d2.py, stats.py
├── experiments/
│   ├── reproduction/                 # ✓ run_r1.py, run_r1.bat, requirements-r1.txt, results/R1–R3; run_r4.py, results/R4
│   │   └── SimCSE/                   # code gốc @ 235f89e (gitignore; script tự tải nếu thiếu)
│   ├── external_dataset/             # D1, cấu hình chốt trong results/D1-dev-tuning/summary.json
│   └── application/                  # D2, so sánh theo mức trùng từ, cảnh báo, latency, lỗi (E2–E5) → results/
├── apps/                             # app.py, search.css, d1.css, search.js
├── tools/                            # kiểm Markdown, kiểm giao diện, đóng và kiểm gói nộp riêng
├── tests/                            # chunker, chuẩn hóa, metrics, infonce (✓ test_infonce.py, infonce_reference.py, test_worked_example.py, conftest.py)
├── docs/                             # PLAN.md, application/, report/, reviews/
└── .venv-repro/ · .cache/            # venv tái hiện, cache HuggingFace (gitignore)
```

Môi trường truy hồi và demo dùng venv riêng. Xem [lệnh cài và kiểm chứng D1](../../experiments/external_dataset/README.md) và [lệnh khởi động Gradio](../../apps/README.md).

Trong cả hai ZIP, `source/` chứa mã và corpus đã kiểm. Bảng SHA-256 và PDF báo cáo nằm ở gốc gói. Gói nộp cuối có thêm video của Minh. [Lệnh đóng gói và kiểm từng tệp](../README.md#báo-cáo-và-video)

**Stack bản bàn giao:** Python, PyTorch, Transformers, pyvi, rank_bm25, NumPy, PyYAML, Gradio và pytest. Phiên bản môi trường tái lập D1 có trong hướng dẫn D1.

---

## 6. Datasets & Experimental Evaluation

### 6.1 Datasets

| ID | Dataset | Vai trò | Thông tin | Truy cập / License |
|---|---|---|---|---|
| **D1** | ViRHE4QA, bản con trong ViRE: `data/ViRHE4QA_v2.csv` @ ViRE commit `60ea7155134eaa426ab1d0a82d2bbbf327d1b470` (sha256 `23fb9699…aa5682`) | **Dataset mới chính** (bắt buộc); đánh giá trên corpus riêng của D1 | [Confirmed, đã đọc file] 1.000 câu hỏi, 297 context khác nhau (287 bắt đầu bằng "Điều"). Mỗi câu hỏi có đúng 1 context gold. Cột: `split, index, context, question, extractive answer, abstractive answer, label`. Đã ghép mọi đoạn với cột `document` trong bộ tác giả. [Tên văn bản UIT, căn cứ và phạm vi xác minh](../../data/README.md#nguồn-văn-bản-d1). Context dài: trung vị 173 từ, p90 495, tối đa 1.249 → cần chunk. Ý nghĩa cột `label` (0/1, 500/500) chưa rõ [Unverified] và không dùng | Tải trực tiếp từ GitHub. ViRE: code MIT, dataset bên thứ ba giữ license gốc. Kho R2GQA của tác giả công bố bộ dữ liệu cho mục đích nghiên cứu. Chỉ dùng đánh giá học thuật, trích dẫn cả hai. **Nộp bằng link permalink** tới file ở commit trên (giảng viên cho phép nộp dataset bằng link) |
| **D2** | Câu hỏi nhóm xây dựng trên quy chế đào tạo HCMUS, QĐ 1175/2021 và QĐ 3087/2026 ([`data/d2/`](../../data/d2/README.md), D-17) | Test trong bối cảnh thực tế (**chỉ test**) | [Bộ nhãn đã chốt và số câu](../../data/d2/README.md#câu-hỏi-và-nhãn-d2-đã-chốt). Corpus 51 Điều (24 + 27). QĐ 1175 trích nguyên văn từ PDF có chữ. ChatGPT chép QĐ 3087 từ scan và nhóm làm sạch | Trường đã công bố PDF của cả hai quyết định. QĐ 91/2023 sửa bảng xếp loại trong bản 2021, xem [metadata D2](../../data/d2/documents.yaml). Bộ đánh giá có `origin: team` và không chứa dữ liệu cá nhân. [Gói D2 công khai trên Drive](../../data/d2/README.md#bộ-d2-công-khai) ghi rõ các tệp được chia sẻ. Bản ChatGPT chép QĐ 3087 chỉ nộp trong `[Group14].zip` (D-18) |
| R-STS | STS12–16, STS-B, SICK-R | Tái hiện R1–R3 | Theo script repo | `senteval.tar` (HF `princeton-nlp/datasets-for-simcse`) |
| D1-full | ViRHE4QA đầy đủ (9.758 cặp QA, 294 điều) | Tùy chọn | [Confirmed theo arXiv:2409.02840] | [Bản tác giả công bố](https://github.com/DoPhamPhucTinh/R2GQA/tree/0653933b6f28b8a05bb822997aed734f7590670e) dùng để kiểm tên nguồn D1; bảng trích dẫn ngoại tuyến đi kèm demo |
| Dự phòng | EduCoQA (`data/EduCoQA.csv` trong ViRE; 511 câu hỏi / 262 đoạn, tư vấn tuyển sinh HCMUT) | Chỉ dùng nếu D1 không dùng được | [Confirmed] | CC BY-NC 4.0; bản trên HF cần đăng nhập |

Cách tạo [corpus D2 từ hai quy chế](../../data/d2/README.md#file) và quy trình [chốt nhãn D2](#62-tiền-xử-lý-gán-nhãn-và-chia-dữ-liệu) là hai bước chuẩn bị đầu vào cho đánh giá.

**Tham chiếu bên ngoài trên D1** (không phải kết quả của nhóm; protocol khác nên **không so sánh trực tiếp**):

- **ViRE** (toàn bộ 1.000 câu): BM25 đạt P@1 65,8%, R@10 93,5%, MRR@10 76,05. Hybrid tốt nhất đạt MRR@10 81,42, với backbone khác SimCSE-VN.
- **R2GQA** trên ViRHE4QA đầy đủ (theo split của họ): BM25 đạt P@1 68,75; embedding LM pretrained đạt P@1 44,06.

**Hệ quả:** câu hỏi D1 được viết từ chính văn bản nên trùng từ vựng cao, và BM25 rất mạnh. Nhóm **không cam kết** dense hay hybrid sẽ thắng BM25 trên D1.
- Lợi ích ngữ nghĩa được kiểm tra chủ yếu trên D2 (câu hỏi kiểu sinh viên). Nhóm câu ít trùng từ trong D1-test là bằng chứng phụ (E2); nhóm này có thể nhỏ, nên phải báo kèm số câu và CI.
- Câu D2 được soạn sau khi đã biết nội dung quy chế (§6.2). Phân phối từ vựng có thể khác câu hỏi tự nhiên, chẳng hạn ít trùng từ hơn và bất lợi cho BM25. Báo cáo cần nêu thiên lệch này.
- Corpus D2 nhỏ: 51 Điều nhưng chỉ 26 chủ đề, vì phần lớn Điều 2021 và 2026 nói cùng một quy định. Hit@3 vì vậy dễ cao với mọi phương pháp. D2 báo hai mức (theo Điều và theo chủ đề), kèm Clause@1 và mức ngẫu nhiên; báo cáo nêu rõ quy mô corpus (§6.3).

### 6.2 Tiền xử lý, gán nhãn và chia dữ liệu

**D1**

- Corpus là 297 context, mỗi context một `article_id`. Trong 1.000 dòng nguồn, có 17 dòng câu hỏi trùng nguyên văn. Sau khi loại trùng, D1-dev có 224 câu thuộc 59 context và D1-test có 759 câu thuộc 238 context.
- **Group split theo context** (seed 42): dev khoảng 20% context, test khoảng 80%. Câu hỏi về cùng một Điều không nằm ở cả dev và test.
- **Bắt buộc:** nhóm context "Điều 6. Báo cáo tiến độ thực hiện KLTN" (4 câu hỏi, gồm câu index 9542) phải vào **dev**, vì câu 9542 đã dùng làm ví dụ lexical gap trong Introduction của báo cáo. Gán nhóm này trước, rồi chia ngẫu nhiên phần còn lại.
- Corpus vẫn chứa **toàn bộ** 297 context, vì đây là kho tri thức chứ không phải nhãn.
- Bỏ qua cột `split` gốc: test gốc chỉ có 77 câu, và cách chia này bị rò rỉ. Ví dụ đã kiểm tra 23/11: context của Điều 6 nói trên có 2 câu ở train và 2 câu ở test.
- Loại câu hỏi trùng lặp nguyên văn nếu có, và ghi lại số lượng đã loại.

**D2** (D-17; mô tả corpus ở [`data/d2/README.md`](../../data/d2/README.md))

- **Corpus:** 51 Điều của hai văn bản trong `data/d2/documents.yaml`. Dùng đúng file 2026 có SHA-256 trong metadata sau khi chạy `python data/d2/prepare_2026.py`. Không đưa ba Điều của QĐ 3087 (Quyết định ban hành) vào corpus.
- **Nguồn câu hỏi:** Huy tự soạn phần của mình. Minh duyệt phần của mình từ bản nháp do trợ lý soạn. Xem [nguồn và số câu theo nhóm](../../data/d2/README.md#câu-hỏi-và-nhãn-d2-đã-chốt).
- **Cách viết (D-18):** viết kiểu "gập sách": đọc Điều, gập văn bản lại, rồi viết câu như khi hỏi bạn hoặc phòng đào tạo. Được dùng thuật ngữ thông dụng (học phần, tín chỉ, điểm trung bình tích lũy…), không chép nguyên câu hay mệnh đề từ văn bản. Câu ngoài phạm vi là câu mà cả hai văn bản đều không trả lời (ví dụ ký túc xá, căn tin).
  - Lý do: quy tắc cũ "không chép quá 3 từ liên tiếp" cấm cả thuật ngữ sinh viên vẫn dùng, làm câu bất lợi cho BM25 ngay từ cách xây dựng. Cách viết mới vẫn có thể cho câu ít trùng từ hơn câu thật, nên báo E2 theo mức trùng từ và báo riêng nhóm `form` nếu có.
- **Loại trùng:** nhóm rà nguyên văn và thông tin được hỏi trước khi chốt. [Kết quả rà trùng](../../data/d2/README.md#câu-hỏi-và-nhãn-d2-đã-chốt).
- **Gán nhãn:** hai thành viên gán `gold_article_ids` và `gold_clause_ids` độc lập trước khi thống nhất. Với số Khoản lặp, đối chiếu nguyên văn để chọn [mã Khoản theo thứ tự xuất hiện](../../data/d2/README.md#mã-điều-và-khoản). [Tỷ lệ đồng ý trước thảo luận](../../data/d2/README.md#câu-hỏi-và-nhãn-d2-đã-chốt) được tính bằng cách so khớp toàn bộ tập nhãn trên từng câu. Phiếu đối chiếu nội bộ lưu các điểm khác nhau.
- **Hai phiên bản:**
  - Gold gồm mọi Điều, ở bất kỳ phiên bản nào, có nội dung trả lời câu hỏi; câu được tính đúng nếu khớp bất kỳ gold nào (§6.3).
  - Không viết câu hỏi mà đáp án phụ thuộc vào việc khóa nào áp dụng phiên bản nào.
  - Nếu hai phiên bản trả lời khác nhau, ghi gold cả hai và thêm một dòng ghi chú.
- **Kỷ luật dữ liệu:** D2 **chỉ dùng để test**. Trọng số λ và ngưỡng θ chọn trên D1-dev. Bảng đối ứng `article_map.tsv` được duyệt trước khi gán nhãn. [Nhãn D2](../../data/d2/queries_d2.jsonl) được chốt trước khi xem dự đoán.

**Chống leakage:**
- λ và θ chỉ chọn trên D1-dev.
- Không xem kết quả test trước khi chốt cấu hình.
- Phiên bản ứng dụng dùng cho demo phải là cấu hình đã chốt.

### 6.3 Baseline và metrics

**Phương pháp so sánh**

| Method ID | Phương pháp | Loại |
|---|---|---|
| `bm25` | BM25 (đại diện tìm kiếm từ khóa hiện có; mạnh hơn Ctrl+F nên là baseline thận trọng) | Bắt buộc |
| `dense` | SimCSE-VN dense (checkpoint nguyên bản) | Bắt buộc |
| `hybrid` | Hybrid `bm25` + `dense` | Bắt buộc |
| `phobert-raw` | PhoBERT-base mean pooling, không fine-tune: kiểm tra trên tiếng Việt luận điểm của paper rằng embedding PLM thô kém hơn contrastive | Khuyến nghị (rẻ) |
| `dense-unsup` | `VoVanPhuc/unsup-SimCSE-VietNamese-phobert-base` | Tùy chọn |

**Metrics** (mức Điều; câu hỏi có nhiều gold thì tính đúng nếu khớp bất kỳ gold nào)

- **Hit@k** (k = 1, 3, 5, 10): tỉ lệ câu hỏi có Điều đúng trong top-k. Với 1 gold, Hit@k = Recall@k.
- **MRR@10:** trung bình 1/rank của Điều đúng đầu tiên, tính 0 nếu rank > 10.
- **Mức Khoản (chỉ D2, trên câu có `gold_clause_ids`):** Clause@1 là tỷ lệ câu mà `clause_id` của chunk trích dẫn thuộc gold. Dùng chunk của Điều đứng đầu trước khi gộp chủ đề. Báo kèm số câu có nhãn Khoản.
- **Hai mức cho D2:** luôn báo cả hai, không báo mức theo chủ đề một mình.
  - **Theo Điều (chặt):** như D1, không gộp. Một Điều chỉ đúng khi nằm trong gold.
  - **Theo chủ đề (khớp giao diện, dễ hơn):** các Điều được gộp thành chủ đề theo [`data/d2/article_map.tsv`](../../data/d2/article_map.tsv) (26 chủ đề cho 51 Điều; đã duyệt 24/11, D-18). Trước khi cắt top-k, các Điều cùng chủ đề chỉ tính một lần; câu hỏi tính là đúng khi chủ đề của một gold nằm trong top-k.
  - **Vì sao mức chủ đề dễ hơn:** sau khi gộp, top-k chứa nhiều chủ đề khác nhau hơn, nên Hit@k và MRR@10 chỉ có thể tăng hoặc giữ nguyên. Kể cả Hit@1 cũng dễ hơn khi chỉ một phiên bản trả lời được câu hỏi. Ví dụ T18: bản 2026 thêm chuyển ngành, nên câu hỏi về chuyển ngành chỉ có gold là Điều 21 bản 2026; nếu Điều 20 bản 2021 đứng đầu thì mức chủ đề tính đúng, mức Điều tính sai.
  - **Gộp trong cùng một phiên bản (giữ theo D-18):** T02 (Điều 2 và 3 bản 2021), T09 (Điều 12 và 13 bản 2026), T16 (Điều 17 và 18 bản 2021). Đã đối chiếu nội dung: một bản tách thành hai Điều nội dung mà bản kia gộp trong một Điều. Ví dụ Điều 10 bản 2021 gồm cả xét giao và đánh giá khóa luận, bản 2026 tách thành Điều 12 và 13.
  - **Mức ngẫu nhiên:** với g Điều gold, xáo đều 51 Điều cho Hit@k kỳ vọng bằng 1 − C(51−g, k)/C(51, k). Để tính mốc chủ đề của cùng hệ thống, dùng 1.000 hoán vị Điều với seed 42, gộp từng hoán vị rồi tính chỉ số. Ví dụ, chủ đề chứa 3 Điều có xác suất đứng đầu là 3/51. Công thức k/26 cho một chủ đề gold chỉ áp dụng nếu xáo đều trực tiếp 26 chủ đề.
  - Runs lưu ở mức Điều (§5.4). E2 cần tính bảng chỉ số mức chủ đề từ runs và `article_map.tsv`.
- **Ý nghĩa thống kê:** lấy mẫu có hoàn lại 1.000 lần trên các câu trong phạm vi (seed 42), giữ cặp kết quả của mỗi câu. Báo 95% CI của ΔMRR@10 và ΔHit@1 bằng phân vị 2,5% và 97,5% của các chênh lệch trung bình, nội suy tuyến tính.
- **Mẫu số của E3:** độ bao phủ là số câu được đánh dấu tin cậy chia cho toàn bộ câu. Hit@1 của mỗi nhóm chỉ tính trên câu trong phạm vi của nhóm đó. False-confidence là số câu ngoài phạm vi được đánh dấu tin cậy chia cho toàn bộ câu ngoài phạm vi. Kết quả kèm số câu và dùng `None` (JSON `null`) khi mẫu số bằng 0.
- **Đường cong risk–coverage:** mỗi điểm dùng một giá trị `top1_dense_cos` đã quan sát và tính độ bao phủ theo quy tắc `cosine >= ngưỡng`. Risk là tỷ lệ sai ở hạng 1 trong các câu trong phạm vi được đánh dấu tin cậy. D2 có cả đường theo Điều và theo chủ đề. Các câu bằng điểm được tính cùng nhau. Risk không xác định khi chưa có câu trong phạm vi được chấp nhận. Điểm đánh dấu dùng θ đã chọn trên D1-dev.
- **Latency:** p50/p95 mỗi truy vấn trên CPU, tách riêng thời gian tách từ, encode và search; thời gian build index.

### 6.4 Thí nghiệm thiết yếu

Lệnh kiểm chứng gói D1-dev đã xác nhận SHA-256, thứ tự xếp hạng và chỉ số của ba phương pháp trên 224 câu. Lượt chọn cấu hình E1 và E3 đã dùng điểm của toàn bộ corpus trên D1-dev. [Lệnh chọn cấu hình và kết quả](../../experiments/external_dataset/README.md#chốt-cấu-hình-bằng-d1-dev)

[Corpus HCMUS](../../data/d2/README.md#file) đã được xuất và đối chiếu với hai nguồn trên máy Huy. Minh đã kiểm demo trên corpus này và đo độ trễ CPU ngày 26/11. [Kết quả D2-test](../../experiments/application/results/D2/summary.json) lưu phiên bản đầu vào và lệnh đã chạy với cấu hình D1-dev.

| ID | Mục đích | Thiết lập | Đầu ra |
|---|---|---|---|
| E0 | Kiểm tra cài đặt | Chạy BM25 trên D1-dev và đối chiếu cách tính hạng bằng ví dụ tính tay. Số ViRE ở §6.1 là tham khảo trên toàn bộ dữ liệu. Chỉ mở D1-test sau khi cố định tiền xử lý và cấu hình | Ghi chú kiểm tra |
| E1 | Chất lượng truy hồi trên dataset mới | `bm25`, `dense`, `hybrid` (+ `phobert-raw`) trên D1-test. λ chọn trên D1-dev (lưới 0..1, bước 0,1, tối ưu MRR@10) | Bảng + CI cho `hybrid`−`bm25`, `dense`−`phobert-raw` |
| E2 | Bối cảnh thực tế và câu hỏi diễn đạt khác văn bản | Ba phương pháp trên D2-in-scope (kết quả chính) và D1-test (bằng chứng phụ) với cấu hình cố định. Chia nhóm thấp/vừa/cao theo Jaccard tập token Pyvi, tại phân vị 1/3 và 2/3. Ở D2 lấy Jaccard lớn nhất với các Điều gold, giữ các câu đồng điểm trong cùng nhóm và báo số câu kể cả nhóm rỗng. Báo cả mức Điều và chủ đề, Clause@1 và nhóm `origin: form` nếu có (§6.3) | Bảng + phân tích theo nhóm |
| E3 | Đánh giá cảnh báo độ tin cậy | Chọn θ lớn nhất sao cho coverage ≥ 80% trên D1-dev với trọng số Hybrid đã chốt. Trên D1-test và D2: coverage, Hit@1 trong nhóm "tin cậy" và nhóm "không tin cậy", tỉ lệ câu ngoài phạm vi của D2 bị đánh dấu tin cậy (false-confidence). Hạn chế phải nêu trong báo cáo: θ chọn trên corpus và kiểu câu hỏi của D1 (UIT) rồi giữ nguyên khi áp dụng cho HCMUS | Bảng + biểu đồ risk–coverage |
| E4 | Chi phí sử dụng | Latency p50/p95 trên CPU cho `bm25`/`dense`/`hybrid`; ghi cấu hình máy | Bảng |
| E5 | Phân tích lỗi | 20–30 câu sai của `hybrid` trên D1-test và D2, phân loại: tách từ, Điều dài bị cắt, số/ngày tháng, viết tắt (vd. ĐTTX, KLTN), câu hỏi cần nhiều Điều, khác biệt diễn đạt | Bảng phân loại + ví dụ |

Thêm R1 và R4 ([§4.5](#45-kế-hoạch-tái-hiện-kết-quả-paper)). Kết quả của nhóm chỉ ghi vào bảng ở §6.7 sau khi đã chạy.

### 6.5 Tái lập thí nghiệm

- R1–R4 chạy bằng [script tái hiện](../../experiments/reproduction/README.md). Với các thí nghiệm ứng dụng E0–E5, lưu cấu hình, điểm, xếp hạng (nếu có), phiên bản thư viện, Python, CPU/GPU và commit của nhóm cùng kết quả.
- Seed 42 cho chia dữ liệu và bootstrap. Fine-tuning (nếu có) dùng 3 seed {42, 43, 44} và báo mean ± std.
- Ghi rõ commit SimCSE `235f89e`, commit ViRE `60ea715`, revision của checkpoint HF khi tải, và với D2 là sha256 các văn bản trong `data/d2/documents.yaml` cùng commit của `article_map.tsv` đã dùng.
- Khi so sánh với số của paper, README hoặc ViRE, ghi rõ "khác protocol/dữ liệu, không tương đương trực tiếp" nếu đúng như vậy.

### 6.6 Thí nghiệm tùy chọn

Chỉ làm khi MVP xong và còn thời gian.

| ID | Nội dung | Điều kiện làm |
|---|---|---|
| O1 | Domain-adaptive SimCSE: (a) unsup SimCSE tiếp tục trên câu của corpus quy chế; hoặc (b) supervised với cặp (câu hỏi, Điều đúng) + hard negative do BM25 khai thác, cần thêm D1-train theo group split. So với `dense` trên cùng test, 3 seed | Chỉ khi E1–E5 xong trước 06/12; dừng mọi việc tùy chọn sau 08/12 |
| O3 | R5 mini dropout ablation | Có GPU rảnh |
| O4 | pyvi vs VnCoreNLP (RDRSegmenter); RRF vs λ-fusion; có/không tiền tố tiêu đề Điều trong chunk | Rẻ, nếu E5 chỉ ra vấn đề liên quan |
| O5 | Encoder đa ngôn ngữ làm trần tham chiếu (vd. `intfloat/multilingual-e5-base`) | Chỉ để thảo luận; không bắt buộc thắng |

**Phép so sánh tiếp nối E5.** Bốn bản dùng chung cấu hình D1-dev và điểm thô trên bộ phát triển mở. Bảng dưới ghi kết quả. [Quy trình và tiêu chí xác nhận](../../experiments/application/clause-scope-comparison.md)

### 6.7 Bảng theo dõi kết quả

Sau D-37, số lượt mở đúng khoản điều kiện tốt nghiệp trong sáu ca phát triển tăng từ 0 lên 6. Cả 16 phản hồi trên bộ phát triển mở trùng bản trước. [Đầu vào, cấu hình và kết quả](../../experiments/application/README.md#kiểm-tra-khoản-điều-kiện-tốt-nghiệp)

Đã kiểm lời giải thích D-38 trên Chrome ở cả hai nguồn. [Câu hỏi, lựa chọn, trích dẫn và nội dung đã mở](../../experiments/application/results/demo-selection/result-reasons.json)

Ở D-39, điểm xếp hạng hiển thị trên Chrome khớp với bảng điểm của câu phát triển HCMUS `pilot-01` và UIT `9542`. Trên 22 lượt gửi trước và sau, sau khi bỏ các nhãn mới, toàn bộ nội dung trả về trùng nhau. [Cấu hình và kết quả kiểm tra](../../experiments/application/results/demo-selection/rank-scores.json)

Trước D-37, đã so cùng câu hỏi xét tốt nghiệp trước và sau khi thêm hai bộ chọn với đúng cấu hình demo. [Các Điều đứng đầu theo lựa chọn](../../experiments/application/results/demo-selection/example.json)

Độ phủ nguồn của tab D1 được kiểm riêng với corpus E1. [Kết quả theo từng văn bản](../../experiments/external_dataset/results/D1-sources/coverage.json)

| Exp | Trạng thái | Kết quả chính | File |
|---|---|---|---|
| Rà giao diện hai nguồn | 27/11, bộ phát triển | 26/26 phản hồi HCMUS khớp từng byte trước và sau khi sửa giao diện. Sáu lượt hỏi điều kiện tốt nghiệp mở đúng Khoản | [Cấu hình và từng phản hồi](../../experiments/application/results/ui-review/workspace-2026-11-27.json) |
| R1 | [x] 23/11 | TB 81,58 (README 81,58; paper 81,57). Từng task: 75,30 / 84,67 / 80,19 / 85,40 / 80,82 / 84,26 / 80,39 → khớp README 7/7 | `experiments/reproduction/results/R1/` |
| R2 | [x] 23/11 | TB 76,25 = paper. Từng task: 68,40 / 82,41 / 74,38 / 80,91 / 78,56 / 76,85 / 72,23 → khớp 7/7 | `experiments/reproduction/results/R2/` |
| R3 | [x] 23/11 | TB 56,70 = paper. Từng task: 39,70 / 59,37 / 49,67 / 66,03 / 66,19 / 53,88 / 62,06 → lệch ≤ 0,01 | `experiments/reproduction/results/R3/` |
| R4 | [x] 24/11 | Chạy lại sau khi ổn định phép tính ở nhiệt độ thấp. 689/689 test đạt. Lệch tối đa ở float64 là 8,7e-15 so với vòng lặp Eq. 4/8 và 1,4e-9 so với `cl_forward`. Ở float32 lệch tối đa 9,5e-7 | [Kết quả, seed và cấu hình](../../experiments/reproduction/results/R4-2026-11-24/metrics.json) |
| R4 | [x] 23/11 | 689/689 test pass. float64: lệch tối đa 8,4e-15 so với vòng lặp Eq. 4/8; so với `cl_forward` 6,0e-15 (w biểu diễn đúng trong float32) và 1,4e-9 (w = log 0,5, log 2; nguyên nhân: `cl_forward` dựng ma trận trọng số bằng float32, dựng bằng float64 thì còn 7,1e-15). Gradient khớp < 1e-6 trên một batch (N=8, d=32, τ=0,05, w ∈ {0, log 2}). float32: 3,7e-6, ngưỡng riêng 5e-5 | `experiments/reproduction/results/R4/`, `tests/test_infonce.py` |
| Dense D1-dev (Phase 2) | [x] | 224 câu, Hit@1 46,43%, Hit@3 65,63%, MRR@10 58,28% | [Kết quả và cấu hình](../../experiments/external_dataset/results/D1-dev/metrics.json) |
| Chọn cấu hình D1-dev | [x] 25/11 | λ = 0,6 đạt Hit@1 69,64%, Hit@3 85,27%, MRR@10 0,782898. Ngưỡng 0,6201629042625427 giữ 180/224 câu tin cậy (80,36%) | [Cấu hình](../../experiments/external_dataset/results/D1-dev-tuning/handoff.md) · [Kết quả quét](../../experiments/external_dataset/results/D1-dev-tuning/summary.json) |
| E0 | Đã kiểm 25/11 | Chỉ số BM25 trên 224 câu D1-dev tính lại khớp, điểm từng chunk và top 20 đoạn nguồn của câu 9542 khớp tính toán độc lập | [Kiểm chứng BM25](../../experiments/external_dataset/results/E0/d1-dev.md) |
| E1 | Đã chạy ba phương pháp 25/11 | Hybrid đạt MRR@10 0,810780. Chênh lệch Hybrid − BM25 là +0,018988 (95% CI [+0,008363, +0,029811]) và +2,11 điểm phần trăm Hit@1 (95% CI [+0,39, +3,82]). Đối chứng PhoBERT thô là phần khuyến nghị | [Kết quả D1-test](../../experiments/external_dataset/results/E1/d1-test.md) |
| E2 D1-test | 25/11 | Nhóm Jaccard thấp có 253 câu. Hybrid tăng MRR@10 thêm 0,042031 so với BM25 (95% CI 0,018749 đến 0,065467) | [Bảng chỉ số và khoảng tin cậy](../../experiments/application/results/E2/d1-test.md) |
| E2 D2-test | 26/11 | Trên 86 câu, MRR@10 theo Điều của Hybrid là 0,8750 và BM25 là 0,8396. Chênh lệch 0,0354 (95% CI 0,0058 đến 0,0717). Hybrid đạt MRR@10 theo chủ đề 0,8895 và Clause@1 68,60% | [Bảng theo Điều, chủ đề, Khoản và mức trùng từ](../../experiments/application/results/D2/d2-test.md) |
| E3 D1-test | 25/11 | Ngưỡng đã chốt cho độ bao phủ 81,42% (618/759) và risk 23,95% (148/618). Risk tại độ bao phủ 100% là 27,54% (209/759) | [Biểu đồ](../../experiments/external_dataset/results/E3/d1-test-risk-coverage.png) · [Dữ liệu đường cong](../../experiments/external_dataset/results/E3/d1-test.json) · [Chỉ số cảnh báo](../../experiments/external_dataset/results/E1/d1-test.md#cảnh-báo-của-hybrid) |
| E3 D2-test | 26/11 | Cùng ngưỡng D1-dev, độ bao phủ 66,98% (71/106), risk theo Điều 17,65% (12/68) và theo chủ đề 16,18% (11/68). Có 3/20 câu ngoài phạm vi được đánh dấu tin cậy (15,00%) | [Chỉ số cảnh báo và mã câu](../../experiments/application/results/D2/d2-test.md#hybrid-warnings) · [Biểu đồ](../../experiments/application/results/D2/risk-coverage.png) |
| Kiểm giao diện | 26/11 | So hai phiên bản giao diện trên 10 câu với cấu hình demo cố định. Tab chính giữ cùng các căn cứ, tab từ khóa bỏ ba chủ đề không có tín hiệu ở câu chứa chuỗi lạ | [Đầu ra trước và sau](../../experiments/application/results/ui-review/search-behavior.json) · [Checklist trải nghiệm](../reviews/workspace.md#trải-nghiệm-sinh-viên-và-tài-liệu) |
| E4 | Hoàn tất 26/11 | Độ trễ truy hồi CPU của ba phương pháp, 60 mẫu mỗi phương pháp | [Bảng E4](../../experiments/application/results/E4/cpu-latency.md) |
| E5 D1-test | Hoàn tất 26/11 | Hybrid trượt Hit@1 ở 209/759 câu, 123 trong số đó có đoạn chuẩn hạng 2–3. Đối chiếu 20 ca lỗi và 2 ca xếp đúng, khớp 66/66 ô thứ hạng với ba tệp gốc | [Phân tích D1-test](../../experiments/application/results/E5/d1-test.md) |
| E5 D2-test | Hoàn tất 26/11 | Hybrid trượt hạng 1 ở 18/86 câu theo Điều và 17/86 theo chủ đề. Đã đọc 5 ca trượt hạng 1 theo Điều và cả 3 ca ngoài phạm vi bị đánh dấu tin cậy | [Phân tích D2-test](../../experiments/application/results/E5/d2-test.md) |
| Bộ phát triển mở HCMUS | 26/11, ngoài D1/D2-test | Cả bốn bản đúng Khoản 7/8, tự tin sai 1/6 câu gần và 0/2 câu ngoài lĩnh vực. K+G so với A giảm độ bao phủ từ 5/8 xuống 2/8, số căn cứ nhìn thấy ngay từ 3/8 xuống 2/8 | [Từng câu và kết luận](../../experiments/application/results/clause-scope-pilot/comparison.md) |
| Cách mở phiên bản | 26/11, cùng bộ phát triển mở | Căn cứ đúng xuất hiện ngay ở 3/8 câu có đáp án của A và 5/8 câu khi ưu tiên năm được hỏi. Hai câu được lợi đều yêu cầu quy chế 2021 | [Kết quả theo nhóm năm](../../experiments/application/results/edition-display-pilot/comparison.md) |
| Thời điểm hỏi khóa | 26/11, diễn tập ngoại tuyến | Hai mẫu cùng hiện đúng căn cứ trong ba nhiệm vụ. Tra chung mất 4 thao tác ở A, 2 ở B. Liên kết mở đúng trang PDF tăng từ 4/6 lên 6/6 sau sửa | [Phiếu từng lượt và phạm vi mô phỏng](../../experiments/application/results/cohort-walkthrough/comparison.md) |

---

## 7. Development Plan & Team Workflow

Phân công chi tiết và checklist nằm ở **[docs/PLAN.md](../PLAN.md)**, nguồn duy nhất về ai làm gì. Mục này chỉ giữ lịch, phụ thuộc và cách làm việc.

### 7.1 Cách làm việc

- Một repo GitHub chung. Mỗi người làm trên branch riêng (`huy/...`, `minh/...`) và merge vào `main` khi chạy được; người kia xem lướt trước khi merge.
- Xong việc nào thì người phụ trách tick trong PLAN.md và cập nhật [§1](#1-current-status).
- Mỗi mục trong PLAN.md có **một người chủ trì**; người còn lại hỗ trợ hoặc kiểm tra chéo.

### 7.2 Lịch theo PLAN.md

Các mốc dưới đây là hạn kế hoạch. Nhóm đặt mục tiêu nộp trước **20:00 ngày 11/12/2026**; hạn chính thức là **23:59** cùng ngày. [Tiến độ thực tế](../PLAN.md#phase-4--hoàn-thiện-và-nộp-bài)

| Phase (PLAN.md) | Hạn | Đầu ra chính | Phụ thuộc |
|---|---|---|---|
| 1 – Nghiên cứu paper | 27/11 | Hai phần viết đã đọc chéo. Huy: bài toán và phương pháp; Minh: dữ liệu, baseline, metric, kết quả, hạn chế | — |
| 2 – Triển khai và tái hiện | 30/11 | **Huy:** R1 ✓ (thêm R2, R3 ✓), R4 InfoNCE + test ✓, giải thích luồng code. **Minh:** D1 + group split ✓, SimCSE-VN dense trên D1-dev ✓ (Hit@1/3, MRR@10, top-20). Bảng D1-test thuộc E1 sau khi chốt cấu hình | D1 có sẵn |
| 3 – Xây dựng ứng dụng | 06/12 | **Minh:** corpus HCMUS từ `data/d2/` (tách Điều/Khoản, metadata), BM25 + Hybrid, Gradio, latency. **Huy:** bảng so sánh + CI, chọn λ/θ trên D1-dev, so sánh trên D1-test và D2 (chung và theo mức trùng từ), phân tích lỗi. **Cả hai:** đã [chốt nhãn D2](../../data/d2/README.md#câu-hỏi-và-nhãn-d2-đã-chốt) trước hạn 02/12 | Phase 2; việc chuẩn bị câu D2 chỉ cần bảng đối ứng đã duyệt |
| 4 – Hoàn thiện và nộp | 10/12, nộp 11/12 | Báo cáo IEEE, video Minh quay, kiểm và đóng gói. [Phân công hiện tại](../PLAN.md#phase-4--hoàn-thiện-và-nộp-bài) | Phase 3 |
| Tùy chọn O1–O5 | dừng 08/12 | Chỉ làm nếu Phase 3 xong trước 06/12 | Phase 3 |

**Ràng buộc thứ tự**
- `article_map.tsv` duyệt xong **trước** khi gán nhãn D2.
- Nhãn D2 phải chốt **trước** khi xem dự đoán trên D2.
- λ và θ phải cố định trên D1-dev **trước** khi chạy D1-test và D2.
- Demo và video chỉ dùng cấu hình đã đánh giá.

---

## 8. Risks, Decisions & Definition of Done

### 8.1 Rủi ro và dự phòng

| Rủi ro | Mức | Dự phòng |
|---|---|---|
| Môi trường tái hiện (transformers 4.2.1/torch 1.7.1 không cài được; SentEval lỗi với numpy ≥ 1.24) | Đã xử lý | Venv Python 3.11 với các bản pin ở D-12; sai lệch phiên bản ghi trong `env.txt` và báo cáo |
| Chậm video hoặc gói nộp | Cao | Ưu tiên các đầu việc còn mở trong [PLAN](../PLAN.md#phase-4--hoàn-thiện-và-nộp-bài) và lịch ở §7.2 |
| Tái lập tách từ PyVi trên môi trường mới | Đã kiểm trên cấu hình đã đo | Dùng phiên bản và checksum trong [kết quả D2](../../experiments/application/results/D2/summary.json) khi đối chiếu lượt đã công bố |
| Không có GPU / hết quota | Thấp với MVP | MVP và R1 chạy CPU; GPU chỉ cần cho O1, O3 (Kaggle/Colab) |
| SimCSE-VN truy hồi kém, hybrid không thắng BM25 | Cao | Kết quả âm vẫn hợp lệ: phân tích theo mức trùng từ vựng (E2) và lỗi (E5); đóng góp vẫn gồm trích dẫn, phiên bản, cảnh báo được đánh giá; cân nhắc O1 |
| License D1 không rõ hoặc repo ViRE bị gỡ | Trung bình | Link nộp là permalink theo commit (không đổi được nội dung); lưu bản sao riêng để chạy lại; dự phòng EduCoQA; D2 vẫn là dataset mới của nhóm |
| Bản chép QĐ 3087/2026 (ChatGPT chép từ scan) khác bản gốc | Trung bình | Sau hai lượt sửa OCR vẫn phát hiện sai ngưỡng buộc thôi học và quy định về hội đồng. Chuẩn bị bản hiệu đính theo [hướng dẫn D2](../../data/d2/README.md#file), đối chiếu căn cứ dùng cho nhãn với PDF đã ký và cho mở bản chính thức ngay tại trích đoạn |
| Người đọc nhầm bản ChatGPT chép QĐ 3087 với bản gốc | Trung bình | Chia sẻ liên kết PDF chính thức của Trường trong metadata D2. Bản chép dùng cho lập chỉ mục và nộp trong `[Group14].zip` theo D-18 |
| Corpus D2 nhỏ (51 Điều, 26 chủ đề) làm Hit@3 cao với mọi phương pháp | Trung bình | Báo cả mức theo Điều (chặt) và theo chủ đề, kèm Clause@1 và mức ngẫu nhiên (§6.3); trong báo cáo nêu rõ quy mô corpus và việc mức chủ đề dễ hơn mức Điều |
| Câu D2 do nhóm viết thiên lệch: người viết đã đọc văn bản nên câu có thể ít trùng từ hơn câu hỏi thật, bất lợi cho BM25 | Trung bình | Viết kiểu gập sách (D-18); nêu rõ trong báo cáo; báo E2 theo mức trùng từ cả trên D2; nếu có câu từ Google Form (`origin: form`) thì báo riêng nhóm này |
| Regex tách Điều/Khoản sai do định dạng khác nhau | Trung bình | Test trên cả ba nguồn: QĐ 1175 (chữ trích từ PDF bằng pdftotext), QĐ 3087 (Markdown) và D1. Kiểm tra số Điều: 24 và 27 |
| Nhãn D2 không nhất quán | Trung bình | Kiểm tra chéo, ghi tỉ lệ đồng ý, có log bất đồng |
| Tách từ không nhất quán giữa index và query | Trung bình | Một hàm `preprocess` dùng chung + unit test |
| Link nộp bài không truy cập được (−50%) | Cao | Kiểm tra mọi link ở chế độ ẩn danh trước khi nộp (Phase 4, Minh) |

### 8.2 Các nội dung đã điều chỉnh so với Research

- **D1 truy cập được ngay:** bản con ViRHE4QA có sẵn trong repo ViRE, không cần chờ xin bộ đầy đủ.
- **Thu gọn khối lượng:** D2 giảm từ 150–300 câu xuống 80–100 câu + 20 câu ngoài phạm vi, rồi bỏ ngày 23/11 (D-16) và khôi phục cùng ngày với corpus quy chế đào tạo HCMUS (D-17). Cohen's κ và fine-tuning chuyển sang tùy chọn. D-33 chốt phần kiểm giao diện bằng mô phỏng ngoại tuyến. Baseline bắt buộc chỉ còn BM25 / SimCSE-VN / Hybrid.
- **Sửa thông tin code:** tại commit cố định không có `--mlp_only_train` (Research mô tả theo bản fork hoặc `main`). Thêm các khác biệt eval_steps 125/250 và 81,58/81,57.
- **Số liệu R2GQA:** chỉ giữ những số đã đối chiếu được. Một số con số Research nêu (vd. ViSimCSE P@1 43,24, ensemble 72,13) chưa xác minh nên **không dùng**.
- **Confidence:** dùng cosine tuyệt đối, không dùng điểm fused đã min-max. Dạng cảnh báo thay vì từ chối cứng.
- **Bonus:** bỏ hẳn, vì giảng viên xác nhận không xét. O1 chỉ còn là thí nghiệm tùy chọn cho ứng dụng.

### 8.3 Decision log

| ID | Quyết định | Trạng thái |
|---|---|---|
| D-01 | Option 1; ứng dụng tra cứu quy chế học vụ; không chuyển sang Option 2 | Chốt |
| D-02 | Encoder: `VoVanPhuc/sup-SimCSE-VietNamese-phobert-base` + pyvi + `pooler_output`, max_len 256 | Chốt cho MVP |
| D-03 | Hybrid λ-fusion trên điểm min-max theo Điều; λ chọn trên D1-dev | Chốt |
| D-04 | Chunk theo Khoản (≤ 256 token, chia cửa sổ nếu dài); xếp hạng và đánh giá theo Điều (MaxP) | Chốt |
| D-05 | Trả về đoạn văn có trong corpus kèm nguồn, không dùng LLM sinh câu trả lời. Ban đầu ghi công bản chép ngay trong kết quả | Phần ghi công khi hiển thị bị thay bởi D-27 |
| D-06 | Confidence là cosine SimCSE của chunk đã chọn trong Điều đứng đầu. Dùng θ từ D1-dev để cảnh báo | Chốt quy tắc đo. Giá trị θ ở D-22 |
| D-07 | D1 = ViRHE4QA (ViRE @ `60ea715`) là dataset mới chính; D2 chỉ test | Chốt (D2 khôi phục theo D-17) |
| D-08 | Tái hiện = R1 (bắt buộc) + R4; R2, R3 khuyến nghị; train SimCSE là tùy chọn | Chốt |
| D-09 | Gradio, chạy local; không server, database hay auth | Chốt |
| D-10 | FAISS `IndexFlatIP`, fallback NumPy | Bị thay bởi D-24 (25/11) |
| D-11 | Fine-tuning (O1) chỉ sau MVP; không nhắm bonus | Chốt |
| D-12 | Môi trường tái hiện: venv Python 3.11 + `experiments/reproduction/requirements-r1.txt` (numpy 1.23.5, scipy 1.10.1, scikit-learn 1.2.2, torch 2.5.1 CPU, transformers 4.46.3); chạy qua `experiments/reproduction/run_r1.py` | Chốt |
| D-13 | Dataset nộp bằng link: D1 = permalink ViRE @ `60ea715`; D2 = Google Drive public | Chốt (giảng viên cho phép); nội dung link D2 theo D-18 |
| D-14 | Phân công theo `docs/PLAN.md`; PROJECT.md chỉ giữ lịch và phụ thuộc | Chốt (23/11) |
| D-15 | Cấu trúc code theo repo `UniSearch-SimCSE` (package `simcse_lab`, thư mục `experiments/`) | Chốt (23/11) |
| D-16 | Bỏ D2. Chỉ đánh giá trên D1; corpus của ứng dụng là 297 đoạn quy chế ĐH CNTT trong D1, không dùng quy chế trường khác. Ứng dụng hiển thị số và tên Điều, không hiển thị văn bản gốc hay phiên bản vì D1 không có thông tin này. Không đo cảnh báo với câu ngoài phạm vi | Bị thay bởi D-17 (23/11). Phần giới hạn nguồn bị thay bởi D-35. D1 chia theo nhóm đoạn, nhóm câu 9542 ghim vào dev; cột `split` gốc của D1 bị rò rỉ |
| D-17 | Khôi phục D2. Corpus của ứng dụng và của D2 là quy chế đào tạo HCMUS: QĐ 1175/QĐ-KHTN (2021, 24 Điều, nguyên văn) và QĐ 3087/QĐ-KHTN (29/9/2026, 27 Điều, bản ChatGPT chép từ scan, nhóm làm sạch). Giữ cả hai phiên bản vì Điều 27 quy chế 2026 ghi: với các khóa tuyển sinh từ năm 2025 trở về trước, Trường lựa chọn áp dụng quy định mới có lợi hơn cho người học. Không dùng bản trích lược trong Sổ tay. D1 giữ vai trò đánh giá trên corpus riêng. Toàn văn để ngoài Git cho tới khi rõ Q7 | Chốt (23/11, Huy); phần toàn văn, hiển thị và cách viết câu được cụ thể hóa ở D-18. Giới hạn D1 ở phần đánh giá bị thay bởi D-34 |
| D-18 | Chốt bốn điểm còn mở của D-17 và thứ tự hiển thị. (1) Duyệt `data/d2/article_map.tsv` sau khi đối chiếu nội dung; giữ T02/T09/T16. (2) Câu D2 viết kiểu gập sách, được dùng thuật ngữ thông dụng, không chép nguyên câu hay mệnh đề; bỏ quy tắc "không chép quá 3 từ liên tiếp". (3) Chữ QĐ 1175 (văn bản công khai) đưa vào Git ở `data/d2/`, giữ nguyên byte (`.gitattributes`) để sha256 khớp. (4) Bản chép QĐ 3087 không đăng công khai cho tới khi trường đăng bản chính thức hoặc Phòng Đào tạo đồng ý; nộp kèm trong `[Group14].zip`. (5) Trong mỗi kết quả, bản 2026 hiển thị trước, bản 2021 là phụ | Chốt (24/11; Huy chọn ưu tiên bản 2026 và giao Claude quyết bốn điểm còn lại). Thứ tự hiển thị theo khóa bị thay bởi D-36 |
| D-19 | Dùng ngay định dạng ở [§5.4](#54-interface--định-dạng-dữ-liệu). Mỗi người viết Related Work theo phần phụ trách trong [PLAN.md](../PLAN.md#phase-1--nghiên-cứu-paper) | Áp dụng từ 24/11 |
| D-20 | E0 dùng D1-dev. Bổ sung cho D-19: D2 lưu đủ thứ hạng theo Điều để tính đúng MRR@10 sau khi gộp chủ đề (§6.3). D1 lưu top-20 | Chốt 24/11 khi rà soát |
| D-21 | Bổ sung D-06 và D-19: cố định cách chọn đoạn trích khi hai phương pháp chọn hai chunk khác nhau và cách xử lý đồng điểm ở [§5.2](#52-vai-trò-từng-thành-phần-proposed). Căn cứ Clause@1 và cảnh báo dùng cùng một đoạn | 24/11, trước khi có xếp hạng D1/D2 |
| D-22 | Cố định trọng số Hybrid tối ưu MRR@10 và ngưỡng lớn nhất giữ coverage ≥ 80% trên D1-dev. Nếu MRR@10 bằng nhau trong lưới, chọn trọng số BM25 nhỏ hơn. Giá trị và lệnh chạy nằm trong [cấu hình D1-dev](../../experiments/external_dataset/results/D1-dev-tuning/handoff.md) | Chốt 25/11, trước khi đánh giá D1-test và D2 |
| D-23 | E2 trên D1-test dùng Jaccard của tập token Pyvi giữa câu hỏi và toàn đoạn chuẩn. Hai mốc phân nhóm lấy theo phân vị 1/3 và 2/3 của Jaccard. [Quy tắc phân nhóm và kết quả](../../experiments/application/results/E2/d1-test.md#cách-chia-nhóm) | Áp dụng cho lượt D1-test ngày 25/11 |
| D-24 | Truy hồi dense và demo dùng tích vô hướng NumPy trên toàn bộ vector chuẩn hóa L2. Đặc tả theo mã và kết quả đã chạy | Ghi nhận 25/11. Thay D-10 cho ứng dụng |
| D-25 | D2 phân biệt các Khoản lặp số bằng thứ tự xuất hiện trong nguồn. Với nhiều Điều gold, E2 dùng Jaccard cao nhất và để các câu đồng điểm cùng nhóm. E3 dùng riêng tỷ lệ sai ở hạng 1 theo Điều và theo chủ đề | Chốt quy tắc triển khai 25/11, trước khi chấm D2 |
| D-26 | Dùng [bộ nhãn D2 đã thống nhất](../../data/d2/README.md#câu-hỏi-và-nhãn-d2-đã-chốt) cho lượt đánh giá chính thức. Mã SHA-256 nhận diện bản này nằm trong [metadata](../../data/d2/documents.yaml) | Chốt 26/11, Huy xác nhận phiếu phản hồi của Minh trước khi chạy đánh giá |
| D-27 | Trong kết quả tra cứu, dành chỗ cho trích đoạn, căn cứ áp dụng và liên kết PDF chính thức. Ghi công bản ChatGPT chép từ scan và phần hiệu đính của nhóm trong hồ sơ dữ liệu, hướng dẫn demo và báo cáo | 26/11, theo yêu cầu của Huy về đầu ra cho sinh viên. Thay phần hiển thị ghi công ở D-05 |
| D-28 | Giao diện chỉ hiện kết quả cho câu đang hỏi. Tab từ khóa hiển thị các chủ đề có tín hiệu BM25, cảnh báo cosine nằm ở tab tra cứu. Ghi rõ bảng gốc năm 2021 đã sửa đổi ngay tại bảng | 26/11, sau khi thử hành trình sinh viên. Bổ sung D-06 và D-27 cho phần hiển thị. [Checklist](../reviews/workspace.md#trải-nghiệm-sinh-viên-và-tài-liệu) |
| D-29 | Mọi đề xuất thay bản vì lỗi chọn Khoản và tự tin sai phạm vi phải so với Hybrid đã công bố trên một bộ phát triển HCMUS mới có phần xác nhận giữ kín. [Thiết kế so sánh và tiêu chí thay bản](../../experiments/application/clause-scope-comparison.md) | 26/11, thiết kế thử nghiệm. Bản đang phục vụ vẫn dùng D-06, D-21 và D-22 |
| D-30 | Tiếp tục dùng Hybrid hiện tại sau phép thử bộ mở. K+G còn giữ nguyên ca tự tin sai và thu gọn thêm ba kết quả có đáp án. [Đối chiếu ghép cặp](../../experiments/application/results/clause-scope-pilot/comparison.md) | 26/11, áp dụng D-29 trên dữ liệu phát triển. Giai đoạn xác nhận giữ kín chưa chạy |
| D-31 | Thử ưu tiên phiên bản sinh viên yêu cầu ở lớp hiển thị, dùng lại xếp hạng và cảnh báo của D-30. Thời điểm hỏi khóa được thử riêng ở D-32. [Bằng chứng ngoại tuyến](../../experiments/application/results/edition-display-pilot/comparison.md) | 26/11, thí nghiệm phát triển. Bản demo tiếp tục dùng D-18 |
| D-32 | So thời điểm hỏi khóa bằng hai mẫu có chung dữ liệu và căn cứ cho K24, K26 và tra cứu chung. [Thiết kế và bộ thử](../../experiments/application/README.md#mô-phỏng-hai-cách-chọn-khóa) | 26/11, [đã chạy sáu lượt mô phỏng](../../experiments/application/results/cohort-walkthrough/comparison.md). Phần dự kiến quan sát sinh viên bị thay bởi D-33 |
| D-33 | Kết thúc phép so chọn khóa ở kết quả Chrome ngoại tuyến và bỏ việc thu phản hồi sinh viên. Minh quay video chính thức từ slide và ảnh đã bàn giao. Codex kiểm và đóng gói khi có bản ghi | 26/11, theo quyết định của Huy. [Hồ sơ video](../README.md#báo-cáo-và-video) |
| D-34 | HCMUS là nguồn mặc định của demo cục bộ. Khi có corpus ViRHE4QA, người dùng có thể tra cứu D1 trong tab riêng. Mỗi nguồn có chỉ mục riêng. [Cách mở và đọc đoạn nguồn](../../apps/README.md#tra-cứu-virhe4qa) | Chốt 27/11 theo yêu cầu của Huy, bổ sung D-17 về phạm vi demo |
| D-35 | Mỗi đoạn D1 dẫn về tên văn bản và dòng trong bộ tác giả R2GQA. Chỉ thêm liên kết PDF UIT khi đối chiếu được nội dung và trang. Bảng nguồn chỉ dùng sau xếp hạng. [Căn cứ và cách kiểm](../../data/README.md#nguồn-văn-bản-d1) | Chốt 27/11 theo yêu cầu của Huy, bổ sung D-34 và thay giới hạn nguồn D1 ở D-16 |
| D-36 | Chọn khóa HCMUS hoặc hệ UIT trước khi hỏi. Cho phép chọn Tra cứu chung. Tên văn bản của tác giả là căn cứ lọc theo hệ UIT. [Cách dùng](../../apps/README.md) | Chốt 27/11 theo yêu cầu của Huy |
| D-37 | Với câu hỏi chung về điều kiện tốt nghiệp HCMUS, ưu tiên Điều chứa danh sách điều kiện xác định duy nhất trong từng văn bản và mở khoản đó trực tiếp. Các câu hỏi chuyên biệt và trường hợp thiếu căn cứ dùng cách tra thông thường. | 27/11, bổ sung D-36 theo yêu cầu của Huy |
| D-38 | Cho mở lời giải thích trên từng đoạn của hai nguồn. Kết quả thông thường hiển thị cosine của đoạn, làm tròn hai chữ số. Kết quả trực tiếp theo D-37 nêu khoản và lý do chọn bản quy chế. | 27/11, bổ sung D-06 và D-37 theo yêu cầu của Huy |
| D-39 | Hiện phương pháp và điểm xếp hạng thật bên cạnh số hạng ở HCMUS và UIT. Với khoản tốt nghiệp ưu tiên theo khóa, hiện **Chọn theo khóa**. Chế độ tra cứu chung ghi căn cứ chọn theo điều kiện tốt nghiệp. | 27/11, bổ sung D-38 theo yêu cầu của Huy |
| D-40 | Với kết quả UIT chỉ khớp tiêu đề, ghi rõ đối tượng được chấm và mở đoạn nguồn nếu thẻ đầu tự mở. Ghi rõ hai liên kết bản lưu PDF và cách tìm lại dòng trong bảng tính của tác giả. | 27/11, Codex bổ sung cách đọc theo D-35 và D-38 sau [lượt rà soát](../reviews/workspace.md#kiểm-tra-ngày-27112026) |

**Giới hạn dữ liệu.** Ý nghĩa của cột `label` trong D1 vẫn chưa được xác minh. Các phép chấm dùng đoạn nguồn chuẩn đi kèm từng câu hỏi. [Mô tả bộ dữ liệu](#61-datasets)

Q5 đã có cấu hình thực chạy với Pyvi và NumPy trong [kết quả D1-dev](../../experiments/external_dataset/results/D1-dev-tuning/summary.json) (D-24).

Q7 đã có nguồn chính thức (24/11). Chia sẻ [PDF của Trường](https://www.hcmus.edu.vn/wp-content/uploads/2026/10/QD3087_QD-Quy-che-dao-tao-2026.pdf). Bản ChatGPT chép từ scan vẫn dùng cho corpus trong bài nộp.

Đã giải quyết (23/11): không xét bonus; Group ID = 14; deadline 23:59 ngày 11/12/2026; dataset được nộp bằng link; không cần xin phép giảng viên để dùng dataset; Q2 (chọn văn bản quy chế của trường) đóng: QĐ 1175/2021 và QĐ 3087/2026 (D-17).

### 8.4 Definition of Done

**Code**
- Chạy từ clone sạch theo README.
- Phiên bản thư viện và checkpoint đã dùng được ghi trong manifest thí nghiệm. Trọng số và ngưỡng lấy từ [cấu hình D1-dev](../../experiments/external_dataset/results/D1-dev-tuning/summary.json).
- Test cho chunker, chuẩn hóa, metrics và InfoNCE đều pass. Có test kiểm số Điều của corpus D2 (24 và 27) và sha256 văn bản theo `documents.yaml`.
- Seed được ghi lại.

**Ứng dụng**
- Nhận câu hỏi tiếng Việt tự do và hiển thị tối đa ba chủ đề, kèm Điều/Khoản, trích đoạn, tên văn bản, số hiệu, ngày ban hành và phạm vi áp dụng.
- Có nhãn cảnh báo, chế độ so sánh BM25 và dòng nhắc tham khảo.
- Chạy trên CPU; latency đã đo.

**Thí nghiệm**
- R1, R4, E0–E5 có file trong `results/` của thư mục `experiments/` tương ứng.
- Bảng có CI.
- Có các câu ghi rõ phần nào không so sánh trực tiếp được.
- Có ≥ 20 ca lỗi được phân loại.

**Báo cáo IEEE** (PDF)
- Đủ các mục Abstract, Introduction, Related Work, Proposed Model/Method, Experimental Setup, Results and Discussion/Application, Conclusion, References.
- Phủ 6 mục phân tích của đề (3.2).
- Có bảng tách bạch phần tái sử dụng và phần mới (§2.6); có hạn chế và điều kiện thất bại.

**Video** dài tối đa 30 phút theo đề. Tư liệu cho Minh gồm phần phương pháp, luồng truy hồi, kết quả tái hiện, thao tác thật trên Hybrid và BM25, đánh giá D1/D2 và một trường hợp cảnh báo bỏ sót. [Slide và ảnh dùng khi quay](../README.md#báo-cáo-và-video)

**Nộp bài** (trước 23:59 ngày 11/12/2026, mục tiêu trước 20:00)
- `[Group14].zip` gồm code hoặc link GitHub, video, PDF.
- Link dataset (D1 permalink ViRE, D2 Google Drive) và link code đã kiểm tra ở chế độ ẩn danh.
- Giữ [thư mục D2 công khai trên Drive](../../data/d2/README.md#bộ-d2-công-khai) truy cập được ít nhất 2 năm. Kèm bản ChatGPT chép QĐ 3087 từ scan, đã được nhóm hiệu đính, trong `[Group14].zip` theo D-18.

### 8.5 References

- Gao, Yao, Chen. *SimCSE: Simple Contrastive Learning of Sentence Embeddings.* EMNLP 2021, pp. 6894–6910 — <https://aclanthology.org/2021.emnlp-main.552/>
- SimCSE code @ commit cố định — <https://github.com/princeton-nlp/SimCSE/tree/235f89e0244b23673b69fbbc4a1cd9868c5a5c24>
- SimCSE-VN checkpoint — <https://huggingface.co/VoVanPhuc/sup-SimCSE-VietNamese-phobert-base>
- PhoBERT — <https://github.com/VinAIResearch/PhoBERT>
- ViRE benchmark (chứa ViRHE4QA_v2, EduCoQA) — <https://github.com/longstnguyen/ViRE/tree/60ea7155134eaa426ab1d0a82d2bbbf327d1b470>
- R2GQA / ViRHE4QA — <https://arxiv.org/abs/2409.02840>
- EduCoQA (HF) — <https://huggingface.co/datasets/longstnguyen/vire-educoqa>
- Thư viện: rank_bm25 <https://github.com/dorianbrown/rank_bm25> · NumPy <https://numpy.org/> · pyvi <https://github.com/trungtv/pyvi> · Gradio <https://www.gradio.app/>
- Mẫu IEEE Conference (`conference_101719.tex`, IEEEtran V1.8b) — <https://www.overleaf.com/latex/templates/ieee-conference-template/grfzhhncsfqn>. Build trên máy, không qua Overleaf: [docs/report/](../report/README.md).
