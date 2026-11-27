"""Exercise the same entry points in a source folder without Git metadata."""

import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile

import pytest


def test_export_docs_follow_links_and_skip_private_inputs(tmp_path):
    script = Path(__file__).resolve().parents[1] / "tools/check_docs.py"
    readme = tmp_path / "README.md"
    readme.write_text("[Section](docs/guide.md#install)", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    guide = tmp_path / "docs/guide.md"
    guide.write_text("# Setup", encoding="utf-8")
    private = tmp_path / "data/raw/transcript.md"
    private.parent.mkdir(parents=True)
    private.write_text("[Editorial marker](missing)", encoding="utf-8")
    command = [sys.executable, "-X", "utf8", str(script)]
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 1 and "missing anchor" in result.stdout
    guide.write_text("# Install", encoding="utf-8")
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0 and "checked 2 Markdown files" in result.stdout


def test_export_corpus_stays_in_generated_directories(tmp_path, monkeypatch):
    scripts = Path(__file__).resolve().parents[1] / "experiments/external_dataset"
    monkeypatch.syspath_prepend(str(scripts))
    from run_retrieval import checked_corpus_output

    assert checked_corpus_output(tmp_path, Path("data/processed/rebuilt")) == tmp_path / "data/processed/rebuilt"
    with pytest.raises(ValueError, match="Git-ignored"):
        checked_corpus_output(tmp_path, Path("outputs/../data/raw"))
    with pytest.raises(ValueError, match="inside"):
        checked_corpus_output(tmp_path, Path("../outside"))


@pytest.mark.parametrize("prepared", [False, True])
def test_submission_verifies_members_and_rejects_modified_ones(tmp_path, prepared, monkeypatch):
    from tools import package_submission
    from tools.package_submission import CORPUS, MANIFEST, TRANSCRIPT, verify

    checked = []
    monkeypatch.setattr(package_submission, "verify_video", lambda stream: checked.append(stream.read()))

    names = ["README.md", "Bao-cao.pdf", "source/README.md", "source/BASE_COMMIT.txt",
             "source/apps/app.py", "source/" + TRANSCRIPT, "source/" + CORPUS]
    if not prepared:
        names.append("Demo.mp4")
    manifest = "".join(f"{sha256(n.encode()).hexdigest()}  {n}\n" for n in names)
    archive = tmp_path / "submission.zip"
    for modified in (False, True):
        with ZipFile(archive, "w") as bundle:
            for name in names:
                payload = "edited" if modified and name == names[-1] else name
                bundle.writestr(name, payload)
            bundle.writestr(MANIFEST, manifest)
        if modified:
            with pytest.raises(ValueError, match="Checksum mismatch"):
                verify(archive, prepared=prepared)
        else:
            assert verify(archive, prepared=prepared) == len(names)
            assert checked == ([] if prepared else [b"Demo.mp4"])
            with pytest.raises(ValueError, match="Missing|Unexpected video"):
                verify(archive, prepared=not prepared)


def test_submission_rejects_text_with_a_video_filename(tmp_path):
    pytest.importorskip("pymediainfo")
    from tools.package_submission import verify_video

    recording = tmp_path / "Demo.mp4"
    recording.write_bytes(b"plain text with an MP4 filename")
    with recording.open("rb") as stream, pytest.raises(ValueError, match="MP4 video track"):
        verify_video(stream)


@pytest.mark.parametrize(("duration", "expected"), [(0, False), (1800000, True), (1800001, False)])
def test_submission_checks_recording_duration(monkeypatch, duration, expected):
    from io import BytesIO
    from types import SimpleNamespace

    media = pytest.importorskip("pymediainfo")
    from tools.package_submission import verify_video

    metadata = SimpleNamespace(general_tracks=[SimpleNamespace(format="MPEG-4", format_profile="Base Media",
                                                                is_truncated=None, duration=duration)],
                               video_tracks=[SimpleNamespace(width=1280, height=720)])
    monkeypatch.setattr(media.MediaInfo, "parse", lambda stream: metadata)
    if expected:
        verify_video(BytesIO())
        for profile in ("QuickTime", "3GPP Media Release 4"):
            metadata.general_tracks[0].format_profile = profile
            with pytest.raises(ValueError, match="MP4 video track"):
                verify_video(BytesIO())
    else:
        with pytest.raises(ValueError, match="at most 30 minutes"):
            verify_video(BytesIO())


def test_export_provenance_uses_recorded_base_and_has_no_worktree(tmp_path, monkeypatch):
    from simcse_lab.provenance import base_commit, working_tree_status

    monkeypatch.chdir(tmp_path)
    recorded = tmp_path / "BASE_COMMIT.txt"
    recorded.write_text("f" * 40 + "\n", encoding="ascii")
    assert base_commit() == "f" * 40
    assert working_tree_status([Path("apps/app.py")]) is None
    recorded.write_text("unknown", encoding="ascii")
    with pytest.raises(ValueError, match="Invalid Git base"):
        base_commit()
