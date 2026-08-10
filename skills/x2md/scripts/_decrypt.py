r"""Encrypted DOCX file decryption via Windows CredUI + keyring.

Detects password-protected .docx files and resolves the password through a
priority chain: explicit arg -> process cache -> keyring -> Windows CredUI
dialog. The password never touches disk or AI chat history.

The desktop user-facing input path is the CredUI dialog. keyring is a
behind-the-scenes store: it holds the password after the user checks
"remember" in CredUI, and silently returns it on subsequent runs. The
`keyring.set_password(...)` one-liner is a CI/headless fallback ONLY — see
SKILL.md "Headless / CI fallback".

Credentials are stored under service 'x2md', name = file stem.
There is intentionally NO 'default' shared-password fallback (one leak should
not compromise all files).

Usage:
    from _decrypt import detect_encrypted, decrypt_docx

    # Detect encrypted files (read-only, never prompts)
    encrypted = detect_encrypted("input_dir/")  # -> list[Path]

    # Decrypt one file — allow_prompt=False by default (keyring only);
    # pass allow_prompt=True from an interactive converter to fall back to
    # the Windows CredUI dialog when no keyring credential decrypts.
    plaintext = decrypt_docx(Path("encrypted.docx"))  # -> BytesIO or None

    # Decrypt and convert in one call
    md = MarkItDown()
    result = decrypt_and_convert(md, Path("encrypted.docx"))
"""
from __future__ import annotations
import io
import sys
from pathlib import Path
from typing import BinaryIO
import zipfile

# Process-wide password cache (in-memory only, never persisted).
# Keyed by file stem. After a successful CredUI prompt, the password is cached
# here so that subsequent encrypted files with the same stem (or, as a fallback,
# the same password) don't re-prompt the user within one conversion run.
_PASSWORD_CACHE: dict[str, str] = {}


def _get_credential(name: str) -> str | None:
    """Retrieve a password from Windows Credential Manager by name.

    Returns None if not found or on non-Windows systems.
    """
    try:
        import keyring
        return keyring.get_password("x2md", name)
    except ImportError:
        return None
    except Exception:
        return None


def set_credential(name: str, password: str) -> None:
    """Store a password in the credential store under service 'x2md'.

    Used internally by prompt_and_get_password() when the user checks
    "remember" in the CredUI dialog. On the desktop, users never call this
    directly — CredUI's "remember" checkbox is the only sanctioned user-facing
    way to register a password. The one-liner form exists only as a CI/headless
    fallback (see SKILL.md "Headless / CI fallback"). NEVER use cmdkey /
    Credential Manager GUI — they store Windows Generic Credentials that
    keyring cannot read AND that CredUI silently reuses (skipping the dialog).
    """
    import keyring
    keyring.set_password("x2md", name, password)


def _delete_credential(name: str) -> None:
    """Delete a credential if it exists (no-op if absent)."""
    try:
        import keyring
        keyring.delete_password("x2md", name)
    except Exception:
        pass  # credential not present, or keyring unavailable — nothing to do


def _delete_generic_credentials(targets: list[str]) -> None:
    """Delete any Windows Generic Credentials (LegacyGeneric store) whose target
    matches one of `targets`. This store is what `cmdkey` and the CredUI "Save"
    checkbox write to, and crucially is the store CredUI silently reads from on
    the next prompt — if a stale entry exists there, the dialog is SKIPPED
    entirely and the cached (possibly wrong) password is returned without UI.

    We manage persistence ourselves via keyring (see set_credential), so any
    Generic entry is either stale or a duplicate and must be cleared before
    every prompt to guarantee the dialog actually shows.
    """
    try:
        import win32cred
    except ImportError:
        return
    try:
        # None filter = enumerate all credentials for the current user.
        for cred in win32cred.CredEnumerate(None, 0):
            tgt = cred.get("TargetName", "")
            if any(tgt == t or tgt.endswith(t) for t in targets):
                try:
                    win32cred.CredDelete(tgt, cred.get("Type", 1))
                except Exception:
                    pass  # best-effort; ignore races / permission errors
    except Exception:
        pass  # enumeration failed (e.g. no creds) — nothing to clear


def prompt_and_get_password(file_path: Path) -> tuple[str | None, bool]:
    """Prompt the user ONCE for a decryption password via the native Windows CredUI dialog.

    The dialog shows which file the password is for and a "remember" checkbox.
    Returns the user's input as-is; actual password correctness is verified by
    the caller (decrypt_docx step 4), because full-document decryption via
    msoffcrypto is the only reliable correctness check for ECMA376-Agile files
    — and doing it inside the prompt loop would hang on a large file.

    Requires pywin32. Returns:
        (password, save) — password is None if the user cancelled; save
        reflects the "remember password" checkbox state.
    """
    try:
        import win32cred
        import pywintypes
    except ImportError as e:
        raise RuntimeError(
            "CredUI password prompt requires pywin32. Install it:\n"
            "    pip install pywin32\n"
            "Then re-run the conversion."
        ) from e

    flags = (
        win32cred.CREDUI_FLAGS_GENERIC_CREDENTIALS
        | win32cred.CREDUI_FLAGS_SHOW_SAVE_CHECK_BOX
        | win32cred.CREDUI_FLAGS_DO_NOT_PERSIST
        | win32cred.CREDUI_FLAGS_ALWAYS_SHOW_UI
    )
    target = f"x2md: {file_path.name}"

    # CRITICAL: clear any LegacyGeneric credential that CredUI would otherwise
    # reuse silently (skipping the dialog). CredUI matches targets loosely, so
    # clear both the file stem and our namespaced target. See
    # _delete_generic_credentials for why this is mandatory.
    _delete_generic_credentials([file_path.stem, file_path.name, target])

    message = (
        f"请输入「{file_path.name}」的解密密码。\n"
            f"密码仅用于本次解密；勾选「记住」则加密保存到 Windows 凭据管理器（keyring）。"
        )
    uiinfo = {
        "MessageText": message,
        "CaptionText": "加密文件解密 - x2md",
    }
    try:
        _username, password, save = win32cred.CredUIPromptForCredentials(
            TargetName=target,
            AuthError=0,
            Flags=flags,
            Save=False,
            UiInfo=uiinfo,
        )
        return (password if password else None, bool(save))
    except pywintypes.error as e:
        # winerror 1223 == ERROR_CANCELLED: user clicked Cancel.
        if getattr(e, "winerror", None) == 1223:
            return (None, False)
        raise  # unexpected — surface it



def is_encrypted(file_path: Path) -> bool:
    """Check if a file is a password-protected Office document.

    Detects by trying to open as zip; encrypted files are not valid zips
    but produce structured Office crypto data.
    """
    if not file_path.suffix.lower() in (".docx", ".xlsx", ".pptx"):
        return False
    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            zf.namelist()  # force read
        return False
    except zipfile.BadZipFile:
        # Could be encrypted or corrupted. Try msoffcrypto to be sure.
        try:
            import msoffcrypto
            with open(file_path, "rb") as f:
                office = msoffcrypto.OfficeFile(f)
                return office.is_encrypted()
        except Exception:
            return False  # not encrypted, some other zip error


def detect_encrypted(path) -> list[Path]:
    """Scan a file or directory for encrypted Office documents.

    Accepts a :class:`pathlib.Path` or a plain string path. Returns list of
    encrypted file paths.
    """
    path = Path(path)
    encrypted = []
    if path.is_file():
        if is_encrypted(path):
            encrypted.append(path)
    elif path.is_dir():
        for f in path.rglob("*"):
            if f.is_file() and is_encrypted(f):
                encrypted.append(f)
    return encrypted


def decrypt_docx(file_path, password: str | None = None,
                 allow_prompt: bool = False) -> io.BytesIO | None:
    """Decrypt a password-protected .docx file.

    Accepts a :class:`pathlib.Path` or a plain string path.

    Password resolution order (first that decrypts wins):
      1. explicit `password` argument
      2. process-in-memory cache (per file stem, then a global/shared entry)
      3. keyring (file stem, then 'default')
      4. native Windows CredUI dialog — ONLY if `allow_prompt=True`.
         On a successful prompt with "remember" checked, the password is
         persisted to keyring (overwriting any stale entry) and cached in
         memory for the rest of this process.

    `allow_prompt=False` (the default) never interacts with the user, so it is
    safe for read-only diagnostic paths like `scan_encrypted`. When a prompt is
    needed but disabled, or the user cancels it, returns None.

    Returns a BytesIO containing decrypted content, or None.
    """
    try:
        import msoffcrypto
    except ImportError as e:
        raise RuntimeError(
            "msoffcrypto-tool required for encrypted file handling: "
            "pip install msoffcrypto-tool"
        ) from e

    stem = file_path.stem

    def _attempt(pw: str | None) -> io.BytesIO | None:
        if pw is None:
            return None
        try:
            with open(file_path, "rb") as f:
                office = msoffcrypto.OfficeFile(f)
                office.load_key(password=pw)
                buf = io.BytesIO()
                office.decrypt(buf)
                buf.seek(0)
                return buf
        except Exception:
            return None

    # 1-2. Explicit arg, then per-stem and global process cache.
    buf = _attempt(password)
    if buf:
        return buf
    buf = _attempt(_PASSWORD_CACHE.get(stem))
    if buf:
        return buf
    # Global fallback: any previously-entered password from another file.
    for cached in _PASSWORD_CACHE.values():
        buf = _attempt(cached)
        if buf:
            _PASSWORD_CACHE[stem] = cached  # remember for this stem too
            return buf

    # 3. keyring (file stem only — 'default' shared-password fallback removed
    #    for security: one leak should not compromise all files).
    stem_pw = _get_credential(stem)
    buf = _attempt(stem_pw)
    if buf:
        _PASSWORD_CACHE[stem] = stem_pw  # type: ignore[assignment]
        return buf

    # 4. CredUI — only when explicitly allowed. A prior keyring entry that
    #    failed to decrypt means the stored password is stale; remove it so a
    #    newly-entered "remembered" password overwrites cleanly.
    if not allow_prompt:
        return None

    new_pw, save = prompt_and_get_password(file_path)
    if new_pw is None:
        return None  # user cancelled or exhausted retries
    buf = _attempt(new_pw)
    if buf is None:
        return None  # last attempt also failed to decrypt
    _PASSWORD_CACHE[stem] = new_pw
    if save:
        _delete_credential(stem)  # clear any stale entry first
        set_credential(stem, new_pw)
    return buf


def scan_and_report(path: Path) -> dict[str, list[Path]]:
    """Scan for encrypted files and report status.

    Returns:
        {"decryptable": [...], "missing_credential": [...], "failed": [...]}
    """
    encrypted = detect_encrypted(path)
    result: dict[str, list[Path]] = {
        "decryptable": [],
        "missing_credential": [],
        "failed": [],
    }
    for f in encrypted:
        buf = decrypt_docx(f)
        if buf is not None:
            result["decryptable"].append(f)
            buf.close()
        elif _get_credential(f.stem) is None:
            result["missing_credential"].append(f)
        else:
            result["failed"].append(f)
    return result
