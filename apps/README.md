# Tra cứu quy chế đào tạo HCMUS

Demo Gradio dùng chung bộ truy hồi với CLI. Giao diện hiển thị tối đa ba chủ đề, Điều/Khoản, trích đoạn, thông tin và phạm vi áp dụng của văn bản, kèm tab đối chiếu BM25. Kết quả của QĐ 3087 ghi nguồn là bản ChatGPT chép từ scan, nhóm đã hiệu đính.

Tạo lại corpus để nạp tiêu đề đầy đủ, trạng thái thay thế và liên kết sửa đổi QĐ 91/2023 của Điều 15 bản 2021.

Từ gốc repo, chuẩn bị [checkpoint D1 và corpus HCMUS đủ hai phiên bản](../experiments/external_dataset/README.md#lệnh-chuẩn-bị-hcmus-và-đánh-giá-d2). Nếu đã có môi trường demo, đặt `$d1Python` thành đường dẫn Python của môi trường đó. Để tạo môi trường riêng trên Windows, dùng Python 3.11. Trên máy Huy, pip với Python 3.14 không tìm được bộ wheel tương thích cho Gradio 5.49.1 và `pydantic-core`.

```powershell
py -3.11 -m venv outputs/demo-venv
$d1Python = '.\outputs\demo-venv\Scripts\python.exe'
```

Cài các phần phụ thuộc vào môi trường vừa chọn rồi mở địa chỉ cục bộ mà Gradio in ra.

```powershell
& $d1Python -m pip install -e ".[test,retrieval,demo]"
& $d1Python apps/app.py --model-path outputs/d1-model --corpus data/processed/d2/corpus.jsonl `
  --weight '0.6' --threshold '0.6201629042625427'
```

Hai tham số lấy từ [cấu hình đã chốt trên D1-dev](../experiments/external_dataset/results/D1-dev-tuning/handoff.md). Khi bỏ trọng số, tab tra cứu dùng dense SimCSE-VN. Khi bỏ ngưỡng, giao diện báo chưa cấu hình cảnh báo. Thông báo trên cả hai tab ghi tên phương pháp có trích đoạn hạng đầu được chấm độ tin cậy. Để kiểm thử giao diện bằng corpus giả lập và endpoint Gradio cục bộ, chạy:

```powershell
& $d1Python -m pytest -q tests/test_retrieval_app.py
```
