"""Check and reserve PyPI names: one 0.0.1 release per reserved name whose page is the name and
the repository link — nothing else. Standard library only (no build, no twine).

Ported from the IdleFree series' reserve script, with the owner parameterized:

    IDLEFREE_OWNER         your GitHub user/org — reserve() requires it; check() uses it to tell
                           "already registered by you" from "taken by someone else"
    IDLEFREE_AUTHOR        the Author field on the placeholder (default: the owner)
    IDLEFREE_RESERVED_LOG  optional path to a reserved.yaml ledger; unset = no ledger
    PYPI_TOKEN             the upload token, or the [pypi] password in ~/.pypirc

A name already on PyPI is skipped. PyPI may still refuse a free-looking name (prohibited, or too
similar to an existing project) — only the upload tells for sure. A reserved name needs a real
repository and release later (PEP 541); the page links the repository it will live in.
"""
import base64
import configparser
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
import uuid
import zipfile

UPLOAD = "https://upload.pypi.org/legacy/"
NAME_RE = r"[A-Za-z0-9][A-Za-z0-9._-]*[A-Za-z0-9]|[A-Za-z0-9]"


def settings(owner=None, author=None, log=None):
    owner = owner or os.environ.get("IDLEFREE_OWNER", "")
    return {"owner": owner,
            "author": author or os.environ.get("IDLEFREE_AUTHOR") or owner,
            "log": log or os.environ.get("IDLEFREE_RESERVED_LOG", ""),
            "version": "0.0.1"}


def valid(names):
    bad = [n for n in names if not re.fullmatch(NAME_RE, n)]
    if not names or bad:
        raise ValueError(f"names: give them separated by spaces, e.g. ztna bao1 bao2 (invalid: {bad})")
    return list(names)


def on_pypi(name):
    """None when free; else the project's homepage / repository URLs (to tell yours from someone else's)."""
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json", timeout=20) as r:
            info = json.load(r)["info"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    return " ".join([info.get("home_page") or ""] + list((info.get("project_urls") or {}).values()))


def page(name, c):
    repo = f"https://github.com/{c['owner']}/{name}"
    return f"# {name}\n\nReserved name, planned project.\n\n{repo}\n"


def metadata(name, c):
    version = c["version"]
    fields = {
        "metadata_version": "2.1", "name": name, "version": version,
        "summary": f"Reserved for https://github.com/{c['owner']}/{name}",
        "author": c["author"], "license": "MIT", "requires_python": ">=3.9",
        "description_content_type": "text/markdown", "description": page(name, c),
        "classifiers": ["Development Status :: 1 - Planning", "License :: OSI Approved :: MIT License",
                        "Programming Language :: Python :: 3"],
        "project_urls": [f"Homepage, https://github.com/{c['owner']}/{name}"],
    }
    text = "".join([
        "Metadata-Version: 2.1\n", f"Name: {name}\n", f"Version: {version}\n", f"Summary: {fields['summary']}\n",
        f"Author: {c['author']}\n", "License: MIT\n",
        *[f"Project-URL: {u}\n" for u in fields["project_urls"]],
        *[f"Classifier: {k}\n" for k in fields["classifiers"]],
        f"Requires-Python: {fields['requires_python']}\n", "Description-Content-Type: text/markdown\n",
        "\n", fields["description"]])
    return fields, text


def wheel(name, fields, meta_text, out_dir):
    """A py3-none-any wheel with one module that says what the project is."""
    module, version = re.sub(r"[-.]+", "_", name).lower(), fields["version"]
    dist = f"{module}-{version}.dist-info"
    files = {
        f"{module}/__init__.py": f'"""{name}: reserved name, planned project. {fields["project_urls"][0].split(", ")[1]}"""\n'
                                 f'__version__ = "{version}"\n',
        f"{dist}/METADATA": meta_text,
        f"{dist}/WHEEL": "Wheel-Version: 1.0\nGenerator: idlefree-mcp\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
        f"{dist}/top_level.txt": module + "\n",
    }
    record_lines = []
    for path, text in files.items():
        data = text.encode()
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
        record_lines.append(f"{path},sha256={digest},{len(data)}")
    files[f"{dist}/RECORD"] = "\n".join(record_lines + [f"{dist}/RECORD,,"]) + "\n"
    path = os.path.join(out_dir, f"{module}-{version}-py3-none-any.whl")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for p, text in files.items():
            z.writestr(p, text)
    return path


def token():
    if os.environ.get("PYPI_TOKEN"):
        return os.environ["PYPI_TOKEN"]
    rc = configparser.ConfigParser()
    rc.read(os.path.expanduser("~/.pypirc"))
    if rc.has_option("pypi", "password"):
        return rc.get("pypi", "password")
    raise RuntimeError("no token: set PYPI_TOKEN or the [pypi] password in ~/.pypirc")


def upload(path, fields, tok):
    with open(path, "rb") as f:
        content = f.read()
    form = dict(fields, **{":action": "file_upload", "protocol_version": "1", "filetype": "bdist_wheel",
                           "pyversion": "py3", "sha256_digest": hashlib.sha256(content).hexdigest()})
    boundary = uuid.uuid4().hex
    body = io.BytesIO()
    for key, value in form.items():
        for v in (value if isinstance(value, list) else [value]):
            body.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{v}\r\n'.encode())
    body.write(f'--{boundary}\r\nContent-Disposition: form-data; name="content"; filename="{os.path.basename(path)}"\r\n'
               "Content-Type: application/octet-stream\r\n\r\n".encode() + content + f"\r\n--{boundary}--\r\n".encode())
    auth = base64.b64encode(f"__token__:{tok}".encode()).decode()
    req = urllib.request.Request(UPLOAD, data=body.getvalue(), method="POST", headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}", "Authorization": f"Basic {auth}"})
    try:
        urllib.request.urlopen(req, timeout=60)
        return None
    except urllib.error.HTTPError as e:
        # PyPI puts its message in the status line ("400 The name 'x' isn't allowed. See ..."); the body repeats it
        reason = str(e.reason)
        if reason in ("Bad Request", "Forbidden", ""):
            lines = [ln.strip() for ln in e.read().decode(errors="replace").splitlines() if ln.strip()]
            reason = lines[-1] if lines else reason
        return e.code, reason.split(" See ")[0].strip()


def load_log(path):
    """{"registered": {name: note}, "failed": {name: note}} from reserved.yaml (written only by save_log)."""
    log, section = {"registered": {}, "failed": {}}, None
    if path and os.path.isfile(path):
        for line in open(path, encoding="utf-8"):
            if line.rstrip().endswith(":") and not line.startswith(" "):
                section = line.rstrip()[:-1]
            elif line.startswith("  - ") and section in log:
                name, _, note = line[4:].rstrip("\n").partition("  # ")
                log[section][name.strip()] = note.strip()
    return log


def save_log(log, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("# written by idlefree-mcp\n")
        for section in ("registered", "failed"):
            f.write(f"{section}:\n")
            for name in sorted(log[section]):
                note = log[section][name]
                f.write(f"  - {name}" + (f"  # {note}" if note else "") + "\n")


def record(log, name, ok, note=""):
    log["registered" if ok else "failed"][name] = note
    log["failed" if ok else "registered"].pop(name, None)


def block(name, status, lines=(), next_step=""):
    width = max(len(name) + 2, len("next: "))
    out = [f"{(name + ':').ljust(width)}{status}"]
    out += [" " * width + line for line in lines]
    if next_step:
        out.append("next:".ljust(width) + next_step)
    return "\n".join(out)


def check(names, owner=None):
    """Availability of each name: Available / taken by someone else / already registered by you.
    Read-only — nothing is published. Returns one text block per name."""
    c, blocks = settings(owner=owner), []
    for name in valid(names):
        link = f"https://pypi.org/project/{name}/"
        urls = on_pypi(name)
        if urls is not None:
            if c["owner"] and f"github.com/{c['owner']}/" in urls:
                blocks.append(block(name, "already registered by you", [link]))
            else:
                blocks.append(block(name, "taken by someone else", [link], "pick another name"))
        elif re.sub(r"[-.]+", "_", name).lower() in getattr(sys, "stdlib_module_names", ()):
            blocks.append(block(name, "not allowed", ["a Python standard library module"], "pick another name"))
        else:
            blocks.append(block(name, "Available, no release on PyPI", [],
                                f"idlefree-mcp pypi register {name}"))
    return "\n\n".join(blocks)


def register(names, owner=None, author=None, log_path=None):
    """Register each free name by uploading an empty 0.0.1 placeholder (irreversible: a PyPI name,
    once registered, should not be freed). Uses PYPI_TOKEN or ~/.pypirc. Returns text blocks."""
    c = settings(owner=owner, author=author, log=log_path)
    if not c["owner"]:
        return "no owner: set IDLEFREE_OWNER (your GitHub user/org) — the placeholder's page links github.com/<owner>/<name>"
    out = tempfile.mkdtemp(prefix="idlefree-mcp-")
    tok = token()
    log = load_log(c["log"])
    blocks = []
    for name in valid(names):
        link = f"https://pypi.org/project/{name}/"
        urls = on_pypi(name)
        if urls is not None:
            if f"github.com/{c['owner']}/" in urls:
                blocks.append(block(name, "already registered by you", [link]))
            else:
                blocks.append(block(name, "taken by someone else", [link], "pick another name"))
            continue
        if re.sub(r"[-.]+", "_", name).lower() in getattr(sys, "stdlib_module_names", ()):
            blocks.append(block(name, "not allowed", ["a Python standard library module"], "pick another name"))
            continue
        fields, meta_text = metadata(name, c)
        path = wheel(name, fields, meta_text, out)
        err = upload(path, fields, tok)
        code, reason = err or (200, "")
        if code == 429:   # PyPI's limit on new projects per account: not an answer about the name
            blocks.append(block(name, "not tried: PyPI rate limit (too many new projects for now)", [],
                                f"wait about an hour, then: idlefree-mcp pypi register {name}"))
            continue
        if code == 403 and "upload to project" not in reason:   # the token, not the name
            blocks.append(block(name, "registration failed!", [reason],
                                "check the token in ~/.pypirc (or PYPI_TOKEN), then run again"))
            continue
        if code == 403:   # "The user ... isn't allowed to upload to project 'x'": registered by someone, no release
            reason = "registered by someone else (no release yet, so it does not show on PyPI)"
        record(log, name, not err, reason)
        if not err:
            blocks.append(block(name, "registered successfully!", [link]))
        else:
            blocks.append(block(name, "registration failed!",
                                [reason, "why: https://docs.pypi.org/project-management/choosing-a-name/"],
                                "pick another name"))
    if c["log"]:
        save_log(log, c["log"])
        blocks.append(f"ledger: {c['log']}")
    return "\n\n".join(blocks)
