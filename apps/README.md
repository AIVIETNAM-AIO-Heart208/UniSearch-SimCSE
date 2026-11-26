# Tra cứu quy chế đào tạo HCMUS

Demo Gradio dùng chung bộ truy hồi với CLI. Giao diện hiển thị tối đa ba chủ đề, Điều/Khoản, trích đoạn, thông tin và phạm vi áp dụng của văn bản, kèm tab đối chiếu BM25. Kết quả của QĐ 3087 ghi nguồn là bản ChatGPT chép từ scan, nhóm đã hiệu đính.

Tạo lại corpus để nạp tiêu đề đầy đủ, trạng thái thay thế và liên kết sửa đổi QĐ 91/2023 của Điều 15 bản 2021.

Từ gốc repo, dùng [môi trường và checkpoint D1](../experiments/external_dataset/README.md) rồi chuẩn bị corpus HCMUS đủ hai phiên bản theo hướng dẫn bên đó.

```powershell
& $d1Python -m pip install -e ".[retrieval,demo]"
& $d1Python apps/app.py --model-path outputs/d1-model --corpus data/processed/d2/corpus.jsonl `
  --weight '0.6' --threshold '0.6201629042625427'
```

Mở địa chỉ cục bộ Gradio in ra. Hai tham số lấy từ [cấu hình đã chốt bằng D1-dev](../experiments/external_dataset/results/D1-dev-tuning/handoff.md). Khi chưa truyền trọng số, tab tra cứu dùng dense SimCSE-VN. Giao diện báo trạng thái khi chưa cấu hình ngưỡng.

Kiểm thử giao diện bằng corpus giả lập và endpoint Gradio cục bộ.

```powershell
& $d1Python -m pip install -e ".[test]"
& $d1Python -m pytest -q tests/test_retrieval_app.py
```
