"""Build the private Lab 03 submission, or verify every file in an existing ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import time
from io import BytesIO
from pathlib import Path, PurePosixPath
from tempfile import NamedTemporaryFile
from typing import BinaryIO
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
DELIVERY = ROOT / "outputs/submission"
ARCHIVE = DELIVERY / "[Group14].zip"
PREPARED = DELIVERY / "Ho-so-cho-video.zip"
TRANSCRIPT = "data/raw/d2/Quy_che_dao_tao_2026_QD3087_verified.md"
CORPUS = "data/processed/d2/corpus.jsonl"
MANIFEST = "SHA256SUMS.txt"

GUIDE = """Viết cho: {audience}

# SimCSE và ứng dụng tra cứu quy chế đào tạo HCMUS

1. Mở **Bao-cao.pdf** để đọc báo cáo IEEE. {media}
2. Giải nén toàn bộ gói. Trong thư mục **source**, làm theo [hướng dẫn mở ứng dụng](source/apps/README.md#chạy-cục-bộ). Corpus cả hai quy chế đã có sẵn ở `data/processed/d2/corpus.jsonl`. Lần đầu cần cài môi trường và tải checkpoint theo phiên bản đã ghim.
3. Xem [mã nguồn và kết quả thí nghiệm](source/README.md), [dữ liệu D1 theo phiên bản](source/experiments/external_dataset/README.md) và [bộ D2 công khai](source/data/d2/README.md#bộ-d2-công-khai). Thư mục source chứa phiên bản mã dùng để bàn giao. BASE_COMMIT.txt ghi commit nền, SHA256SUMS.txt nhận diện nội dung chính xác của từng tệp trong gói.
4. Để đối chiếu toàn bộ tệp với bảng SHA-256, giải nén tại thư mục đang chứa ZIP. {verification_setup}Chạy `python source/tools/package_submission.py verify {verify_args}`.

Bản ChatGPT chép từ scan của QĐ 3087 đã được nhóm hiệu đính theo PDF của Trường. Bản chép cùng corpus đầy đủ được cung cấp riêng trong bài nộp.
"""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_member(bundle: ZipFile, name: str, source: BinaryIO, size: int, timestamp: tuple,
                 compression: int = ZIP_DEFLATED) -> str:
    # The base commit time gives identical inputs a stable, meaningful archive date.
    entry = ZipInfo(name, date_time=timestamp)
    entry.create_system = 3
    entry.external_attr = 0o100644 << 16
    entry.compress_type = compression
    entry.file_size = size
    checksum = hashlib.sha256()
    with bundle.open(entry, "w") as dest:
        while block := source.read(1024 * 1024):
            dest.write(block)
            checksum.update(block)
    return checksum.hexdigest()


def verify_video(stream: BinaryIO) -> None:
    """Check the recording's MP4 container, video track and assignment duration limit."""
    try:
        from pymediainfo import MediaInfo
    except ImportError as exc:
        raise ValueError("Install pymediainfo==7.0.1 to check the final MP4 (see docs/README.md)") from exc
    media = MediaInfo.parse(stream)
    container = next(iter(media.general_tracks), None)
    if (not container or container.format != "MPEG-4" or container.is_truncated == "Yes"
            or (container.format_profile or "").startswith(("QuickTime", "3GPP"))
            or not any(t.width and t.height for t in media.video_tracks)):
        raise ValueError("Demo.mp4 must contain an MP4 video track")
    duration_ms = float(container.duration or 0)
    if not math.isfinite(duration_ms) or not 0 < duration_ms <= 30 * 60 * 1000:
        raise ValueError("Demo.mp4 must have a positive duration of at most 30 minutes")


def source_paths() -> list[Path]:
    public = ("README.md", "pyproject.toml", ".gitignore", ".gitattributes", "apps", "data",
              "docs", "experiments", "src", "tests", "tools")
    result = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", *public], cwd=ROOT)
    paths = [Path(os.fsdecode(entry)) for entry in result.split(b"\0") if entry]
    for path in paths:
        if (path.parts[:2] in {("data", "raw"), ("data", "processed")} or
                path.is_absolute() or not (ROOT / path).resolve().is_relative_to(ROOT)):
            raise ValueError(f"Unexpected source path: {path}")
    return sorted(p for p in paths if (ROOT / p).is_file())


def verify(archive: Path, *, prepared: bool = False) -> int:
    with ZipFile(archive) as bundle:
        names = bundle.namelist()
        required = {"README.md", "Bao-cao.pdf", MANIFEST,
                    "source/README.md", "source/BASE_COMMIT.txt", "source/apps/app.py",
                    "source/" + TRANSCRIPT, "source/" + CORPUS}
        if prepared:
            if {"Demo.mp4", "Demo.vi.vtt"}.intersection(names):
                raise ValueError("Unexpected video or captions in the pre-recording package")
        else:
            required.add("Demo.mp4")
        if len(names) != len(set(names)) or not required.issubset(names):
            raise ValueError("Missing or duplicate submission members")
        expected = {}
        for line in bundle.read(MANIFEST).decode("utf-8").splitlines():
            checksum, name = line.split("  ", 1)
            path = PurePosixPath(name)
            if name in expected or path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
                raise ValueError(f"Invalid manifest path: {name}")
            expected[name] = checksum
        if set(expected) != set(names) - {MANIFEST}:
            raise ValueError("Manifest does not cover the complete submission")
        for name, checksum in expected.items():
            actual = hashlib.sha256()
            with bundle.open(name) as member:
                while block := member.read(1024 * 1024):
                    actual.update(block)
            if actual.hexdigest() != checksum:
                raise ValueError(f"Checksum mismatch: {name}")
        if not prepared:
            with bundle.open("Demo.mp4") as recording:
                verify_video(recording)
        return len(expected)


def build(video: Path | None = None, captions: Path | None = None) -> None:
    import yaml

    documents = yaml.safe_load((ROOT / "data/d2/documents.yaml").read_bytes())["documents"]
    signed = next(d for d in documents if d["doc_id"] == "hcmus-qcdt-2026")
    measured = json.loads((ROOT / "experiments/application/results/E4/latency.json").read_bytes())
    if (signed["file"] != TRANSCRIPT or digest((ROOT / TRANSCRIPT).read_bytes()) != signed["sha256"]
            or digest((ROOT / CORPUS).read_bytes()) != measured["corpus_sha256"]):
        raise ValueError("Submission inputs differ from the verified regulation or measured corpus")
    files = {f"source/{p.as_posix()}": ROOT / p for p in source_paths()}
    files.update({"source/" + name: ROOT / name for name in (TRANSCRIPT, CORPUS)})
    files["Bao-cao.pdf"] = ROOT / "docs/report/build/main.pdf"
    if video is None:
        if captions is not None:
            raise ValueError("Captions require a recorded video")
        archive = PREPARED
        guide = GUIDE.format(audience="Nhóm 14, chuẩn bị bài nộp Lab 03", media="Đây là hồ sơ chờ Minh quay video.",
                             verify_args=f'--prepared "{archive.name}"', verification_setup="")
    else:
        if video.suffix.lower() != ".mp4" or not video.stat().st_size:
            raise ValueError("Expected a nonempty MP4 recording")
        archive = ARCHIVE
        files["Demo.mp4"] = video
        media = "Mở **Demo.mp4** để xem phần tra cứu và so sánh với BM25."
        if captions is not None:
            if not captions.read_text(encoding="utf-8-sig").startswith("WEBVTT"):
                raise ValueError("Expected WebVTT captions for this recording")
            files["Demo.vi.vtt"] = captions
            media += " Trình phát hỗ trợ WebVTT có thể nạp phụ đề **Demo.vi.vtt**."
        guide = GUIDE.format(audience="giảng viên chấm Lab 03, Nhóm 14", media=media,
                             verify_args=f'"{archive.name}"', verification_setup=(
                                 "Cài bộ đọc thông tin video bằng `python -m pip install pymediainfo==7.0.1`. "))
    revision, epoch = subprocess.check_output(["git", "show", "-s", "--format=%H%n%ct", "HEAD"], cwd=ROOT).splitlines()
    timestamp = time.gmtime(int(epoch))[:6]
    DELIVERY.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=DELIVERY, suffix=".part", delete=False) as tmp:
        pending = Path(tmp.name)
    try:
        hashes = {}
        with ZipFile(pending, "w", compression=ZIP_DEFLATED) as bundle:
            for name, path in sorted(files.items()):
                compression = ZIP_STORED if path.suffix.lower() in {".mp4", ".pdf", ".png"} else ZIP_DEFLATED
                with path.open("rb") as source:
                    hashes[name] = write_member(bundle, name, source, os.fstat(source.fileno()).st_size, timestamp, compression)
            for name, data in (("README.md", guide.encode("utf-8")), ("source/BASE_COMMIT.txt", revision + b"\n")):
                hashes[name] = write_member(bundle, name, BytesIO(data), len(data), timestamp)
            manifest = "".join(f"{h}  {n}\n" for n, h in sorted(hashes.items()))
            data = manifest.encode("utf-8")
            write_member(bundle, MANIFEST, BytesIO(data), len(data), timestamp)
        count = verify(pending, prepared=video is None)
        pending.replace(archive)
        print(f"{archive.name}: {count} file checksums verified")
    finally:
        pending.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("prepare", help="Prepare the report and sources before the demo is recorded")
    final = commands.add_parser("build", help="Build the submission with the selected recording")
    final.add_argument("--video", type=Path, required=True)
    final.add_argument("--captions", type=Path, help="Optional WebVTT for this recording")
    verifier = commands.add_parser("verify", help="Check all members against SHA256SUMS.txt")
    verifier.add_argument("archive", type=Path)
    verifier.add_argument("--prepared", action="store_true", help="Verify the pre-recording package")
    args = parser.parse_args()
    if args.action == "prepare":
        build()
    elif args.action == "build":
        build(args.video, args.captions)
    else:
        print(f"{args.archive.name}: {verify(args.archive, prepared=args.prepared)} file checksums verified")
