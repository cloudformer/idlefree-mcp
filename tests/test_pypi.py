"""Offline tests: PyPI answered by a fake urlopen, uploads never leave the process."""
import io
import json
import urllib.error
import zipfile

import pytest

from idlefree_mcp.tools import pypi


def fake_urlopen(taken_names, fail_upload=None):
    """taken: {name: urls-string}; fail_upload: (code, reason) to refuse uploads with."""
    def opener(req, timeout=0):
        url = getattr(req, "full_url", req)
        if url.startswith(pypi.UPLOAD):
            if fail_upload:
                raise urllib.error.HTTPError(url, fail_upload[0], fail_upload[1], {}, io.BytesIO(b""))
            return io.BytesIO(b"OK")
        name = url.split("/pypi/")[1].split("/")[0]
        if name in taken_names:
            body = {"info": {"home_page": taken_names[name], "project_urls": None}}
            return io.BytesIO(json.dumps(body).encode())
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, io.BytesIO(b""))
    return opener


def test_check_three_verdicts(monkeypatch):
    monkeypatch.setenv("IDLEFREE_OWNER", "exampleorg")
    monkeypatch.setattr(pypi.urllib.request, "urlopen", fake_urlopen(
        {"mine": "https://github.com/exampleorg/mine", "theirs": "https://example.com"}))
    out = pypi.check(["mine", "theirs", "freename123"])
    assert "mine: " in out and "already registered by you" in out
    assert "taken by someone else" in out
    assert "Available, no release on PyPI" in out


def test_check_rejects_bad_names():
    with pytest.raises(ValueError):
        pypi.check(["-bad-"])


def test_wheel_is_a_valid_zip(tmp_path):
    c = pypi.settings(owner="exampleorg")
    fields, meta = pypi.metadata("some-name", c)
    path = pypi.wheel("some-name", fields, meta, str(tmp_path))
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        assert "some_name/__init__.py" in names
        assert any(n.endswith("METADATA") for n in names)
        assert "github.com/exampleorg/some-name" in z.read("some_name-0.0.1.dist-info/METADATA").decode()


def test_register_success_and_ledger(monkeypatch, tmp_path):
    log = tmp_path / "reserved.yaml"
    monkeypatch.setenv("IDLEFREE_OWNER", "exampleorg")
    monkeypatch.setenv("PYPI_TOKEN", "pypi-faketoken")
    monkeypatch.setattr(pypi.urllib.request, "urlopen", fake_urlopen({}))
    out = pypi.register(["freename123"], log_path=str(log))
    assert "registered successfully!" in out
    saved = log.read_text()
    assert "registered:" in saved and "freename123" in saved


def test_register_refused_name_goes_to_failed(monkeypatch, tmp_path):
    log = tmp_path / "reserved.yaml"
    monkeypatch.setenv("IDLEFREE_OWNER", "exampleorg")
    monkeypatch.setenv("PYPI_TOKEN", "pypi-faketoken")
    monkeypatch.setattr(pypi.urllib.request, "urlopen",
                        fake_urlopen({}, fail_upload=(400, "The name 'freename123' isn't allowed. See https://example.com")))
    out = pypi.register(["freename123"], log_path=str(log))
    assert "registration failed!" in out and "isn't allowed" in out
    assert "freename123" in pypi.load_log(str(log))["failed"]


def test_register_requires_owner(monkeypatch):
    monkeypatch.delenv("IDLEFREE_OWNER", raising=False)
    assert "set IDLEFREE_OWNER" in pypi.register(["anything"])


def test_log_roundtrip(tmp_path):
    path = str(tmp_path / "r.yaml")
    log = {"registered": {"a": ""}, "failed": {"b": "too similar"}}
    pypi.save_log(log, path)
    assert pypi.load_log(path) == log
