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
def test_submission_verifies_members_and_rejects_modified_ones(tmp_path, prepared):
    from tools.package_submission import CORPUS, MANIFEST, TRANSCRIPT, verify

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
            with pytest.raises(ValueError, match="Missing|Unexpected video"):
                verify(archive, prepared=not prepared)


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
