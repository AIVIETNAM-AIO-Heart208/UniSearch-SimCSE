Viết cho: Minh

# Cấu hình truy hồi đã chốt trên D1-dev

| Tham số | Giá trị | Cách chọn |
|---|---:|---|
| `--weight` | `0.6` | Trọng số BM25 có MRR@10 cao nhất trong 11 mức từ 0,0 đến 1,0, bước 0,1 |
| `--threshold` | `0.6201629042625427` | Cosine lớn nhất giữ ít nhất 80% câu ở mức tin cậy sau khi chốt trọng số |

Từ gốc repo, chạy trong môi trường demo khi đã dựng corpus HCMUS đủ hai quy chế.

```powershell
python apps/app.py --model-path outputs/d1-model --corpus data/processed/d2/corpus.jsonl `
  --weight '0.6' --threshold '0.6201629042625427'
```

## Kết quả trên 224 câu D1-dev

| Phương pháp | Hit@1 | Hit@3 | MRR@10 |
|---|---:|---:|---:|
| SimCSE-VN | 46,43% | 65,63% | 0,582836 |
| BM25 | 66,52% | 80,80% | 0,749676 |
| Hybrid, trọng số 0,5 | 66,52% | 86,16% | 0,768789 |
| **Hybrid, trọng số 0,6** | **69,64%** | **85,27%** | **0,782898** |

Ngưỡng giữ **180/224 câu (80,36%)** ở mức tin cậy và cảnh báo 44 câu. Bảng điểm đầu vào gồm cả điểm BM25 và cosine của 955 chunk thuộc 297 đoạn nguồn cho từng câu. Lượt chạy dùng checkpoint `608779b`, CPU bốn luồng và batch 16. Xem đủ 11 mức trọng số, phiên bản môi trường và mã kiểm tra tệp trong [summary.json](summary.json).

Giữ nguyên hai tham số khi đánh giá D1-test và D2. Lượt đánh giá D2 dùng bộ nhãn mà hai thành viên đã thống nhất.
