# D2: bộ test quy chế đào tạo của Trường ĐH KHTN (HCMUS)

D2 là bộ câu hỏi kiểu sinh viên do nhóm tự viết về quy chế đào tạo của trường mình, **chỉ dùng để test**. Quyết định: D-17 trong [PROJECT.md §8.3](../../docs/application/PROJECT.md#83-decision-log). Quy tắc gán nhãn: [PROJECT.md §6.2](../../docs/application/PROJECT.md#62-tiền-xử-lý-gán-nhãn-và-chia-dữ-liệu).

D2 bù ba chỗ D1 (ViRHE4QA) không có:
- Câu hỏi diễn đạt khác văn bản. Câu hỏi D1 được viết từ chính văn bản, nên trùng từ nhiều.
- Câu hỏi ngoài phạm vi, để đo cảnh báo độ tin cậy.
- Văn bản thật của trường mình, có số hiệu, ngày ban hành và hiệu lực, để ứng dụng hiển thị đúng phiên bản.

## Corpus: 2 văn bản, 51 Điều

| doc_id | Văn bản | Số Điều | Văn bản dùng làm corpus |
|---|---|---|---|
| `hcmus-qcdt-2021` | Quy chế đào tạo trình độ đại học, QĐ 1175/QĐ-KHTN ngày 24/9/2021 | 24 | Nguyên văn, trích từ PDF có lớp chữ (công khai) |
| `hcmus-qcdt-2026` | Quy chế đào tạo trình độ đại học, QĐ 3087/QĐ-KHTN ngày 29/9/2026 | 27 | Bản ChatGPT chép từ scan, nhóm làm sạch lỗi OCR; **không phải nguyên văn** |

**Vì sao giữ cả hai phiên bản:**
- QĐ 3087 thay thế QĐ 1175.
- Theo Điều 27 của quy chế 2026, quy chế mới áp dụng cho các khóa tuyển từ năm học 2026–2027. Với khóa tuyển sinh từ năm 2025 trở về trước, Trường lựa chọn áp dụng quy định mới có lợi hơn cho người học.
- Người dùng thật của ứng dụng (sinh viên K21–K25) vì vậy cần tra được cả hai văn bản và biết mỗi Điều thuộc phiên bản nào.

Chỉ các Điều của quy chế được đưa vào corpus. File 2026 có kèm Quyết định ban hành (3 Điều); ba Điều này không được đưa vào, để số Điều không bị trùng. File PDF 2021 chỉ có phần quy chế.

Thông tin từng văn bản (số hiệu, ngày ban hành, hiệu lực, nguồn, cách chép, sha256, kết quả kiểm chứng): [documents.yaml](documents.yaml).

## Đối ứng 2021 ↔ 2026

[article_map.tsv](article_map.tsv) gộp 51 Điều thành 26 chủ đề. **Đã duyệt ngày 24/11 (D-18)** sau khi đối chiếu nội dung các cặp có tiêu đề khác nhau.
- 22 chủ đề có ở cả hai bản; 4 Điều chỉ có ở bản 2026 (Điều 2, 9, 24, 26).
- Bảng được dựng từ tiêu đề Điều; ba cặp khó (Điều 4, 5, 24 của bản 2021) đã đối chiếu thêm nội dung. Script dựng bảng (`build_article_map.py`, kiểm mỗi Điều xuất hiện đúng một lần) ở `data/raw/d2/verification/scripts/`.
- T02, T09, T16 gộp hai Điều của **cùng một** phiên bản (một bản tách thành hai Điều nội dung mà bản kia gộp trong một Điều). Đã đối chiếu nội dung và giữ (D-18).
- **Cách dùng** (PROJECT.md §5.3, §6.3):
  - Khi hiển thị, các Điều cùng chủ đề gộp thành một kết quả; bản 2026 hiển thị trước, bản 2021 là phụ (D-18).
  - Khi đánh giá, D2 báo hai mức. **Theo Điều** là mức chặt, không gộp. **Theo chủ đề** khớp với giao diện nhưng dễ hơn: Điều của phiên bản kia hoặc Điều cùng chủ đề cũng được tính đúng. Luôn báo cả hai mức, không báo mức theo chủ đề một mình.

## File

| File | Nội dung | Trong Git? |
|---|---|---|
| `data/d2/README.md`, `data/d2/documents.yaml`, `data/d2/article_map.tsv` | Mô tả D2, thông tin văn bản, đối ứng Điều 2021 ↔ 2026 | Có |
| `data/d2/Quy_che_dao_tao_2021_QD1175.txt` | Chữ trích từ PDF công khai, dùng làm corpus 2021. `.gitattributes` giữ nguyên byte để sha256 khớp | Có |
| `data/raw/d2/Quy_che_dao_tao_2021_QD1175.pdf` | Bản PDF công khai (tải lại từ `source_url`) | Không (`data/raw/` bị bỏ qua) |
| `data/raw/d2/Quy_che_dao_tao_2026_QD3087.md` | Bản ChatGPT chép từ scan (bản gốc, giữ nguyên) | Không |
| `data/raw/d2/Quy_che_dao_tao_2026_QD3087_clean.md` | Bản đã làm sạch, dùng làm corpus | Không |
| `data/raw/d2/Quy_che_dao_tao_2026_QD3087_corrections.md` | Nhật ký 165 chỗ sửa (hai lượt) | Không |
| `data/raw/d2/verification/` | Đầu vào, script và kết quả kiểm chứng bản chép 2026 và bảng đối ứng | Không |
| `data/d2/queries_d2.jsonl` | Câu hỏi và nhãn do nhóm viết (chưa có, Phase 3) | Có |

Chữ QĐ 1175 có trong Git vì văn bản đã công khai. Bản chép QĐ 3087 không đăng công khai cho tới khi trường đăng bản chính thức hoặc Phòng Đào tạo đồng ý; bản này được nộp kèm trong `[Group14].zip` (D-18, Q7). Bản scan gốc do Huy giữ.

## Câu hỏi (Phase 3, chốt nhãn trước 02/12)

- **Số lượng:** 80–100 câu trong phạm vi và khoảng 20 câu ngoài phạm vi. Huy và Minh mỗi người viết 40–50 câu trong phạm vi và 10 câu ngoài phạm vi.
- **Định dạng:** mỗi dòng của `queries_d2.jsonl` theo schema ở PROJECT.md §5.4, với `source: "d2"` và `origin: "team"` hoặc `"form"` (câu thu qua Google Form). Mã Điều có tiền tố `doc_id`, ví dụ `hcmus-qcdt-2026:dieu-15`; mã Khoản ví dụ `hcmus-qcdt-2026:dieu-15:khoan-1`.
- **Cách viết và thiên lệch đã biết (D-18):** viết kiểu gập sách, được dùng thuật ngữ thông dụng, không chép nguyên câu hay mệnh đề. Người viết đã đọc văn bản nên câu vẫn có thể ít trùng từ hơn câu hỏi thật, bất lợi cho BM25. Báo cáo phải nêu điều này; nếu có câu từ Google Form thì báo riêng nhóm `origin: "form"`.
- Quy tắc viết, gán nhãn và chống rò rỉ: PROJECT.md §6.2.
