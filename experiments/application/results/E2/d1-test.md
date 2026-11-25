# E2 theo mức trùng từ trên D1-test

So sánh dùng ba bảng xếp hạng đã lưu của [E1](../../../external_dataset/results/E1/d1-test.json), với `--weight 0.6` và `--threshold 0.6201629042625427`. Các tệp đầu vào được kiểm SHA-256. Toàn bộ 759 câu D1-test có nhãn đoạn chuẩn và mỗi câu thuộc đúng một nhóm.

## Cách chia nhóm

Jaccard (J) bằng số token chung chia cho số token phân biệt trong hợp của hai tập. Hai tập lấy từ câu hỏi và **toàn bộ đoạn chuẩn** trong CSV. Cả hai văn bản dùng bước chuẩn hóa và tách từ Pyvi sẵn có của repo, chuyển chữ thường, bỏ token chỉ gồm dấu câu hoặc ký hiệu, giữ các token có chữ hoặc số.

Hai mốc là phân vị 1/3 và 2/3, nội suy tuyến tính trên phân bố Jaccard của D1-test. Những câu cùng điểm Jaccard thuộc cùng nhóm. Mốc được tính từ nội dung câu hỏi và đoạn chuẩn trước khi dùng thứ hạng để chấm chỉ số.

| Mức trùng từ | Số câu | Quy tắc | Khoảng Jaccard thực đo | Trung vị số token phân biệt của đoạn chuẩn |
|---|---:|---|---|---:|
| Thấp | 253 | J ≤ 0,07230059685295713 | 0,014235–0,072165 | 129 |
| Vừa | 253 | 0,07230059685295713 < J ≤ 0,12269667880392805 | 0,072368–0,122642 | 90 |
| Cao | 253 | J > 0,12269667880392805 | 0,122807–0,772727 | 55 |

## Chỉ số theo nhóm

Hit@k là tỷ lệ câu tìm được đoạn chuẩn trong k vị trí đầu. MRR@10 tính trung bình nghịch đảo hạng của đoạn chuẩn và dùng 0 nếu đoạn chuẩn nằm ngoài top 10.

| Mức trùng từ | Số câu | Phương pháp | Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR@10 |
|---|---:|---|---:|---:|---:|---:|---:|
| Thấp | 253 | BM25 | 50,99% | 77,87% | 84,98% | 90,91% | 0,655681 |
| Thấp | 253 | SimCSE-VN | 35,57% | 57,31% | 71,54% | 81,82% | 0,497274 |
| Thấp | 253 | Hybrid | 55,73% | 82,21% | 88,14% | 93,68% | 0,697712 |
| Vừa | 253 | BM25 | 75,49% | 88,93% | 92,09% | 96,05% | 0,826705 |
| Vừa | 253 | SimCSE-VN | 43,08% | 66,80% | 73,91% | 84,98% | 0,565683 |
| Vừa | 253 | Hybrid | 75,89% | 89,33% | 92,89% | 95,65% | 0,830439 |
| Cao | 253 | BM25 | 84,58% | 93,68% | 96,84% | 97,23% | 0,892989 |
| Cao | 253 | SimCSE-VN | 59,29% | 77,08% | 85,77% | 90,51% | 0,701531 |
| Cao | 253 | Hybrid | 85,77% | 94,47% | 96,84% | 98,02% | 0,904188 |

## Hybrid so với BM25

Mỗi khoảng tin cậy 95% lấy từ 1.000 mẫu bootstrap ghép cặp có hoàn lại theo câu hỏi trong cùng nhóm, seed 42. Hai cận là phân vị 2,5% và 97,5% với nội suy tuyến tính. Chênh lệch tính trên điểm chưa làm tròn.

| Mức trùng từ | ΔHit@1 (điểm phần trăm) | Khoảng tin cậy 95% | ΔMRR@10 | Khoảng tin cậy 95% |
|---|---:|---:|---:|---:|
| Thấp | +4,74 | +0,79 đến +8,70 | +0,042031 | +0,018749 đến +0,065467 |
| Vừa | +0,40 | −2,37 đến +3,16 | +0,003735 | −0,012522 đến +0,020024 |
| Cao | +1,19 | −0,79 đến +3,16 | +0,011199 | −0,000464 đến +0,023058 |

Hybrid có MRR@10 cao hơn BM25 ở cả ba nhóm. Mức tăng quan sát được lớn nhất ở nhóm thấp với **+0,042031 MRR@10** và **+4,74 điểm phần trăm Hit@1**. Cả hai khoảng tin cậy của nhóm thấp nằm trên 0. Hai khoảng của mỗi nhóm vừa và cao đều chứa 0. SimCSE-VN đứng sau BM25 về Hit@1 và MRR@10 ở cả ba nhóm.

Trung vị số token phân biệt của đoạn chuẩn được tính theo từng câu hỏi. Nhóm thấp có trung vị cao nhất. Đoạn dài làm mẫu số Jaccard lớn hơn, nên điểm Jaccard thấp có thể phản ánh độ dài đoạn chuẩn cùng với khác biệt từ vựng.

[Dữ liệu kết quả và mã câu theo nhóm](d1-test.json) lưu các mốc, điểm chưa làm tròn, khoảng tin cậy, checksum và cấu hình thực chạy. Tính lại độc lập từ xếp hạng đã xác nhận 45 ô chỉ số và cả sáu khoảng tin cậy. Trung bình có trọng số theo số câu tái tạo đúng kết quả chung của E1. [Lệnh tái lập E2](../../README.md#e2-trên-d1-test)
