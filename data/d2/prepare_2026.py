"""Apply corrections checked against the signed QD 3087 PDF to the local D2 corpus."""

import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory


RAW = Path(__file__).resolve().parents[1] / "raw" / "d2"
BASE = RAW / "Quy_che_dao_tao_2026_QD3087_clean.md"
TARGET = RAW / "Quy_che_dao_tao_2026_QD3087_verified.md"
BASE_SHA256 = "e8415f9d8c4bbf2c2dcc33aae0380f404cd3a180f3a4124a67a92b2dc852d478"
TARGET_SHA256 = "caee800b1a10a3ad929b15d1dbc212b3c651520134336eb50df2611ce792f916"

# In PDF order (physical pages 4, 8, 9, 12, 14, 15 and 20).
CORRECTIONS = (
    ("học phần/s6 tín chỉ", "học phần/số tín chỉ"),
    ("học phần mà sinh |\n\nviên phải", "học phần mà sinh viên phải"),
    ("tín chỉ trong đương", "tín chỉ tương đương"),
    ("cử nhân tài.\n\nnăng)", "cử nhân tài năng)"),
    ("phương thức t6 chức", "phương thức tổ chức"),
    ("giải trình, khác phục", "giải trình, khắc phục"),
    ("ít nhất 1 10 tín chỉ", "ít nhất 110 tín chỉ"),
    ("Giáo dục quốc phòng\n\n- an ninh", "Giáo dục quốc phòng - an ninh"),
    (
        "Chủ tịch Hội đồng không được đồng thời là giảng viên hướng dẫn đối với sinh viên có đề "
        "tài được Hội đồng xem xét, đánh giá khóa luận tốt nghiệp, thực tập tốt nghiệp, dự án "
        "tốt nghiệp, đồ án tốt nghiệp.\n\n3. Trường hợp đặc biệt",
        "Thành viên Hội đồng không đồng thời là giảng viên hướng dẫn hoặc giảng viên phản biện. "
        "Trường hợp đặc biệt",
    ),
    ("4. Điểm đánh giá khóa luận tốt nghiệp", "3. Điểm đánh giá khóa luận tốt nghiệp"),
    (
        "điểm chính thức của học phần -\n\nvà trọng số",
        "điểm chính thức của học phần và trọng số",
    ),
    (
        "điểm trung bình tích lũy (làm tròn đến hàng phần trăm) được sử dụng",
        "điểm trung bình tích lũy được sử dụng",
    ),
    ("Bị cảnh báo học tập ba lần liên tiếp", "Bị cảnh báo học tập quá ba lần liên tiếp"),
    (
        "cấp bằng tốt nghiệp chương trình thứ hai được quy định tại",
        "cấp bằng tốt nghiệp chương trình thứ hai theo quy định tại",
    ),
)


def prepare(source: Path, target: Path) -> None:
    """Verify the input and output bytes, then publish the corrected copy atomically."""
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != BASE_SHA256:
        raise ValueError("Unexpected base transcription SHA-256")
    text = data.decode("utf-8")
    for old, new in CORRECTIONS:
        if text.count(old) != 1:
            raise ValueError(f"Expected exactly one occurrence of {old!r}")
        text = text.replace(old, new)
    corrected = text.encode("utf-8")
    if hashlib.sha256(corrected).hexdigest() != TARGET_SHA256:
        raise ValueError("Unexpected corrected transcription SHA-256")
    if target.exists():
        if target.read_bytes() != corrected:
            raise ValueError("Destination already contains different data")
        return
    with TemporaryDirectory(dir=target.parent) as temp:
        staged = Path(temp) / target.name
        staged.write_bytes(corrected)
        staged.replace(target)


if __name__ == "__main__":
    prepare(BASE, TARGET)
    print(f"{TARGET_SHA256}  {TARGET.name}")
