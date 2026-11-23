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

**Nhóm 14** · **Deadline: 23:59 ngày 11/12/2026** · Cập nhật lần cuối: 2026-11-23 (Huy)

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

**Đang thực hiện:** không có.

**Chưa thực hiện:** phần còn lại của Phase 2–4 ([§7.2](#72-lịch-theo-planmd)).

**Blocker / chờ quyết định**

- Chưa chốt văn bản quy chế cụ thể của trường để làm corpus cho ứng dụng và D2 (Q2 ở [§8.3](#83-decision-log)).

**3 việc ưu tiên tiếp theo**

1. **Minh** đọc chéo phần bài toán và phương pháp của Huy (Phase 1, hạn 27/11): Introduction và Proposed Method trong `docs/report/sections/`. **Huy** đọc chéo phần của Minh khi Minh xong.
2. **Minh:** chuẩn bị D1 (`data/prepare_virhe4qa.py`, group split) và chạy SimCSE-VN dense trên D1. Chọn văn bản quy chế của trường trước 27/11 để hai người bắt đầu viết D2.
3. **Cả hai:** chốt schema dữ liệu ở [§5.4](#54-interface--định-dạng-dữ-liệu) trước 25/11.

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

Truy hồi lai **BM25 + SimCSE-VN** trên corpus chia theo Điều/Khoản. Kết quả hiển thị là nguyên văn kèm nguồn và phiên bản, có cảnh báo khi độ tin cậy thấp. Ứng dụng **không** sinh câu trả lời bằng LLM.

### 2.5 Phạm vi

**MVP (bắt buộc)**

1. Nạp 1–3 văn bản quy chế dạng text-based PDF/DOCX/TXT. Tách Điều/Khoản và lưu metadata (văn bản, số hiệu, ngày ban hành, hiệu lực).
2. Ba phương pháp truy hồi chạy trên cùng pipeline: BM25, SimCSE-VN (dense) và Hybrid.
3. Giao diện Gradio gồm:
   - ô nhập câu hỏi;
   - top-3 Điều/Khoản, trích đoạn và nguồn/phiên bản;
   - nhãn "Độ tin cậy thấp" khi cần;
   - chế độ so sánh song song với BM25.
4. Đánh giá định lượng trên D1 và D2 ([§6](#6-datasets--experimental-evaluation)) và đo latency trên CPU.
5. Tái hiện R1 ([§4.5](#45-kế-hoạch-tái-hiện-kết-quả-paper)) và tự cài lại InfoNCE kèm kiểm thử.

**Nâng cao (tùy chọn, chỉ làm sau khi MVP xong):** O1 domain-adaptive fine-tuning, O2 user study nhỏ, O3–O5 ablation ([§6.6](#66-thí-nghiệm-tùy-chọn)).

**Ngoài phạm vi:** sinh câu trả lời bằng LLM, hội thoại nhiều lượt, OCR cho PDF scan, so sánh khác biệt giữa các phiên bản văn bản, đăng nhập, database server, triển khai cloud, Option 2.

### 2.6 Đóng góp riêng của nhóm

| Tái sử dụng (có trích dẫn) | Nhóm tự phát triển |
|---|---|
| Mã nguồn và checkpoint SimCSE chính thức (tái hiện) | Pipeline tách Điều/Khoản, giữ metadata và phiên bản |
| Checkpoint `VoVanPhuc/sup-SimCSE-VietNamese-phobert-base`, PhoBERT | Truy hồi lai, gộp điểm theo Điều, chọn α trên dev |
| pyvi, rank_bm25, faiss, Gradio | Cơ chế cảnh báo độ tin cậy cùng cách chọn và đánh giá ngưỡng |
| Bộ ViRHE4QA (bản con trong ViRE) | Bộ test D2 (quy chế trường, câu hỏi kiểu sinh viên, kèm câu ngoài phạm vi) |
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
| 3.3.4 | Tái hiện ≥1 kết quả (hoặc đánh giá tương đương); **đánh giá trên dataset mới** và nêu rõ khi không so sánh trực tiếp được | B | R1 ([§4.5](#45-kế-hoạch-tái-hiện-kết-quả-paper)); D1 + D2 ([§6.1](#61-datasets)) | Bảng R1; bảng E1/E2 | Huy (R1 ✓), Minh (D1) / 2 |
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

```
[Offline – build index]
Văn bản quy chế (PDF/DOCX/TXT) + documents.yaml (metadata)
  → ingest: trích text → tách Điều / Khoản → chunk ≤ 256 token → corpus.jsonl
  → preprocess: Unicode NFC → chuẩn hóa dấu thanh (khoá→khóa) → tách từ pyvi
  → BM25 index (token thường hóa)  +  SimCSE-VN embeddings (chuẩn hóa L2) → FAISS IndexFlatIP

[Online – mỗi câu hỏi]
Câu hỏi → preprocess (cùng hàm) → điểm BM25 và cosine cho mọi chunk
  → gộp chunk về Điều (MaxP: lấy max) → min-max normalize theo từng phương pháp
  → Hybrid: s = α·BM25_norm + (1−α)·Dense_norm   (α chọn trên D1-dev)
  → top-3 Điều (kèm Khoản / chunk tốt nhất)
  → Confidence: cosine SimCSE của chunk tốt nhất trong top-1 < τ  ⇒  cảnh báo "Độ tin cậy thấp"
  → UI: Điều/Khoản · trích đoạn · văn bản · số hiệu · ngày ban hành · điểm · [so sánh BM25]
```

### 5.2 Vai trò từng thành phần [Proposed]

| Thành phần | Vai trò | Lý do |
|---|---|---|
| SimCSE-VN | Khớp ngữ nghĩa, xử lý câu hỏi diễn đạt khác văn bản | Thành phần ML chính, gắn trực tiếp với paper |
| BM25 (`rank_bm25`) | Khớp từ khóa, số liệu, thuật ngữ, viết tắt | Đại diện giải pháp hiện có; rất mạnh trên D1 theo tham chiếu ngoài ([§6.1](#61-datasets)) |
| Hybrid α-fusion | Kết hợp hai loại tín hiệu; chỉ 1 tham số | Đơn giản, chọn trên dev, dễ giải thích |
| FAISS `IndexFlatIP` | Tìm kiếm chính xác (exact) theo inner product trên vector đã chuẩn hóa; cùng cách với `simcse/tool.py` | Nếu cài lỗi, dùng numpy dot product (kết quả giống hệt vì đều exact) |
| Gộp MaxP theo Điều | Điều dài phải chia chunk vì giới hạn 256 token; hiển thị và đánh giá ở mức Điều | Nhãn gold của D1 ở mức Điều |

**Lưu ý:** min-max normalize theo từng câu hỏi làm top-1 luôn gần 1, nên **không** dùng điểm fused làm độ tin cậy. Confidence dùng cosine tuyệt đối của SimCSE-VN.

### 5.3 Metadata, trích dẫn, phiên bản và trường hợp không chắc chắn

- **`documents.yaml`**, mỗi văn bản một mục: `doc_id`, `title`, `so_hieu` (số quyết định), `ngay_ban_hanh`, `hieu_luc_tu`, `trang_thai` (hiện hành / hết hiệu lực), `source_url`, `file`, `sha256`.
- **Index:** mặc định chỉ index văn bản *hiện hành*. Mỗi chunk giữ `doc_id`, `article`, `clause`, offset ký tự để trích đúng nguyên văn.
- **Hiển thị:** "Điều 12, Khoản 2 – \<tên văn bản\> (QĐ số …, ngày …)", kèm dòng nhắc "Kết quả để tham khảo, hãy đối chiếu văn bản gốc".
- **Độ tin cậy thấp:** vẫn hiển thị top-3, gắn nhãn cảnh báo và gợi ý liên hệ phòng đào tạo. MVP **không từ chối cứng**. Ngưỡng τ được chọn và đánh giá theo E3 ([§6.4](#64-thí-nghiệm-thiết-yếu)).

### 5.4 Interface & định dạng dữ liệu

Hai người chốt phần này trước 25/11 để làm song song. Owner theo [docs/PLAN.md](../PLAN.md).

```text
corpus.jsonl   {chunk_id, doc_id, article_id, article, article_title, clause|null, text, char_start, char_end}
queries.jsonl  {qid, question, gold_article_ids: [..], gold_clause|null, split: dev|test, source: virhe4qa|d2, in_scope: bool}
runs/<method>.jsonl  {qid, ranked: [[article_id, score], ...]}   # top-20
API: search(query: str, k: int = 3, method: "bm25"|"dense"|"hybrid") -> list[Hit]
     Hit = {article_id, score, best_chunk_id, bm25_score, dense_cos, low_confidence: bool}
```

| Module (vị trí trong repo) | Input → Output | Owner | Tái sử dụng / Mới |
|---|---|---|---|
| `data/prepare_virhe4qa.py` | CSV ViRE → corpus/queries D1 + group split | Minh | Mới |
| `src/simcse_lab/retrieval/ingest.py` | PDF/DOCX/TXT + `documents.yaml` → `corpus.jsonl` | Minh | Mới (dùng pdfplumber, python-docx) |
| `src/simcse_lab/retrieval/preprocess.py` | text → text chuẩn hóa / tách từ / token BM25 | Minh | Mới (dùng pyvi) |
| `src/simcse_lab/model/encoders.py` | list[str] → ndarray (L2-norm) | Minh | Model tái sử dụng; code mới (tham khảo `simcse/tool.py`) |
| `src/simcse_lab/retrieval/search.py` | query → list[Hit] (BM25 / dense / hybrid, MaxP, confidence) | Minh | Mới (dùng rank_bm25, faiss) |
| `src/simcse_lab/evaluation/metrics.py` | runs + qrels → Hit@k, MRR@10 | Minh | Mới |
| `src/simcse_lab/evaluation/stats.py` | hai runs → paired bootstrap CI; đo cảnh báo (coverage, false-confidence) | Huy | Mới |
| `experiments/external_dataset/` | Chạy 3 phương pháp trên D1 (Minh); chọn α, τ trên D1-dev (Huy) → `results/` | Minh, Huy | Mới |
| `experiments/application/` | So sánh trên D1-test và D2, phân tích lỗi (Huy); đo latency (Minh) → `results/` | Huy, Minh | Mới |
| `experiments/reproduction/` | `run_r1.py` gọi `evaluation.py` tại commit → `results/R1–R3` ✓; `run_r4.py` → `results/R4` ✓ | Huy | Code gốc + mới |
| `src/simcse_lab/model/infonce.py` + `tests/test_infonce.py` | R4: InfoNCE tự cài + test khớp `cl_forward` | Huy | Mới |
| `apps/app.py` | Gradio UI gọi `search` | Minh | Mới (dùng Gradio) |

### 5.5 Cấu trúc thư mục

Theo repo GitHub. Mục có dấu ✓ là đã có nội dung.

```
├── README.md · pyproject.toml · .gitignore
├── configs/default.yaml              # model, max_len, chunk, α, τ, seed (dự kiến)
├── data/                             # README + prepare_virhe4qa.py; raw/ processed/ bị gitignore
│   └── d2/                           # documents.yaml, queries_d2.jsonl (nhóm tự tạo)
├── src/simcse_lab/
│   ├── model/                        # encoders.py, infonce.py ✓
│   ├── retrieval/                    # ingest.py, preprocess.py, search.py
│   └── evaluation/                   # metrics.py, stats.py
├── experiments/
│   ├── reproduction/                 # ✓ run_r1.py, run_r1.bat, requirements-r1.txt, results/R1–R3; run_r4.py, results/R4
│   │   └── SimCSE/                   # code gốc @ 235f89e (gitignore; script tự tải nếu thiếu)
│   ├── external_dataset/             # đánh giá D1 (E0, E1, E3-D1) → results/
│   └── application/                  # D2, so sánh, latency, lỗi (E2–E5) → results/
├── apps/app.py                       # Gradio
├── tests/                            # chunker, chuẩn hóa, metrics, infonce (✓ test_infonce.py, infonce_reference.py, conftest.py)
├── docs/                             # PLAN.md, application/{README,PROJECT}.md, report/, demo/
└── .venv-repro/ · .cache/            # venv tái hiện, cache HuggingFace (gitignore)
```

Môi trường cho ứng dụng dùng venv riêng (`.venv`, cài bằng `pip install -e .`), không dùng chung `.venv-repro`.

**Stack:** Python 3.10 hoặc 3.11 [Proposed; kiểm tra pyvi cài được trước 25/11], torch, transformers, pyvi, rank_bm25, faiss-cpu, gradio, pdfplumber, python-docx, pyyaml, numpy, pandas, pytest. Không dùng server, database, Docker hay CI.

---

## 6. Datasets & Experimental Evaluation

### 6.1 Datasets

| ID | Dataset | Vai trò | Thông tin | Truy cập / License |
|---|---|---|---|---|
| **D1** | ViRHE4QA, bản con trong ViRE: `data/ViRHE4QA_v2.csv` @ ViRE commit `60ea7155134eaa426ab1d0a82d2bbbf327d1b470` | **Dataset mới chính** (bắt buộc) | [Confirmed, đã đọc file] 1.000 câu hỏi, 297 context khác nhau (287 bắt đầu bằng "Điều"). Mỗi câu hỏi có đúng 1 context gold. Cột: `split, index, context, question, extractive answer, abstractive answer, label`. Theo nội dung mẫu, đây là quy định của Trường ĐH CNTT – ĐHQG-HCM. Context dài: trung vị 173 từ, p90 495, tối đa 1.249 → cần chunk. Ý nghĩa cột `label` (0/1, 500/500) chưa rõ [Unverified] và không dùng | Tải trực tiếp từ GitHub. ViRE: code MIT, dataset bên thứ ba giữ license gốc. Bài gốc R2GQA ghi dữ liệu cung cấp "on reasonable request" → license [Unverified]. Chỉ dùng đánh giá học thuật, trích dẫn cả hai. **Nộp bằng link permalink** tới file ở commit trên (giảng viên cho phép nộp dataset bằng link) |
| **D2** | Quy chế của trường + câu hỏi nhóm tự viết | Test trong bối cảnh thực tế (**chỉ test**) | [Proposed] 80–100 câu trong phạm vi + 20 câu ngoài phạm vi | Văn bản công khai của trường; câu hỏi do nhóm tạo, không chứa dữ liệu cá nhân. Upload Google Drive (public) và nộp link |
| R-STS | STS12–16, STS-B, SICK-R | Tái hiện R1–R3 | Theo script repo | `senteval.tar` (HF `princeton-nlp/datasets-for-simcse`) |
| D1-full | ViRHE4QA đầy đủ (9.758 cặp QA, 294 điều) | Tùy chọn | [Confirmed theo arXiv:2409.02840] | Xin tác giả; dự án **không phụ thuộc** vào bộ này |
| Dự phòng | EduCoQA (`data/EduCoQA.csv` trong ViRE; 511 câu hỏi / 262 đoạn, tư vấn tuyển sinh HCMUT) | Chỉ dùng nếu D1 không dùng được | [Confirmed] | CC BY-NC 4.0; bản trên HF cần đăng nhập |

**Tham chiếu bên ngoài trên D1** (không phải kết quả của nhóm; protocol khác nên **không so sánh trực tiếp**):

- **ViRE** (toàn bộ 1.000 câu): BM25 đạt P@1 65,8%, R@10 93,5%, MRR@10 76,05. Hybrid tốt nhất đạt MRR@10 81,42, với backbone khác SimCSE-VN.
- **R2GQA** trên ViRHE4QA đầy đủ (theo split của họ): BM25 đạt P@1 68,75; embedding LM pretrained đạt P@1 44,06.

**Hệ quả:** câu hỏi D1 được viết từ chính văn bản nên trùng từ vựng cao, và BM25 rất mạnh. Nhóm **không cam kết** dense hay hybrid sẽ thắng BM25 trên D1. D2 (câu hỏi kiểu sinh viên) là nơi kiểm tra lợi ích ngữ nghĩa.

### 6.2 Tiền xử lý, gán nhãn và chia dữ liệu

**D1**

- Corpus là 297 context, mỗi context một `article_id`. Queries là cả 1.000 câu hỏi.
- **Group split theo context** (seed 42): dev khoảng 20% context, test khoảng 80%. Câu hỏi về cùng một Điều không nằm ở cả dev và test.
- Corpus vẫn chứa **toàn bộ** 297 context, vì đây là kho tri thức chứ không phải nhãn.
- Bỏ qua cột `split` gốc: test gốc chỉ có 77 câu, và chia theo cặp QA nên context có thể trùng giữa các split.
- Loại câu hỏi trùng lặp nguyên văn nếu có, và ghi lại số lượng đã loại.

**D2**

- Huy và Minh mỗi người viết 40–50 câu hỏi, có thể thu thêm câu hỏi thật của bạn học qua Google Form ẩn danh (chỉ lấy nội dung câu hỏi).
- Quy tắc: diễn đạt như sinh viên, không chép cụm quá 3 từ liên tiếp từ văn bản. Thêm khoảng 20 câu ngoài phạm vi văn bản.
- **Gán nhãn:** người viết ghi `gold_article_ids` (và Khoản nếu rõ); người kia kiểm tra độc lập. Ghi tỉ lệ đồng ý trước khi thảo luận và lưu log bất đồng.
- D2 **chỉ dùng để test**. Không dùng để chọn α, τ hay huấn luyện.

**Chống leakage:**
- α và τ chỉ chọn trên D1-dev.
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
- **Ý nghĩa thống kê:** paired bootstrap 1.000 lần trên câu hỏi (seed 42), báo 95% CI của ΔMRR@10 và ΔHit@1.
- **Latency:** p50/p95 mỗi truy vấn trên CPU, tách riêng thời gian tách từ, encode và search; thời gian build index.

### 6.4 Thí nghiệm thiết yếu

| ID | Mục đích | Thiết lập | Đầu ra |
|---|---|---|---|
| E0 | Kiểm tra cài đặt | BM25 trên toàn bộ 1.000 câu D1, so sơ bộ với MRR@10 = 76,05 của ViRE. Lệch lớn → kiểm tra tách từ/chuẩn hóa | Ghi chú sanity check |
| E1 | Chất lượng truy hồi trên dataset mới | `bm25`, `dense`, `hybrid` (+ `phobert-raw`) trên D1-test. α chọn trên D1-dev (lưới 0..1, bước 0,1, tối ưu MRR@10) | Bảng + CI cho `hybrid`−`bm25`, `dense`−`phobert-raw` |
| E2 | Bối cảnh thực tế và câu hỏi diễn đạt khác văn bản | Như E1 trên D2-in-scope, cấu hình giữ nguyên. Chia câu hỏi theo mức trùng từ vựng với Điều gold (Jaccard token, ba nhóm thấp/vừa/cao) và báo metric từng nhóm | Bảng + phân tích theo nhóm |
| E3 | Đánh giá cảnh báo độ tin cậy | τ chọn trên D1-dev: τ lớn nhất sao cho coverage ≥ 80% [Proposed, chốt khi có dữ liệu dev]. Trên D1-test và D2: coverage, Hit@1 trong nhóm "tin cậy" và nhóm "không tin cậy", tỉ lệ câu ngoài phạm vi bị đánh dấu tin cậy (false-confidence) | Bảng + biểu đồ risk–coverage |
| E4 | Chi phí sử dụng | Latency p50/p95 trên CPU cho `bm25`/`dense`/`hybrid`; ghi cấu hình máy | Bảng |
| E5 | Phân tích lỗi | 20–30 câu sai của `hybrid` (cả D1 và D2), phân loại: tách từ, Điều dài bị cắt, số/ngày tháng, viết tắt (vd. ĐTTX, KLTN), câu hỏi cần nhiều Điều, khác biệt diễn đạt | Bảng phân loại + ví dụ |

Thêm R1 và R4 ([§4.5](#45-kế-hoạch-tái-hiện-kết-quả-paper)). Kết quả của nhóm chỉ ghi vào bảng ở §6.7 sau khi đã chạy.

### 6.5 Tái lập thí nghiệm

- Mọi thí nghiệm chạy qua `configs/*.yaml`. Mỗi lần chạy lưu `experiments/<nhóm>/results/<exp_id>/{metrics.json, runs/, config.yaml, env.txt}`, trong đó `env.txt` gồm `pip freeze`, phiên bản Python, CPU/GPU và commit hash của repo nhóm.
- Seed 42 cho chia dữ liệu và bootstrap. Fine-tuning (nếu có) dùng 3 seed {42, 43, 44} và báo mean ± std.
- Ghi rõ commit SimCSE `235f89e`, commit ViRE `60ea715`, và revision của checkpoint HF khi tải.
- Khi so sánh với số của paper, README hoặc ViRE, ghi rõ "khác protocol/dữ liệu, không tương đương trực tiếp" nếu đúng như vậy.

### 6.6 Thí nghiệm tùy chọn

Chỉ làm khi MVP xong và còn thời gian.

| ID | Nội dung | Điều kiện làm |
|---|---|---|
| O1 | Domain-adaptive SimCSE: (a) unsup SimCSE tiếp tục trên câu của corpus quy chế; hoặc (b) supervised với cặp (câu hỏi, Điều đúng) + hard negative do BM25 khai thác, cần thêm D1-train theo group split. So với `dense` trên cùng test, 3 seed | Chỉ khi E1–E5 xong trước 06/12; dừng mọi việc tùy chọn sau 08/12 |
| O2 | User study nhỏ: 5–8 sinh viên, 4–6 nhiệm vụ tra cứu, within-subject (Ctrl+F trên PDF và ứng dụng, đảo thứ tự). Đo task success, thời gian, 3–5 câu Likert | Khi có thời gian; báo cáo là nghiên cứu nhỏ, không khái quát hóa |
| O3 | R5 mini dropout ablation | Có GPU rảnh |
| O4 | pyvi vs VnCoreNLP (RDRSegmenter); RRF vs α-fusion; có/không tiền tố tiêu đề Điều trong chunk | Rẻ, nếu E5 chỉ ra vấn đề liên quan |
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

Còn 18 ngày (23/11 → 11/12/2026). Phase 3 xong trước **06/12**. Từ 07/12 đến 10/12 viết báo cáo và quay video. Nộp sớm trong ngày **11/12, trước 20:00**.

| Phase (PLAN.md) | Hạn | Đầu ra chính | Phụ thuộc |
|---|---|---|---|
| 1 – Nghiên cứu paper | 27/11 | Hai phần viết đã đọc chéo. Huy: bài toán và phương pháp; Minh: dữ liệu, baseline, metric, kết quả, hạn chế | — |
| 2 – Triển khai và tái hiện | 30/11 | **Huy:** R1 ✓ (thêm R2, R3 ✓), R4 InfoNCE + test ✓, giải thích luồng code. **Minh:** D1 + group split; SimCSE-VN dense trên D1 (Hit@1/3, MRR@10, top-20, bảng D1-test) | D1 có sẵn |
| 3 – Xây dựng ứng dụng | 06/12 | **Minh:** chọn văn bản (trước 27/11), tách Điều/Khoản, BM25 + Hybrid, Gradio, latency. **Huy:** bảng so sánh + CI, chọn α/τ trên D1-dev, so sánh D1-test và D2, phân tích lỗi. **Cả hai:** D2 chốt nhãn trước 02/12 | Phase 2 |
| 4 – Hoàn thiện và nộp | 10/12; nộp 11/12 | **Huy:** PDF IEEE, chạy lại từ clone sạch. **Minh:** README, video, `[Group14].zip`, kiểm tra link | Phase 3 |
| Tùy chọn O1–O5 | dừng 08/12 | Chỉ làm nếu Phase 3 xong trước 06/12 | Phase 3 |

**Ràng buộc thứ tự**
- Nhãn D2 phải chốt **trước** khi xem dự đoán trên D2.
- α và τ phải cố định trên D1-dev **trước** khi chạy D1-test và D2.
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
| PDF quy chế là bản scan | Trung bình | Chọn bản text-based hoặc DOCX từ website; nếu không có thì chuyển text thủ công cho 1–2 văn bản (OCR ngoài phạm vi) |
| Regex tách Điều/Khoản sai do định dạng khác nhau | Trung bình | Test trên ≥ 2 văn bản; kiểm tra thủ công số Điều so với mục lục |
| Nhãn D2 không nhất quán | Trung bình | Kiểm tra chéo, ghi tỉ lệ đồng ý, có log bất đồng |
| Tách từ không nhất quán giữa index và query | Trung bình | Một hàm `preprocess` dùng chung + unit test |
| Link nộp bài không truy cập được (−50%) | Cao | Kiểm tra mọi link ở chế độ ẩn danh trước khi nộp (Phase 4, Minh) |

### 8.2 Các nội dung đã điều chỉnh so với Research

- **D1 truy cập được ngay:** bản con ViRHE4QA có sẵn trong repo ViRE, không cần chờ xin bộ đầy đủ.
- **Thu gọn khối lượng:** D2 giảm từ 150–300 câu xuống 80–100 câu + 20 câu ngoài phạm vi. Cohen's κ, user study và fine-tuning chuyển sang tùy chọn. Baseline bắt buộc chỉ còn BM25 / SimCSE-VN / Hybrid.
- **Sửa thông tin code:** tại commit cố định không có `--mlp_only_train` (Research mô tả theo bản fork hoặc `main`). Thêm các khác biệt eval_steps 125/250 và 81,58/81,57.
- **Số liệu R2GQA:** chỉ giữ những số đã đối chiếu được. Một số con số Research nêu (vd. ViSimCSE P@1 43,24, ensemble 72,13) chưa xác minh nên **không dùng**.
- **Confidence:** dùng cosine tuyệt đối, không dùng điểm fused đã min-max. Dạng cảnh báo thay vì từ chối cứng.
- **Bonus:** bỏ hẳn, vì giảng viên xác nhận không xét. O1 chỉ còn là thí nghiệm tùy chọn cho ứng dụng.

### 8.3 Decision log

| ID | Quyết định | Trạng thái |
|---|---|---|
| D-01 | Option 1; ứng dụng tra cứu quy chế học vụ; không chuyển sang Option 2 | Chốt |
| D-02 | Encoder: `VoVanPhuc/sup-SimCSE-VietNamese-phobert-base` + pyvi + `pooler_output`, max_len 256 | Chốt cho MVP |
| D-03 | Hybrid α-fusion trên điểm min-max theo Điều; α chọn trên D1-dev | Chốt |
| D-04 | Chunk theo Khoản (≤ 256 token, chia cửa sổ nếu dài); xếp hạng và đánh giá theo Điều (MaxP) | Chốt |
| D-05 | Không dùng LLM sinh câu trả lời; hiển thị nguyên văn + nguồn | Chốt |
| D-06 | Confidence = cosine SimCSE của chunk tốt nhất trong top-1; τ từ D1-dev; chỉ cảnh báo | Chốt; quy tắc chọn τ chốt khi có dev |
| D-07 | D1 = ViRHE4QA (ViRE @ `60ea715`) là dataset mới chính; D2 chỉ test | Chốt |
| D-08 | Tái hiện = R1 (bắt buộc) + R4; R2, R3 khuyến nghị; train SimCSE là tùy chọn | Chốt |
| D-09 | Gradio, chạy local; không server, database hay auth | Chốt |
| D-10 | FAISS `IndexFlatIP`, fallback numpy | Chốt |
| D-11 | Fine-tuning (O1) chỉ sau MVP; không nhắm bonus | Chốt |
| D-12 | Môi trường tái hiện: venv Python 3.11 + `experiments/reproduction/requirements-r1.txt` (numpy 1.23.5, scipy 1.10.1, scikit-learn 1.2.2, torch 2.5.1 CPU, transformers 4.46.3); chạy qua `repro/run_r1.py` | Chốt |
| D-13 | Dataset nộp bằng link: D1 = permalink ViRE @ `60ea715`; D2 = Google Drive public | Chốt (giảng viên cho phép) |
| D-14 | Phân công theo `docs/PLAN.md`; PROJECT.md chỉ giữ lịch và phụ thuộc | Chốt (23/11) |
| D-15 | Cấu trúc code theo repo `UniSearch-SimCSE` (package `simcse_lab`, thư mục `experiments/`) | Chốt (23/11) |

**Vấn đề còn mở**

| ID | Câu hỏi | Ai giải quyết |
|---|---|---|
| Q2 | Dùng văn bản quy chế nào của trường (tên, số hiệu, bản text-based)? | Minh |
| Q5 | pyvi và faiss-cpu có cài được trên môi trường của nhóm không? | Minh (trước 25/11) |
| Q6 | Ý nghĩa cột `label` trong D1 | Minh (không chặn tiến độ) |

Đã giải quyết (23/11): không xét bonus; Group ID = 14; deadline 23:59 ngày 11/12/2026; dataset được nộp bằng link; không cần xin phép giảng viên để dùng dataset.

### 8.4 Definition of Done

**Code**
- Chạy từ clone sạch theo README.
- Phiên bản thư viện được pin; cấu hình trong YAML; không có đường dẫn cứng.
- Test cho chunker, chuẩn hóa, metrics và InfoNCE đều pass.
- Seed được ghi lại.

**Ứng dụng**
- Nhận câu hỏi tiếng Việt tự do; trả về top-3 Điều/Khoản với trích đoạn, tên văn bản, số hiệu, ngày ban hành.
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
- D2 public trên Google Drive (giữ ≥ 2 năm).

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
