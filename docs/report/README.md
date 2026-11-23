# Báo cáo IEEE · Lab 03

Báo cáo viết theo [IEEE Conference Template trên Overleaf](https://www.overleaf.com/latex/templates/ieee-conference-template/grfzhhncsfqn) (`conference_101719.tex`, lớp `IEEEtran` V1.8b, engine pdfLaTeX) và build trên máy, không cần Overleaf. `main.tex` giữ nguyên preamble của mẫu, phần nhóm thêm được đánh dấu riêng. Đã bỏ các đoạn hướng dẫn, chú thích tài trợ và hình mẫu, vì chính mẫu yêu cầu xóa chúng trước khi nộp.

## Build

Cần MiKTeX hoặc TeX Live có gói `IEEEtran` và `vntex`. Chạy từ thư mục gốc repo bằng PowerShell, mất khoảng 10 giây.

```powershell
powershell -ExecutionPolicy Bypass -File docs\report\build.ps1     # thêm -Clean để build lại từ đầu
```

PDF nằm ở `docs/report/build/main.pdf`. Thư mục `build/` không được commit. Script in số cảnh báo LaTeX và số ghi chú `\TODO` còn lại.

Trên Linux hoặc macOS, chạy trong `docs/report/`:

```bash
mkdir -p build && pdflatex -output-directory=build main.tex && bibtex build/main \
  && pdflatex -output-directory=build main.tex && pdflatex -output-directory=build main.tex
```

Không dùng `latexmk`. Bản đi kèm MiKTeX cần Perl, mà PowerShell không có sẵn. Khi chạy qua Git Bash, BibTeX lại không tìm thấy `references.bib` lúc xuất ra `build/`.

## Ai viết mục nào

Mỗi mục là một file trong `sections/`, nên hai người sửa song song không bị xung đột. Đầu mỗi file ghi người viết, mục đề Lab 03 tương ứng và phần liên quan trong [PROJECT.md](../application/PROJECT.md).

| File | Mục | Người viết |
|---|---|---|
| `abstract.tex`, `introduction.tex`, `method.tex`, `conclusion.tex` | Abstract, I, III, VII | Huy |
| `related-work.tex` | II | Huy và Minh |
| `experimental-setup.tex`, `results.tex` | IV, V | Huy. Minh viết phần dữ liệu, baseline, chỉ số, kết quả chính của paper và hạn chế STS → tiếng Việt (3.2.4–3.2.6), cùng chi tiết D1/D2 |
| `application.tex`, `contributions.tex` | VI, Team Contributions | Minh |

`main.tex` chứa tiêu đề, tác giả, từ khóa và thứ tự các mục. Huy giữ file này.

## Quy ước

- **Ngôn ngữ.** Báo cáo viết bằng tiếng Anh (chốt 23/11). Tiếng Việt chỉ dùng cho tên riêng, trích nguyên văn Điều/Khoản và câu hỏi ví dụ. Preamble có `\usepackage[T5]{fontenc}`, nên gõ dấu trực tiếp trong file UTF-8 mà font vẫn là Times như mẫu.
- **Số liệu.** Chỉ lấy từ file kết quả trong `experiments/*/results/` và ghi đường dẫn file trong comment cạnh bảng.
- **Trích dẫn.** Xuất BibTeX từ nguồn gốc (ACL Anthology, DBLP, trang nhà xuất bản), dán vào `references.bib` và ghi URL nguồn phía trên entry. Mẫu gõ tay danh mục tham khảo, còn nhóm dùng `IEEEtran.bst` để ra cùng định dạng mà dễ quản lý hơn.
- **Hình.** Đặt trong `figures/` rồi gọi `\includegraphics{tên-file}`.
- **Ghi chú nháp.** `\TODO{...}` hiện chữ đỏ trong PDF. Chỉ nộp khi script báo `TODO notes left: 0`.
