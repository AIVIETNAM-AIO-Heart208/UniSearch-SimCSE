# Kiểm chứng xếp hạng BM25 trên D1-dev

E0 dùng 224 câu D1-dev và điểm BM25 của toàn bộ 955 chunk thuộc 297 đoạn nguồn. Gói xếp hạng [D1-dev-retrieval-check](../D1-dev-retrieval-check/manifest.json) đã qua `verify-d1-dev`. BM25 đạt Hit@1 **0,665179**, Hit@3 **0,808036** và MRR@10 **0,749676**.

## Đối chiếu câu 9542

Câu hỏi về việc dừng giữa chừng khi làm khóa luận thuộc nhóm ghim vào D1-dev. Sau tách từ Pyvi và chuyển chữ thường, các mục truy vấn là `việc_làm`, `kltn`, `có_thể`, `bị`, `dừng`, `giữa_chừng`, `không` và `?`. Tính lại điểm bằng BM25Okapi với `k1=1.5`, `b=0.75` và `epsilon=0.25`. Corpus có 955 chunk và độ dài trung bình 63,378010 mục tách theo khoảng trắng.

Với mỗi mục truy vấn xuất hiện `tf` lần trong chunk, phần điểm là `IDF × tf × (k1 + 1) / (tf + k1 × (1 − b + b × độ dài / độ dài trung bình))`. `IDF` dùng số chunk chứa mục đó. Với các mục trong bảng, `IDF = ln((955 − df + 0.5) / (df + 0.5))`.

| Chunk tốt nhất trong đoạn | Độ dài | Mục khớp, kèm số lần xuất hiện trong chunk | Điểm từng mục theo thứ tự | Tổng điểm | Hạng đoạn |
|---|---:|---|---|---:|---:|
| `0719a4866265:0001` | 88 | `việc_làm` (1), `bị` (2), `không` (2) | 4,772064 + 3,491113 + 1,851354 | 10,114531 | 1 |
| `afa5630168e4:0000` (đoạn chuẩn) | 152 | `kltn` (5), `bị` (2), `không` (2) | 5,915723 + 2,709333 + 1,436773 | 10,061829 | 2 |

Số chunk chứa `việc_làm`, `kltn`, `bị` và `không` lần lượt là 3, 20, 57 và 180. Mã chunk trong bảng dùng 12 ký tự đầu của mã đoạn và số thứ tự chunk. MaxP lấy điểm cao nhất của các chunk trong cùng đoạn. Phép tính độc lập từ token và tần suất cho đủ 955 điểm khớp bảng điểm D1-dev với sai số tuyệt đối dưới `1e-10`. Top 20 mã đoạn của câu 9542 khớp [xếp hạng BM25 đã lưu](../D1-dev-retrieval-check/runs/bm25.jsonl).

Lượt đối chiếu dùng Python 3.14.0, pyvi 0.1.1 và rank-bm25 0.2.2 trên CPU. [Manifest chọn cấu hình](../D1-dev-tuning/summary.json) ghi mã commit, checksum CSV, môi trường và SHA-256 của `outputs/d1-dev-tuning/scores.npz`. [Hướng dẫn kiểm lại gói D1-dev](../../README.md#bàn-giao-cho-huy).
