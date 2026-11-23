# Tái hiện kết quả SimCSE

Chọn một hàng, cột và bảng cụ thể trong paper. Ví dụ, Bảng 5 báo cáo **76,85** cho unsupervised SimCSE-BERT-base trên **STS-B test**, theo Spearman × 100. Đây là mốc tham khảo từ paper. Ghi riêng kết quả nhóm thực sự đo được.

Lưu tại đây cấu hình, entry point hoặc lệnh chạy từ thư mục gốc, phiên bản checkpoint, thiết lập pooling, tập chia, môi trường và kết quả. Ghi rõ phạm vi nhóm tái hiện, chẳng hạn đánh giá checkpoint công khai hay huấn luyện lại mô hình. Đối với STS, tính cosine cho từng cặp câu rồi tính Spearman giữa các điểm cosine và nhãn trên toàn tập đánh giá.
