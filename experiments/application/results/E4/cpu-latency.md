# E4 · Độ trễ truy hồi trên CPU

Đo ngày 26/11/2026 trên Windows với AMD Ryzen 7 7735HS, PyTorch 2.14.1, 4 luồng Torch và checkpoint đã ghim. Corpus HCMUS gồm 51 Điều, 26 chủ đề và 273 đoạn truy hồi. Hybrid dùng trọng số 0,6 và cấu hình demo dùng ngưỡng 0,6201629042625427.

[Mẫu đo gốc](latency.json) gồm thời gian từng truy vấn, cấu hình máy và checksum corpus. Mỗi phương pháp chạy 6 câu thử ngoài D2, làm nóng mỗi câu một lần rồi đo 10 lượt, tổng cộng 60 mẫu mỗi phương pháp. Benchmark xóa bộ nhớ đệm token của encoder trước mỗi mẫu. Thời gian dựng chỉ mục dùng chung là 40,51 giây, gồm lập chỉ mục BM25 và mã hóa corpus sau khi đã nạp model.

| Phương pháp | Truy hồi p50 / p95 (ms) | Tách từ p50 / p95 (ms) | Encode p50 / p95 (ms) | Tìm kiếm p50 / p95 (ms) |
|---|---:|---:|---:|---:|
| BM25 | 0,79 / 1,07 | 0,19 / 0,28 | 0,00 / 0,00 | 0,59 / 0,81 |
| SimCSE-VN | 29,39 / 36,03 | 0,18 / 0,26 | 28,91 / 35,47 | 0,25 / 0,31 |
| Hybrid | 30,31 / 34,88 | 0,55 / 0,66 | 28,69 / 32,96 | 1,14 / 1,53 |

Phép đo kết thúc sau khi xếp hạng. Chi phí trình bày giao diện và truyền qua HTTP nằm ngoài phép đo. Mỗi cột tính phân vị riêng trên 60 mẫu. Kiểm tra riêng qua API Gradio trên localhost cho thấy cả 6 câu đều trả về ba nhóm kết quả và kết quả đối chiếu BM25. Có 2 câu hiện cảnh báo độ tin cậy thấp.

Chạy từ thư mục gốc sau khi dựng corpus và kích hoạt môi trường của ứng dụng.

```powershell
$env:PYTHONPATH = 'src'
python -m experiments.application.benchmark_cpu --demo --output outputs/e4-cpu/latency.json
```

Lệnh ghi mẫu đo thô, checksum corpus và bảng phân vị vào `outputs/e4-cpu/latency.json`, cùng phản hồi kiểm tra Gradio trong `outputs/e4-cpu/demo-check.json`.
