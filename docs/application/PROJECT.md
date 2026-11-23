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

**Nhóm 14** · **Deadline: 23:59 ngày 11/12/2026** · Cập nhật lần cuối: 2026-11-24 (Huy)

**Repo GitHub:** <https://github.com/AIVIETNAM-AIO-Heart208/UniSearch-SimCSE>. Minh tạo ngày 23/11.

**Bản clone trên laptop Huy:** `D:\TAI_LIEU_HCMUS_K24\Năm 3 - Kì 1\Nhập môn học máy\Project-ML_Lab\Lab03\UniSearch-SimCSE`. Script, log và kết quả R1–R4 đã có trên nhánh `main` của nhóm trong `experiments/reproduction/`. R4 có thêm `src/simcse_lab/model/infonce.py` và `tests/`. R1–R3: [commit `622dc22`](https://github.com/AIVIETNAM-AIO-Heart208/UniSearch-SimCSE/commit/622dc223cd3ef43aeffab5d0ff1da230d8a3b641).

Thư mục cũ `D:\Lab03_Group14` chỉ còn giữ venv và bản gốc của lần chạy R1–R3; xóa được khi không cần nữa.

**Giai đoạn hiện tại:** Phase 1 (đọc paper) và Phase 2 (tái hiện: R1–R4 đã xong) theo [docs/PLAN.md](../PLAN.md). Chưa có code ứng dụng.

**Đã hoàn thành**

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
  - Kiểm thử: 689/689 test pass. Ở float64, lệch ≤ 1,4e-9 so với `cl_forward` và ≤ 8,4e-15 so với vòng lặp tính theo Eq. 4/8.
  - File: `experiments/reproduction/results/R4/` ([§6.7](#67-bảng-theo-dõi-kết-quả)).
- [x] Bản nháp phần Introduction và Proposed Method của báo cáo IEEE (commit `652fa4e`), gồm cả phần giải thích luồng code gốc. Chưa đọc chéo.
  - Bổ sung ngày 23/11 cho phần Phase 1 của Huy:
    - đoạn so sánh SimCSE với các cách làm trước (post-processing, các phương pháp contrastive khác, SBERT);
    - §Worked Example: ví dụ tính loss cho cả hai cách huấn luyện, dùng câu của Figure 1 và cosine minh hoạ, kiểm bằng `tests/test_worked_example.py`;
    - ví dụ lexical gap thật trong Introduction: câu D1 index 9542 ("bị dừng giữa chừng" và "đình chỉ" trong Điều 6). Nhóm đoạn của câu này phải vào D1-dev ([§6.2](#62-tiền-xử-lý-gán-nhãn-và-chia-dữ-liệu)).
- [x] **Corpus D2 (23/11, D-17):** quy chế đào tạo của Trường ĐH KHTN, gồm hai văn bản.
  - QĐ 1175/QĐ-KHTN (2021): 24 Điều, PDF có lớp chữ, công khai.
  - QĐ 3087/QĐ-KHTN ngày 29/9/2026: 27 Điều. ChatGPT chép từ bản scan; nhóm làm sạch 158 lỗi OCR có kiểm chứng.
  - Mô tả và metadata ở [`data/d2/`](../../data/d2/README.md). Chữ QĐ 1175 (văn bản công khai) có trong Git ở `data/d2/`; bản chép QĐ 3087 chỉ ở `data/raw/d2/`, không đăng công khai (D-18).
  - Bảng đối ứng Điều 2021 ↔ 2026 (`data/d2/article_map.tsv`, 26 chủ đề): đã duyệt ngày 24/11 sau khi đối chiếu nội dung (D-18).
  - Rà soát lại ngày 24/11: sha256 khớp, URL công khai của QĐ 1175 vẫn tải được, hai đoạn có độ giống thấp của bản chép 2026 đã đọc tay đối chiếu.

**Đang thực hiện:** không có.

**Chưa thực hiện:** phần còn lại của Phase 2–4 ([§7.2](#72-lịch-theo-planmd)).

**Blocker / chờ quyết định**

- Chưa chia phần viết Related Work (mục 3.2.2, giao cho cả Huy và Minh) trong `docs/report/sections/related-work.tex`.

**Việc ưu tiên tiếp theo**

1. **Huy:** báo Minh về D-17 và D-18 (đã lên `main` ngày 24/11): bảng đối ứng đã duyệt, quy tắc viết câu D2 mới ([§6.2](#62-tiền-xử-lý-gán-nhãn-và-chia-dữ-liệu)), bản 2026 hiển thị trước. Rà lỗi OCR còn sót trong bản chép QĐ 3087 trước khi Minh dựng index.
2. **Cả hai:** chốt schema dữ liệu ở [§5.4](#54-interface--định-dạng-dữ-liệu) trước 25/11.
3. **Minh** đọc chéo phần bài toán và phương pháp của Huy (Phase 1, hạn 27/11): Introduction và Proposed Method trong `docs/report/sections/`. **Huy** đọc chéo phần của Minh khi Minh xong.
4. **Minh:** chuẩn bị D1 (`data/prepare_virhe4qa.py`, group split) và chạy SimCSE-VN dense trên D1. Khi chia, nhóm đoạn của câu index 9542 phải vào D1-dev ([§6.2](#62-tiền-xử-lý-gán-nhãn-và-chia-dữ-liệu)).
5. **Cả hai:** bắt đầu viết câu hỏi D2 ngay sau bước 1, song song với Phase 2, để kịp chốt nhãn trước 02/12.

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
- **D1** (ViRHE4QA, quy chế ĐH CNTT) chỉ dùng để đánh giá, trên corpus riêng của nó.
- Ứng dụng **không** sinh câu trả lời bằng LLM.

### 2.5 Phạm vi

**MVP (bắt buộc)**

1. Corpus của ứng dụng gồm 2 văn bản trong [`data/d2/documents.yaml`](../../data/d2/documents.yaml): QĐ 1175/2021 (24 Điều) và QĐ 3087/2026 (27 Điều).
   - Tách Điều/Khoản và lưu metadata: văn bản, số hiệu, ngày ban hành, hiệu lực, phạm vi áp dụng.
   - Bản 2026 là bản chép từ scan đã làm sạch, không phải nguyên văn.
   - Khi đánh giá D1, dùng corpus 297 đoạn của D1; corpus này không có metadata văn bản.
2. Ba phương pháp truy hồi chạy trên cùng pipeline: BM25, SimCSE-VN (dense) và Hybrid.
3. Giao diện Gradio gồm:
   - ô nhập câu hỏi;
   - top-3 Điều/Khoản, trích đoạn, tên văn bản, số hiệu và phạm vi áp dụng;
   - nhãn "Độ tin cậy thấp" khi cần;
   - chế độ so sánh song song với BM25.
4. Đánh giá định lượng trên D1 và D2 ([§6](#6-datasets--experimental-evaluation)) và đo latency trên CPU.
5. Tái hiện R1 ([§4.5](#45-kế-hoạch-tái-hiện-kết-quả-paper)) và tự cài lại InfoNCE kèm kiểm thử.

**Nâng cao (tùy chọn, chỉ làm sau khi MVP xong):** O1 domain-adaptive fine-tuning, O2 user study nhỏ, O3–O5 ablation ([§6.6](#66-thí-nghiệm-tùy-chọn)).

**Ngoài phạm vi:** văn bản khác ngoài hai quy chế đào tạo trên, tự xác định phiên bản nào áp dụng cho từng khóa (ứng dụng chỉ hiển thị phạm vi áp dụng ghi trong văn bản), sinh câu trả lời bằng LLM, hội thoại nhiều lượt, OCR tự động trong ứng dụng (bản chép QĐ 3087 được chuẩn bị một lần, ngoài ứng dụng), so sánh khác biệt giữa các phiên bản văn bản, đăng nhập, database server, triển khai cloud, Option 2.

### 2.6 Đóng góp riêng của nhóm

| Tái sử dụng (có trích dẫn) | Nhóm tự phát triển |
|---|---|
| Mã nguồn và checkpoint SimCSE chính thức (tái hiện) | Pipeline tách Điều/Khoản, giữ metadata văn bản, phiên bản và vị trí ký tự để trích đúng đoạn |
| Checkpoint `VoVanPhuc/sup-SimCSE-VietNamese-phobert-base`, PhoBERT | Truy hồi lai, gộp điểm theo Điều, chọn λ trên dev |
| pyvi, rank_bm25, faiss, Gradio | Cơ chế cảnh báo độ tin cậy cùng cách chọn và đánh giá ngưỡng |
| Bộ ViRHE4QA (bản con trong ViRE) | Chia lại D1 theo nhóm đoạn nguồn, vì cột `split` gốc bị rò rỉ (cùng một đoạn có câu hỏi ở cả train và test) |
| Quy chế đào tạo HCMUS (QĐ 1175/2021, QĐ 3087/2026); bản chép QĐ 3087 từ scan do ChatGPT tạo | Bộ test D2: câu hỏi kiểu sinh viên kèm câu ngoài phạm vi. Làm sạch bản chép QĐ 3087 (158 chỗ sửa) và kiểm chứng với OCR của bản scan. Bảng đối ứng Điều 2021 ↔ 2026 |
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
| 3.4.5 | Bằng chứng: metrics, response time, task success, phản hồi có cấu trúc | B | E1–E4 bắt buộc; O2 user study tùy chọn | `results/` | Huy (so sánh), Minh (latency) / 3 |
| 3.4.6 | Thảo luận: tính hữu ích, hạn chế, khi nào thất bại, hướng phát triển | B | E5 phân tích lỗi; [§8.1](#81-rủi-ro-và-dự-phòng) | Báo cáo §Discussion | Huy / 3–4 |
| 4 | Nộp `[Group14].zip` (theo mẫu `[Group01].zip` của đề): code/GitHub + README; video ≤ 30 phút; báo cáo PDF mẫu IEEE | B | [§8.4](#84-definition-of-done) | Bản nộp | Huy (báo cáo), Minh (video, zip) / 4 |
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
| Supervised (Eq. 5) | Dùng NLI (SNLI+MNLI): entailment làm positive, contradiction làm **hard negative**. Table 4: 84,9 → 86,2 khi thêm hard negative. Table 7: trọng số α (Eq. 8, §6.3) bằng 1 là tốt nhất |
| Pooling (Table 6) | Unsup: [CLS] + MLP **chỉ khi train**, bỏ MLP khi test. Sup: [CLS] + MLP |
| Alignment / uniformity (Eq. 2–3) | Alignment: positive pair gần nhau. Uniformity: embedding trải đều trên hypersphere. Unsup SimCSE cải thiện uniformity mà vẫn giữ alignment (Fig. 2–3) |
| Anisotropy (§5) | Embedding của PLM bị dồn vào một "nón" hẹp. Contrastive objective làm phẳng phổ trị riêng → isotropic hơn |
| Đánh giá (§6.1, App. B) | 7 STS task (STS12–16, STS-B, SICK-R). Lấy cosine trực tiếp, **không** dùng regressor. Báo **Spearman**, gộp theo setting "all" |
| Kết quả chính (Table 5) | Trung bình 7 STS, BERT-base: unsup SimCSE **76,25**, sup SimCSE **81,57**. Baseline BERT first-last avg 56,70; SBERT 74,89 |
| Training (App. A) | Unsup: 10⁶ câu Wikipedia, 1 epoch, BERT-base bs 64, lr 3e-5. Sup: SNLI+MNLI (314k), 3 epoch, bs 512, lr 5e-5. Đánh giá STS-B dev mỗi 250 step và giữ checkpoint tốt nhất. Paper dùng GPU 3090, CUDA 11 |

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
| R3 | `bert-base-uncased --pooler avg_first_last` (không fine-tune) | Paper: 56,70 (BERT first-last avg). [Confirmed bằng R3] Số của paper dùng đúng cách tính tại commit, tức `hidden_states[0]` (lớp embedding) và lớp cuối | Khuyến nghị (rẻ) — **đã chạy** | như R1 |
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
  3. Tải `senteval.tar` (cùng URL với script của repo).
  4. Gọi **nguyên bản** `evaluation.py` của repo.
  5. Ghi vào `experiments/reproduction/results/<exp>/`: `eval_log.txt`, `metrics.json` (điểm, chênh lệch so với README/paper, ngưỡng 0,5), `env.txt` (OS, CPU, phiên bản, commit, revision model), `pip_freeze.txt`, `status.txt`.

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
Corpus D1 (chỉ để đánh giá D1): 297 đoạn trong ViRHE4QA_v2.csv, không có metadata văn bản
  → ingest: tách Điều / Khoản → chunk ≤ 256 token → corpus.jsonl
  → preprocess: Unicode NFC → chuẩn hóa dấu thanh (khoá→khóa) → tách từ pyvi
  → BM25 index (token thường hóa)  +  SimCSE-VN embeddings (chuẩn hóa L2) → FAISS IndexFlatIP

[Online – mỗi câu hỏi]
Câu hỏi → preprocess (cùng hàm) → điểm BM25 và cosine cho mọi chunk
  → gộp chunk về Điều (MaxP: lấy max) → min-max normalize theo từng phương pháp
  → Hybrid: s = λ·BM25_norm + (1−λ)·Dense_norm   (λ chọn trên D1-dev)
  → xếp hạng Điều (runs lưu ở mức này, top-20)
  → corpus HCMUS: gộp các Điều cùng chủ đề theo data/d2/article_map.tsv thành một kết quả, bản 2026 đứng trước
  → top-3 kết quả (kèm Khoản / chunk tốt nhất)
  → Confidence: cosine SimCSE của chunk tốt nhất trong Điều đứng đầu < θ  ⇒  cảnh báo "Độ tin cậy thấp"
  → UI: Điều/Khoản · trích đoạn · văn bản · số hiệu · ngày ban hành · phạm vi áp dụng · điểm · [so sánh BM25]
```

### 5.2 Vai trò từng thành phần [Proposed]

| Thành phần | Vai trò | Lý do |
|---|---|---|
| SimCSE-VN | Khớp ngữ nghĩa, xử lý câu hỏi diễn đạt khác văn bản | Thành phần ML chính, gắn trực tiếp với paper |
| BM25 (`rank_bm25`) | Khớp từ khóa, số liệu, thuật ngữ, viết tắt | Đại diện giải pháp hiện có; rất mạnh trên D1 theo tham chiếu ngoài ([§6.1](#61-datasets)) |
| Hybrid λ-fusion | Kết hợp hai loại tín hiệu; chỉ 1 tham số | Đơn giản, chọn trên dev, dễ giải thích |
| FAISS `IndexFlatIP` | Tìm kiếm chính xác (exact) theo inner product trên vector đã chuẩn hóa; cùng cách với `simcse/tool.py` | Nếu cài lỗi, dùng numpy dot product (kết quả giống hệt vì đều exact) |
| Gộp MaxP theo Điều | Điều dài phải chia chunk vì giới hạn 256 token; hiển thị và đánh giá ở mức Điều | Nhãn gold của D1 ở mức Điều |

**Lưu ý:** min-max normalize theo từng câu hỏi làm top-1 luôn gần 1, nên **không** dùng điểm fused làm độ tin cậy. Confidence dùng cosine tuyệt đối của SimCSE-VN.

### 5.3 Metadata, trích dẫn, phiên bản và trường hợp không chắc chắn

- **Corpus HCMUS (ứng dụng, D2):** [`data/d2/documents.yaml`](../../data/d2/documents.yaml), mỗi văn bản một mục.
  - Các trường: `doc_id`, `title`, `so_hieu`, `ngay_ban_hanh`, `hieu_luc`, `trang_thai`, nguồn, `file`, `sha256`, `nguyen_van`.
  - Index **cả hai phiên bản** (2021 và 2026). Lý do: theo Điều 27 quy chế 2026, quy chế mới áp dụng cho khóa tuyển từ năm học 2026–2027; với khóa tuyển từ 2025 trở về trước, Trường lựa chọn áp dụng quy định mới có lợi hơn cho người học.
  - Chỉ index các Điều của quy chế, không index ba Điều của QĐ 3087 (file 2026 có kèm Quyết định ban hành; file PDF 2021 chỉ có phần quy chế).
- **Corpus D1 (chỉ để đánh giá):** D1 chỉ có nội dung từng đoạn, không ghi Điều thuộc văn bản nào, số hiệu, ngày ban hành hay phiên bản. Repo ViRE @ `60ea715` cũng không có file ánh xạ đoạn về văn bản gốc (đã kiểm tra 23/11). Chunk của D1 chỉ giữ mã đoạn, số và tên Điều; không suy đoán các thông tin còn lại.
- **Index:** mỗi chunk giữ `doc_id` (D1: `virhe4qa`), `article_id`, `article`, `article_title`, `clause`, offset ký tự để trích đúng đoạn.
- **Hiển thị (corpus HCMUS):**
  - Dạng: "Điều 15, Khoản 1 – Quy chế đào tạo trình độ đại học (QĐ 3087/QĐ-KHTN, 29/9/2026; áp dụng cho khóa tuyển từ năm học 2026–2027, xem Điều 27 với khóa trước đó)".
  - Kèm dòng nhắc "Kết quả để tham khảo, hãy đối chiếu văn bản gốc".
  - Với QĐ 3087, ghi thêm "bản chép từ bản scan", vì đây là bản ChatGPT chép và nhóm làm sạch, không phải nguyên văn.
  - Ứng dụng không tự xác định phiên bản nào áp dụng cho một khóa cụ thể: nó hiển thị kết quả của cả hai phiên bản, kèm phạm vi áp dụng ghi trong văn bản.
  - Các Điều cùng chủ đề (theo `data/d2/article_map.tsv`; một chủ đề có thể gồm 2–3 Điều) hiển thị thành **một** kết quả, có cả bản 2021 và bản 2026, để top-3 không tốn nhiều vị trí cho cùng một quy định.
  - Trong mỗi kết quả, **bản 2026 hiển thị trước** vì là bản mới nhất (D-18); mọi chủ đề đều có Điều của bản 2026. Bản 2021 hiển thị phụ, ghi rõ áp dụng cho khóa tuyển từ năm học 2021–2022 đến 2025, trừ quy định mới có lợi hơn (Điều 27 bản 2026).
- **Độ tin cậy thấp:** vẫn hiển thị top-3, gắn nhãn cảnh báo và gợi ý liên hệ phòng đào tạo. MVP **không từ chối cứng**. Ngưỡng θ được chọn và đánh giá theo E3 ([§6.4](#64-thí-nghiệm-thiết-yếu)).

### 5.4 Interface & định dạng dữ liệu

Hai người chốt phần này trước 25/11 để làm song song. Owner theo [docs/PLAN.md](../PLAN.md).

```text
corpus.jsonl   {chunk_id, doc_id, article_id, article, article_title, clause|null, text, char_start, char_end}
queries.jsonl  {qid, question, gold_article_ids: [..], gold_clause_ids: [..], split: dev|test, source: virhe4qa|d2, origin: team|form|null, in_scope: bool}
               # D2: article_id = "<doc_id>:dieu-<n>", clause id = "<article_id>:khoan-<m>"; câu ngoài phạm vi có gold rỗng
               # D2: origin = team (nhóm viết) hoặc form (câu thu qua Google Form); D1: origin = null
               # D1: chỉ có split dev|test, gold_clause_ids rỗng; D2 luôn là test
runs/<method>.jsonl  {qid, ranked: [[article_id, score, best_chunk_id], ...], top1_dense_cos}
               # top-20 ở mức Điều, chưa gộp chủ đề; best_chunk_id cho Clause@1, top1_dense_cos cho E3
API: search(query: str, k: int = 3, method: "bm25"|"dense"|"hybrid", corpus: "hcmus"|"virhe4qa" = "hcmus") -> list[Hit]
     Hit = {article_id, score, best_chunk_id, bm25_score, dense_cos, low_confidence: bool}
```

| Module (vị trí trong repo) | Input → Output | Owner | Tái sử dụng / Mới |
|---|---|---|---|
| `data/prepare_virhe4qa.py` | CSV ViRE → corpus/queries D1 + group split | Minh | Mới |
| `src/simcse_lab/retrieval/ingest.py` | `data/d2/documents.yaml` (đọc đúng file đã kiểm chứng: `text_file` của QĐ 1175, `file` của QĐ 3087), hoặc context của D1 → tách Điều/Khoản, chunk → `corpus.jsonl` | Minh | Mới |
| `src/simcse_lab/retrieval/preprocess.py` | text → text chuẩn hóa / tách từ / token BM25 | Minh | Mới (dùng pyvi) |
| `src/simcse_lab/model/encoders.py` | list[str] → ndarray (L2-norm) | Minh | Model tái sử dụng; code mới (tham khảo `simcse/tool.py`) |
| `src/simcse_lab/retrieval/search.py` | query → list[Hit] (BM25 / dense / hybrid, MaxP, confidence) | Minh | Mới (dùng rank_bm25, faiss) |
| `src/simcse_lab/evaluation/metrics.py` | runs + qrels (+ `data/d2/article_map.tsv` cho D2) → Hit@k, MRR@10 theo Điều; với D2 thêm mức theo chủ đề (gộp từ runs theo Điều) và Clause@1 | Minh | Mới |
| `src/simcse_lab/evaluation/stats.py` | hai runs → paired bootstrap CI; đo cảnh báo (coverage, Hit@1 theo nhóm tin cậy / không tin cậy, false-confidence trên câu ngoài phạm vi của D2) | Huy | Mới |
| `experiments/external_dataset/` | Chạy 3 phương pháp trên D1 (Minh); chọn λ, θ trên D1-dev (Huy) → `results/` | Minh, Huy | Mới |
| `experiments/application/` | So sánh trên D1-test và D2, phân tích lỗi (Huy); đo latency (Minh) → `results/` | Huy, Minh | Mới |
| `experiments/reproduction/` | `run_r1.py` gọi `evaluation.py` tại commit → `results/R1–R3` ✓; `run_r4.py` → `results/R4` ✓ | Huy | Code gốc + mới |
| `src/simcse_lab/model/infonce.py` + `tests/test_infonce.py` | R4: InfoNCE tự cài + test khớp `cl_forward` | Huy | Mới |
| `apps/app.py` | Gradio UI gọi `search` | Minh | Mới (dùng Gradio) |

### 5.5 Cấu trúc thư mục

Theo repo GitHub. Mục có dấu ✓ là đã có nội dung.

```
├── README.md · pyproject.toml · .gitignore
├── configs/default.yaml              # model, max_len, chunk, λ, θ, seed (dự kiến)
├── data/                             # README + prepare_virhe4qa.py; raw/ processed/ bị gitignore
│   └── d2/                           # ✓ README.md, documents.yaml, article_map.tsv, chữ QĐ 1175; queries_d2.jsonl (Phase 3). Bản chép QĐ 3087 ở raw/d2/
├── src/simcse_lab/
│   ├── model/                        # encoders.py, infonce.py ✓
│   ├── retrieval/                    # ingest.py, preprocess.py, search.py
│   └── evaluation/                   # metrics.py, stats.py
├── experiments/
│   ├── reproduction/                 # ✓ run_r1.py, run_r1.bat, requirements-r1.txt, results/R1–R3; run_r4.py, results/R4
│   │   └── SimCSE/                   # code gốc @ 235f89e (gitignore; script tự tải nếu thiếu)
│   ├── external_dataset/             # đánh giá D1 (E0, E1) → results/
│   └── application/                  # D2, so sánh theo mức trùng từ, cảnh báo, latency, lỗi (E2–E5) → results/
├── apps/app.py                       # Gradio
├── tests/                            # chunker, chuẩn hóa, metrics, infonce (✓ test_infonce.py, infonce_reference.py, test_worked_example.py, conftest.py)
├── docs/                             # PLAN.md, application/{README,PROJECT}.md, report/, demo/
└── .venv-repro/ · .cache/            # venv tái hiện, cache HuggingFace (gitignore)
```

Môi trường cho ứng dụng dùng venv riêng (`.venv`, cài bằng `pip install -e .`), không dùng chung `.venv-repro`.

**Stack:** Python 3.10 hoặc 3.11 [Proposed; kiểm tra pyvi cài được trước 25/11], torch, transformers, pyvi, rank_bm25, faiss-cpu, gradio, pyyaml, numpy, pandas, pytest. Không dùng server, database, Docker hay CI.

---

## 6. Datasets & Experimental Evaluation

### 6.1 Datasets

| ID | Dataset | Vai trò | Thông tin | Truy cập / License |
|---|---|---|---|---|
| **D1** | ViRHE4QA, bản con trong ViRE: `data/ViRHE4QA_v2.csv` @ ViRE commit `60ea7155134eaa426ab1d0a82d2bbbf327d1b470` (sha256 `23fb9699…aa5682`) | **Dataset mới chính** (bắt buộc); đánh giá trên corpus riêng của D1 | [Confirmed, đã đọc file] 1.000 câu hỏi, 297 context khác nhau (287 bắt đầu bằng "Điều"). Mỗi câu hỏi có đúng 1 context gold. Cột: `split, index, context, question, extractive answer, abstractive answer, label`. Theo nội dung, đây là quy định của Trường ĐH CNTT – ĐHQG-HCM: 77/297 context nêu tên trường, không context nào nêu trường khác. Tóm tắt bài R2GQA không nêu tên trường, nên đây là suy ra từ nội dung (kiểm tra 23/11). Không có thông tin văn bản gốc, số hiệu hay phiên bản của từng Điều. Context dài: trung vị 173 từ, p90 495, tối đa 1.249 → cần chunk. Ý nghĩa cột `label` (0/1, 500/500) chưa rõ [Unverified] và không dùng | Tải trực tiếp từ GitHub. ViRE: code MIT, dataset bên thứ ba giữ license gốc. Bài gốc R2GQA ghi dữ liệu cung cấp "on reasonable request" → license [Unverified]. Chỉ dùng đánh giá học thuật, trích dẫn cả hai. **Nộp bằng link permalink** tới file ở commit trên (giảng viên cho phép nộp dataset bằng link) |
| **D2** | Câu hỏi nhóm tự viết trên quy chế đào tạo HCMUS: QĐ 1175/2021 và QĐ 3087/2026 ([`data/d2/`](../../data/d2/README.md); D-17) | Test trong bối cảnh thực tế (**chỉ test**) | [Proposed] 80–100 câu trong phạm vi + khoảng 20 câu ngoài phạm vi. Corpus 51 Điều (24 + 27). QĐ 1175: nguyên văn từ PDF có chữ. QĐ 3087: bản ChatGPT chép từ scan, nhóm làm sạch, không phải nguyên văn | QĐ 1175 công khai trên website trường. QĐ 3087 chưa thấy công khai (Q7). Câu hỏi do nhóm viết, có thể thêm câu thu qua Google Form ẩn danh (`origin`); không chứa dữ liệu cá nhân. Link Google Drive công khai gồm câu hỏi, nhãn, metadata và chữ QĐ 1175; bản chép QĐ 3087 chỉ nộp trong `[Group14].zip` (D-18) |
| R-STS | STS12–16, STS-B, SICK-R | Tái hiện R1–R3 | Theo script repo | `senteval.tar` (HF `princeton-nlp/datasets-for-simcse`) |
| D1-full | ViRHE4QA đầy đủ (9.758 cặp QA, 294 điều) | Tùy chọn | [Confirmed theo arXiv:2409.02840] | Xin tác giả; dự án **không phụ thuộc** vào bộ này |
| Dự phòng | EduCoQA (`data/EduCoQA.csv` trong ViRE; 511 câu hỏi / 262 đoạn, tư vấn tuyển sinh HCMUT) | Chỉ dùng nếu D1 không dùng được | [Confirmed] | CC BY-NC 4.0; bản trên HF cần đăng nhập |

**Tham chiếu bên ngoài trên D1** (không phải kết quả của nhóm; protocol khác nên **không so sánh trực tiếp**):

- **ViRE** (toàn bộ 1.000 câu): BM25 đạt P@1 65,8%, R@10 93,5%, MRR@10 76,05. Hybrid tốt nhất đạt MRR@10 81,42, với backbone khác SimCSE-VN.
- **R2GQA** trên ViRHE4QA đầy đủ (theo split của họ): BM25 đạt P@1 68,75; embedding LM pretrained đạt P@1 44,06.

**Hệ quả:** câu hỏi D1 được viết từ chính văn bản nên trùng từ vựng cao, và BM25 rất mạnh. Nhóm **không cam kết** dense hay hybrid sẽ thắng BM25 trên D1.
- Lợi ích ngữ nghĩa được kiểm tra chủ yếu trên D2 (câu hỏi kiểu sinh viên). Nhóm câu ít trùng từ trong D1-test là bằng chứng phụ (E2); nhóm này có thể nhỏ, nên phải báo kèm số câu và CI.
- Câu D2 do nhóm viết sau khi đã đọc văn bản (§6.2), nên phân phối từ vựng có thể khác câu hỏi thật (thường ít trùng từ hơn, bất lợi cho BM25). Báo cáo phải nêu thiên lệch này; nếu có câu thu qua Google Form thì báo riêng nhóm đó.
- Corpus D2 nhỏ: 51 Điều nhưng chỉ 26 chủ đề, vì phần lớn Điều 2021 và 2026 nói cùng một quy định. Hit@3 vì vậy dễ cao với mọi phương pháp. D2 báo hai mức (theo Điều và theo chủ đề), kèm Clause@1 và mức ngẫu nhiên; báo cáo nêu rõ quy mô corpus (§6.3).

### 6.2 Tiền xử lý, gán nhãn và chia dữ liệu

**D1**

- Corpus là 297 context, mỗi context một `article_id`. Queries là cả 1.000 câu hỏi.
- **Group split theo context** (seed 42): dev khoảng 20% context, test khoảng 80%. Câu hỏi về cùng một Điều không nằm ở cả dev và test.
- **Bắt buộc:** nhóm context "Điều 6. Báo cáo tiến độ thực hiện KLTN" (4 câu hỏi, gồm câu index 9542) phải vào **dev**, vì câu 9542 đã dùng làm ví dụ lexical gap trong Introduction của báo cáo. Gán nhóm này trước, rồi chia ngẫu nhiên phần còn lại.
- Corpus vẫn chứa **toàn bộ** 297 context, vì đây là kho tri thức chứ không phải nhãn.
- Bỏ qua cột `split` gốc: test gốc chỉ có 77 câu, và cách chia này bị rò rỉ. Ví dụ đã kiểm tra 23/11: context của Điều 6 nói trên có 2 câu ở train và 2 câu ở test.
- Loại câu hỏi trùng lặp nguyên văn nếu có, và ghi lại số lượng đã loại.

**D2** (D-17; mô tả corpus ở [`data/d2/README.md`](../../data/d2/README.md))

- **Corpus:** 51 Điều của hai văn bản trong `data/d2/documents.yaml`. Không đưa ba Điều của QĐ 3087 (Quyết định ban hành) vào corpus.
- **Người viết:** Huy và Minh mỗi người viết 40–50 câu trong phạm vi và 10 câu ngoài phạm vi (`origin: team`). Có thể thu thêm câu hỏi thật của bạn học qua Google Form ẩn danh (chỉ lấy nội dung câu hỏi; `origin: form`).
- **Cách viết (D-18):** viết kiểu "gập sách": đọc Điều, gập văn bản lại, rồi viết câu như khi hỏi bạn hoặc phòng đào tạo. Được dùng thuật ngữ thông dụng (học phần, tín chỉ, điểm trung bình tích lũy…), không chép nguyên câu hay mệnh đề từ văn bản. Câu ngoài phạm vi là câu mà cả hai văn bản đều không trả lời (ví dụ ký túc xá, căn tin).
  - Lý do: quy tắc cũ "không chép quá 3 từ liên tiếp" cấm cả thuật ngữ sinh viên vẫn dùng, làm câu bất lợi cho BM25 ngay từ cách xây dựng. Cách viết mới vẫn có thể cho câu ít trùng từ hơn câu thật, nên báo E2 theo mức trùng từ và báo riêng nhóm `form` nếu có.
- **Loại trùng:** trước khi chốt, loại câu trùng hoặc gần trùng giữa hai người viết và ghi số câu đã loại.
- **Gán nhãn:** người viết ghi `gold_article_ids`, và `gold_clause_ids` khi xác định được Khoản. Người kia kiểm tra độc lập. Ghi tỉ lệ đồng ý trước khi thảo luận và lưu log bất đồng.
- **Hai phiên bản:**
  - Gold gồm mọi Điều, ở bất kỳ phiên bản nào, có nội dung trả lời câu hỏi; câu được tính đúng nếu khớp bất kỳ gold nào (§6.3).
  - Không viết câu hỏi mà đáp án phụ thuộc vào việc khóa nào áp dụng phiên bản nào.
  - Nếu hai phiên bản trả lời khác nhau, ghi gold cả hai và thêm một dòng ghi chú.
- **Kỷ luật dữ liệu:** D2 **chỉ dùng để test**, không dùng để chọn λ, θ hay huấn luyện. Bảng đối ứng `article_map.tsv` duyệt xong trước khi gán nhãn. Nhãn chốt trước 02/12 và trước khi xem bất kỳ dự đoán nào trên D2.

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
- **Mức Khoản (chỉ D2, trên câu có `gold_clause_ids`):** Khoản tốt nhất của Điều đứng đầu có thuộc gold không (Clause@1). Metric này chặt, vì gắn với Điều đứng đầu, và bù cho việc corpus D2 nhỏ.
- **Hai mức cho D2:** luôn báo cả hai, không báo mức theo chủ đề một mình.
  - **Theo Điều (chặt):** như D1, không gộp. Một Điều chỉ đúng khi nằm trong gold.
  - **Theo chủ đề (khớp giao diện, dễ hơn):** các Điều được gộp thành chủ đề theo [`data/d2/article_map.tsv`](../../data/d2/article_map.tsv) (26 chủ đề cho 51 Điều; đã duyệt 24/11, D-18). Trước khi cắt top-k, các Điều cùng chủ đề chỉ tính một lần; câu hỏi tính là đúng khi chủ đề của một gold nằm trong top-k.
  - **Vì sao mức chủ đề dễ hơn:** sau khi gộp, top-k chứa nhiều chủ đề khác nhau hơn, nên Hit@k và MRR@10 chỉ có thể tăng hoặc giữ nguyên. Kể cả Hit@1 cũng dễ hơn khi chỉ một phiên bản trả lời được câu hỏi. Ví dụ T18: bản 2026 thêm chuyển ngành, nên câu hỏi về chuyển ngành chỉ có gold là Điều 21 bản 2026; nếu Điều 20 bản 2021 đứng đầu thì mức chủ đề tính đúng, mức Điều tính sai.
  - **Gộp trong cùng một phiên bản (giữ theo D-18):** T02 (Điều 2 và 3 bản 2021), T09 (Điều 12 và 13 bản 2026), T16 (Điều 17 và 18 bản 2021). Đã đối chiếu nội dung: một bản tách thành hai Điều nội dung mà bản kia gộp trong một Điều. Ví dụ Điều 10 bản 2021 gồm cả xét giao và đánh giá khóa luận, bản 2026 tách thành Điều 12 và 13.
  - **Mức ngẫu nhiên** (xếp hạng ngẫu nhiên): theo Điều, với g Điều gold, Hit@k = 1 − C(51−g, k)/C(51, k), vd. g = 2: Hit@1 ≈ 3,9%, Hit@3 ≈ 11,5%. Theo chủ đề, với một chủ đề gold: Hit@1 = 1/26 ≈ 3,8%, Hit@3 = 3/26 ≈ 11,5%.
  - Runs lưu ở mức Điều (§5.4); `metrics.py` tính mức chủ đề từ runs và `article_map.tsv`.
- **Ý nghĩa thống kê:** paired bootstrap 1.000 lần trên câu hỏi (seed 42), báo 95% CI của ΔMRR@10 và ΔHit@1.
- **Latency:** p50/p95 mỗi truy vấn trên CPU, tách riêng thời gian tách từ, encode và search; thời gian build index.

### 6.4 Thí nghiệm thiết yếu

| ID | Mục đích | Thiết lập | Đầu ra |
|---|---|---|---|
| E0 | Kiểm tra cài đặt | BM25 trên toàn bộ 1.000 câu D1, so sơ bộ với MRR@10 = 76,05 của ViRE. Lệch lớn → kiểm tra tách từ/chuẩn hóa | Ghi chú sanity check |
| E1 | Chất lượng truy hồi trên dataset mới | `bm25`, `dense`, `hybrid` (+ `phobert-raw`) trên D1-test. λ chọn trên D1-dev (lưới 0..1, bước 0,1, tối ưu MRR@10) | Bảng + CI cho `hybrid`−`bm25`, `dense`−`phobert-raw` |
| E2 | Bối cảnh thực tế và câu hỏi diễn đạt khác văn bản | Như E1 trên D2-in-scope (kết quả chính) và trên D1-test (bằng chứng phụ), cấu hình giữ nguyên. Chia câu hỏi theo mức trùng từ vựng với Điều gold (Jaccard token, ba nhóm thấp/vừa/cao) và báo metric từng nhóm kèm số câu mỗi nhóm. D2 báo cả mức theo Điều và theo chủ đề, thêm Clause@1, và báo riêng nhóm `origin: form` nếu có (§6.3) | Bảng + phân tích theo nhóm |
| E3 | Đánh giá cảnh báo độ tin cậy | θ chọn trên D1-dev: θ lớn nhất sao cho coverage ≥ 80% [Proposed, chốt khi có dữ liệu dev]. Trên D1-test và D2: coverage, Hit@1 trong nhóm "tin cậy" và nhóm "không tin cậy", tỉ lệ câu ngoài phạm vi của D2 bị đánh dấu tin cậy (false-confidence). Hạn chế phải nêu trong báo cáo: θ chọn trên corpus và kiểu câu hỏi của D1 (UIT) rồi dùng nguyên cho HCMUS, không chỉnh trên D2 | Bảng + biểu đồ risk–coverage |
| E4 | Chi phí sử dụng | Latency p50/p95 trên CPU cho `bm25`/`dense`/`hybrid`; ghi cấu hình máy | Bảng |
| E5 | Phân tích lỗi | 20–30 câu sai của `hybrid` trên D1-test và D2, phân loại: tách từ, Điều dài bị cắt, số/ngày tháng, viết tắt (vd. ĐTTX, KLTN), câu hỏi cần nhiều Điều, khác biệt diễn đạt | Bảng phân loại + ví dụ |

Thêm R1 và R4 ([§4.5](#45-kế-hoạch-tái-hiện-kết-quả-paper)). Kết quả của nhóm chỉ ghi vào bảng ở §6.7 sau khi đã chạy.

### 6.5 Tái lập thí nghiệm

- Mọi thí nghiệm chạy qua `configs/*.yaml`. Mỗi lần chạy lưu `experiments/<nhóm>/results/<exp_id>/{metrics.json, runs/, config.yaml, env.txt}`, trong đó `env.txt` gồm `pip freeze`, phiên bản Python, CPU/GPU và commit hash của repo nhóm.
- Seed 42 cho chia dữ liệu và bootstrap. Fine-tuning (nếu có) dùng 3 seed {42, 43, 44} và báo mean ± std.
- Ghi rõ commit SimCSE `235f89e`, commit ViRE `60ea715`, revision của checkpoint HF khi tải, và với D2 là sha256 các văn bản trong `data/d2/documents.yaml` cùng commit của `article_map.tsv` đã dùng.
- Khi so sánh với số của paper, README hoặc ViRE, ghi rõ "khác protocol/dữ liệu, không tương đương trực tiếp" nếu đúng như vậy.

### 6.6 Thí nghiệm tùy chọn

Chỉ làm khi MVP xong và còn thời gian.

| ID | Nội dung | Điều kiện làm |
|---|---|---|
| O1 | Domain-adaptive SimCSE: (a) unsup SimCSE tiếp tục trên câu của corpus quy chế; hoặc (b) supervised với cặp (câu hỏi, Điều đúng) + hard negative do BM25 khai thác, cần thêm D1-train theo group split. So với `dense` trên cùng test, 3 seed | Chỉ khi E1–E5 xong trước 06/12; dừng mọi việc tùy chọn sau 08/12 |
| O2 | User study nhỏ: 5–8 sinh viên, 4–6 nhiệm vụ tra cứu, within-subject (Ctrl+F trên PDF và ứng dụng, đảo thứ tự). Đo task success, thời gian, 3–5 câu Likert | Khi có thời gian; báo cáo là nghiên cứu nhỏ, không khái quát hóa |
| O3 | R5 mini dropout ablation | Có GPU rảnh |
| O4 | pyvi vs VnCoreNLP (RDRSegmenter); RRF vs λ-fusion; có/không tiền tố tiêu đề Điều trong chunk | Rẻ, nếu E5 chỉ ra vấn đề liên quan |
| O5 | Encoder đa ngôn ngữ làm trần tham chiếu (vd. `intfloat/multilingual-e5-base`) | Chỉ để thảo luận; không bắt buộc thắng |

### 6.7 Bảng theo dõi kết quả

Chỉ điền khi đã có file kết quả.

| Exp | Trạng thái | Kết quả chính | File |
|---|---|---|---|
| R1 | [x] 23/11 | TB 81,58 (README 81,58; paper 81,57). Từng task: 75,30 / 84,67 / 80,19 / 85,40 / 80,82 / 84,26 / 80,39 → khớp README 7/7 | `experiments/reproduction/results/R1/` |
| R2 | [x] 23/11 | TB 76,25 = paper. Từng task: 68,40 / 82,41 / 74,38 / 80,91 / 78,56 / 76,85 / 72,23 → khớp 7/7 | `experiments/reproduction/results/R2/` |
| R3 | [x] 23/11 | TB 56,70 = paper. Từng task: 39,70 / 59,37 / 49,67 / 66,03 / 66,19 / 53,88 / 62,06 → lệch ≤ 0,01 | `experiments/reproduction/results/R3/` |
| R4 | [x] 23/11 | 689/689 test pass. float64: lệch tối đa 8,4e-15 so với vòng lặp Eq. 4/8; so với `cl_forward` 6,0e-15 (w biểu diễn đúng trong float32) và 1,4e-9 (w = log 0,5, log 2; nguyên nhân: `cl_forward` dựng ma trận trọng số bằng float32, dựng bằng float64 thì còn 7,1e-15). Gradient khớp < 1e-6 trên một batch (N=8, d=32, τ=0,05, w ∈ {0, log 2}). float32: 3,7e-6, ngưỡng riêng 5e-5 | `experiments/reproduction/results/R4/`, `tests/test_infonce.py` |
| E0 | [ ] | — | `experiments/external_dataset/results/E0/` |
| E1 | [ ] | — | `experiments/external_dataset/results/E1/` |
| E2 | [ ] | — | `experiments/application/results/E2/` |
| E3 | [ ] | — | `experiments/external_dataset/results/E3/` |
| E4 | [ ] | — | `experiments/application/results/E4/` |
| E5 | [ ] | — | `experiments/application/results/E5/` |

---

## 7. Development Plan & Team Workflow

Phân công chi tiết và checklist nằm ở **[docs/PLAN.md](../PLAN.md)**, nguồn duy nhất về ai làm gì. Mục này chỉ giữ lịch, phụ thuộc và cách làm việc.

### 7.1 Cách làm việc

- Một repo GitHub chung. Mỗi người làm trên branch riêng (`huy/...`, `minh/...`) và merge vào `main` khi chạy được; người kia xem lướt trước khi merge.
- Interface ở [§5.4](#54-interface--định-dạng-dữ-liệu) được chốt trước 25/11 để hai người ít phải chờ nhau.
- Mỗi tuần sync ngắn một lần (khoảng 15 phút). Xong việc nào thì người phụ trách tick trong PLAN.md và cập nhật [§1](#1-current-status).
- Mỗi mục trong PLAN.md có **một người chủ trì**; người còn lại hỗ trợ hoặc kiểm tra chéo.

### 7.2 Lịch theo PLAN.md

Tính từ 23/11, còn 18 ngày đến 11/12/2026. Phase 3 xong trước **06/12**. Từ 07/12 đến 10/12 viết báo cáo và quay video. Nộp sớm trong ngày **11/12, trước 20:00**.

| Phase (PLAN.md) | Hạn | Đầu ra chính | Phụ thuộc |
|---|---|---|---|
| 1 – Nghiên cứu paper | 27/11 | Hai phần viết đã đọc chéo. Huy: bài toán và phương pháp; Minh: dữ liệu, baseline, metric, kết quả, hạn chế | — |
| 2 – Triển khai và tái hiện | 30/11 | **Huy:** R1 ✓ (thêm R2, R3 ✓), R4 InfoNCE + test ✓, giải thích luồng code. **Minh:** D1 + group split; SimCSE-VN dense trên D1 (Hit@1/3, MRR@10, top-20, bảng D1-test) | D1 có sẵn |
| 3 – Xây dựng ứng dụng | 06/12 | **Minh:** corpus HCMUS từ `data/d2/` (tách Điều/Khoản, metadata), BM25 + Hybrid, Gradio, latency. **Huy:** bảng so sánh + CI, chọn λ/θ trên D1-dev, so sánh trên D1-test và D2 (chung và theo mức trùng từ), phân tích lỗi. **Cả hai:** D2 chốt nhãn trước 02/12 | Phase 2. Riêng việc viết câu D2 không phụ thuộc Phase 2: bắt đầu ngay (bảng đối ứng đã duyệt 24/11) |
| 4 – Hoàn thiện và nộp | 10/12; nộp 11/12 | **Huy:** PDF IEEE, chạy lại từ clone sạch. **Minh:** README, video, `[Group14].zip`, kiểm tra link | Phase 3 |
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
| Thời gian còn 18 ngày cho 2 người | Cao | MVP trước; hạn từng milestone ở §7.2; dừng việc tùy chọn sau 08/12; nộp trước 20:00 ngày 11/12 |
| pyvi không cài được [Unverified] | Trung bình | Thử Python 3.10; dự phòng VnCoreNLP (cần Java) hoặc underthesea và ghi rõ khác với model card |
| Không có GPU / hết quota | Thấp với MVP | MVP và R1 chạy CPU; GPU chỉ cần cho O1, O3 (Kaggle/Colab) |
| SimCSE-VN truy hồi kém, hybrid không thắng BM25 | Cao | Kết quả âm vẫn hợp lệ: phân tích theo mức trùng từ vựng (E2) và lỗi (E5); đóng góp vẫn gồm trích dẫn, phiên bản, cảnh báo được đánh giá; cân nhắc O1 |
| License D1 không rõ hoặc repo ViRE bị gỡ | Trung bình | Link nộp là permalink theo commit (không đổi được nội dung); lưu bản sao riêng để chạy lại; dự phòng EduCoQA; D2 vẫn là dataset mới của nhóm |
| Bản chép QĐ 3087/2026 (ChatGPT chép từ scan) khác bản gốc | Trung bình | Đã làm sạch 158 lỗi OCR có kiểm chứng: mọi con số có trong OCR, độ giống từng Điều trung bình 0,74 so với mức nền 0,15. Hai đoạn điểm thấp (Điều 6–7: 0,40; Điều 26: 0,35) đã đọc tay ngày 24/11: đủ Khoản, nội dung khớp, điểm thấp do OCR mất dấu. Vẫn còn lỗi OCR sót ngoài 158 chỗ đã sửa (vd. "đơn vi", "cau thành" ở Điều 3, phát hiện 24/11), cần một lượt rà toàn văn. Script và kết quả chạy lại ở `data/raw/d2/verification/`. Trích dẫn quan trọng đối chiếu bản scan. Ứng dụng ghi "bản chép từ bản scan" |
| Không được công bố lại bản chép quy chế 2026 (Q7) | Trung bình | Mặc định không đăng công khai (D-18): link D2 công khai gồm câu hỏi, nhãn, metadata và chữ QĐ 1175; bản chép QĐ 3087 chỉ nộp trong `[Group14].zip` để giảng viên chạy lại được. Khi trường đăng bản chính thức thì trỏ về đó |
| Corpus D2 nhỏ (51 Điều, 26 chủ đề) làm Hit@3 cao với mọi phương pháp | Trung bình | Báo cả mức theo Điều (chặt) và theo chủ đề, kèm Clause@1 và mức ngẫu nhiên (§6.3); trong báo cáo nêu rõ quy mô corpus và việc mức chủ đề dễ hơn mức Điều |
| Câu D2 do nhóm viết thiên lệch: người viết đã đọc văn bản nên câu có thể ít trùng từ hơn câu hỏi thật, bất lợi cho BM25 | Trung bình | Viết kiểu gập sách (D-18); nêu rõ trong báo cáo; báo E2 theo mức trùng từ cả trên D2; nếu có câu từ Google Form (`origin: form`) thì báo riêng nhóm này |
| Regex tách Điều/Khoản sai do định dạng khác nhau | Trung bình | Test trên cả ba nguồn: QĐ 1175 (chữ trích từ PDF bằng pdftotext), QĐ 3087 (Markdown) và D1. Kiểm tra số Điều: 24 và 27 |
| Nhãn D2 không nhất quán | Trung bình | Kiểm tra chéo, ghi tỉ lệ đồng ý, có log bất đồng |
| Tách từ không nhất quán giữa index và query | Trung bình | Một hàm `preprocess` dùng chung + unit test |
| Link nộp bài không truy cập được (−50%) | Cao | Kiểm tra mọi link ở chế độ ẩn danh trước khi nộp (Phase 4, Minh) |

### 8.2 Các nội dung đã điều chỉnh so với Research

- **D1 truy cập được ngay:** bản con ViRHE4QA có sẵn trong repo ViRE, không cần chờ xin bộ đầy đủ.
- **Thu gọn khối lượng:** D2 giảm từ 150–300 câu xuống 80–100 câu + 20 câu ngoài phạm vi, rồi bỏ ngày 23/11 (D-16) và khôi phục cùng ngày với corpus quy chế đào tạo HCMUS (D-17). Cohen's κ, user study và fine-tuning chuyển sang tùy chọn. Baseline bắt buộc chỉ còn BM25 / SimCSE-VN / Hybrid.
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
| D-05 | Không dùng LLM sinh câu trả lời; chỉ hiển thị đoạn văn bản có trong corpus + nguồn (QĐ 3087 là bản chép từ scan, ghi rõ khi hiển thị) | Chốt |
| D-06 | Confidence = cosine SimCSE của chunk tốt nhất trong top-1; θ từ D1-dev; chỉ cảnh báo | Chốt; quy tắc chọn θ chốt khi có dev |
| D-07 | D1 = ViRHE4QA (ViRE @ `60ea715`) là dataset mới chính; D2 chỉ test | Chốt (D2 khôi phục theo D-17) |
| D-08 | Tái hiện = R1 (bắt buộc) + R4; R2, R3 khuyến nghị; train SimCSE là tùy chọn | Chốt |
| D-09 | Gradio, chạy local; không server, database hay auth | Chốt |
| D-10 | FAISS `IndexFlatIP`, fallback numpy | Chốt |
| D-11 | Fine-tuning (O1) chỉ sau MVP; không nhắm bonus | Chốt |
| D-12 | Môi trường tái hiện: venv Python 3.11 + `experiments/reproduction/requirements-r1.txt` (numpy 1.23.5, scipy 1.10.1, scikit-learn 1.2.2, torch 2.5.1 CPU, transformers 4.46.3); chạy qua `experiments/reproduction/run_r1.py` | Chốt |
| D-13 | Dataset nộp bằng link: D1 = permalink ViRE @ `60ea715`; D2 = Google Drive public | Chốt (giảng viên cho phép); nội dung link D2 theo D-18 |
| D-14 | Phân công theo `docs/PLAN.md`; PROJECT.md chỉ giữ lịch và phụ thuộc | Chốt (23/11) |
| D-15 | Cấu trúc code theo repo `UniSearch-SimCSE` (package `simcse_lab`, thư mục `experiments/`) | Chốt (23/11) |
| D-16 | Bỏ D2. Chỉ đánh giá trên D1; corpus của ứng dụng là 297 đoạn quy chế ĐH CNTT trong D1, không dùng quy chế trường khác. Ứng dụng hiển thị số và tên Điều, không hiển thị văn bản gốc hay phiên bản vì D1 không có thông tin này. Không đo cảnh báo với câu ngoài phạm vi | Bị thay bởi D-17 (23/11). Các phần vẫn còn hiệu lực: D1 không có metadata văn bản/phiên bản; D1 chia theo nhóm đoạn, nhóm câu 9542 ghim vào dev; cột `split` gốc của D1 bị rò rỉ |
| D-17 | Khôi phục D2. Corpus của ứng dụng và của D2 là quy chế đào tạo HCMUS: QĐ 1175/QĐ-KHTN (2021, 24 Điều, nguyên văn) và QĐ 3087/QĐ-KHTN (29/9/2026, 27 Điều, bản ChatGPT chép từ scan, nhóm làm sạch). Giữ cả hai phiên bản vì Điều 27 quy chế 2026 ghi: với các khóa tuyển sinh từ năm 2025 trở về trước, Trường lựa chọn áp dụng quy định mới có lợi hơn cho người học. Không dùng bản trích lược trong Sổ tay. D1 giữ vai trò đánh giá trên corpus riêng. Toàn văn để ngoài Git cho tới khi rõ Q7 | Chốt (23/11, Huy); phần toàn văn, hiển thị và cách viết câu được cụ thể hóa ở D-18 |
| D-18 | Chốt bốn điểm còn mở của D-17 và thứ tự hiển thị. (1) Duyệt `data/d2/article_map.tsv` sau khi đối chiếu nội dung; giữ T02/T09/T16. (2) Câu D2 viết kiểu gập sách, được dùng thuật ngữ thông dụng, không chép nguyên câu hay mệnh đề; bỏ quy tắc "không chép quá 3 từ liên tiếp". (3) Chữ QĐ 1175 (văn bản công khai) đưa vào Git ở `data/d2/`, giữ nguyên byte (`.gitattributes`) để sha256 khớp. (4) Bản chép QĐ 3087 không đăng công khai cho tới khi trường đăng bản chính thức hoặc Phòng Đào tạo đồng ý; nộp kèm trong `[Group14].zip`. (5) Trong mỗi kết quả, bản 2026 hiển thị trước, bản 2021 là phụ | Chốt (24/11; Huy chọn ưu tiên bản 2026 và giao Claude quyết bốn điểm còn lại) |

**Vấn đề còn mở**

| ID | Câu hỏi | Ai giải quyết |
|---|---|---|
| Q5 | pyvi và faiss-cpu có cài được trên môi trường của nhóm không? | Minh (trước 25/11) |
| Q6 | Ý nghĩa cột `label` trong D1 | Minh (không chặn tiến độ) |
| Q7 | Phòng Đào tạo có đồng ý cho đăng công khai bản chép QĐ 3087/2026 không? Không còn chặn tiến độ: mặc định theo D-18 (không đăng công khai, nộp trong zip; chữ QĐ 1175 đã có trong Git). Nếu được đồng ý hoặc trường đăng bản chính thức thì thêm vào link D2 | Huy (khi có dịp, không chặn) |

Đã giải quyết (23/11): không xét bonus; Group ID = 14; deadline 23:59 ngày 11/12/2026; dataset được nộp bằng link; không cần xin phép giảng viên để dùng dataset; Q2 (chọn văn bản quy chế của trường) đóng: QĐ 1175/2021 và QĐ 3087/2026 (D-17).

### 8.4 Definition of Done

**Code**
- Chạy từ clone sạch theo README.
- Phiên bản thư viện được pin; cấu hình trong YAML; không có đường dẫn cứng.
- Test cho chunker, chuẩn hóa, metrics và InfoNCE đều pass. Có test kiểm số Điều của corpus D2 (24 và 27) và sha256 văn bản theo `documents.yaml`.
- Seed được ghi lại.

**Ứng dụng**
- Nhận câu hỏi tiếng Việt tự do; trả về top-3 Điều/Khoản với trích đoạn, tên văn bản, số hiệu, ngày ban hành và phạm vi áp dụng.
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

**Video** (≤ 30 phút; phân bổ gợi ý)
- Paper và phương pháp: ~8 phút.
- Code và tái hiện: ~7 phút.
- Thí nghiệm và phân tích: ~8 phút.
- Demo ứng dụng, so sánh với tìm kiếm từ khóa: ~6 phút.

**Nộp bài** (trước 23:59 ngày 11/12/2026, mục tiêu trước 20:00)
- `[Group14].zip` gồm code hoặc link GitHub, video, PDF.
- Link dataset (D1 permalink ViRE, D2 Google Drive) và link code đã kiểm tra ở chế độ ẩn danh.
- D2 public trên Google Drive (giữ ≥ 2 năm), nội dung theo D-18; `[Group14].zip` có kèm bản chép QĐ 3087.

### 8.5 References

- Gao, Yao, Chen. *SimCSE: Simple Contrastive Learning of Sentence Embeddings.* EMNLP 2021, pp. 6894–6910 — <https://aclanthology.org/2021.emnlp-main.552/>
- SimCSE code @ commit cố định — <https://github.com/princeton-nlp/SimCSE/tree/235f89e0244b23673b69fbbc4a1cd9868c5a5c24>
- SimCSE-VN checkpoint — <https://huggingface.co/VoVanPhuc/sup-SimCSE-VietNamese-phobert-base>
- PhoBERT — <https://github.com/VinAIResearch/PhoBERT>
- ViRE benchmark (chứa ViRHE4QA_v2, EduCoQA) — <https://github.com/longstnguyen/ViRE/tree/60ea7155134eaa426ab1d0a82d2bbbf327d1b470>
- R2GQA / ViRHE4QA — <https://arxiv.org/abs/2409.02840>
- EduCoQA (HF) — <https://huggingface.co/datasets/longstnguyen/vire-educoqa>
- Thư viện: rank_bm25 <https://github.com/dorianbrown/rank_bm25> · faiss <https://github.com/facebookresearch/faiss> · pyvi <https://github.com/trungtv/pyvi> · Gradio <https://www.gradio.app/>
- Mẫu IEEE Conference (`conference_101719.tex`, IEEEtran V1.8b) — <https://www.overleaf.com/latex/templates/ieee-conference-template/grfzhhncsfqn>. Build trên máy, không qua Overleaf: [docs/report/](../report/README.md).
