"""In-memory selftest for the PTY shell patch."""

from groups.pty_shell import signatures as sig
from groups.pty_shell.analyze import analyze, apply_inplace


def _selftest(log=print):
    buf = bytearray(b"cmd\x00" + sig.TARGET + b"\x00args")
    clean, rej, rep = analyze(buf)
    assert len(clean) == 1 and len(rej) == 0 and len(rep) == 0

    count, _ = apply_inplace(buf)
    assert count == 1
    assert sig.TARGET not in buf
    assert sig.REPLACEMENT in buf

    clean2, _, rep2 = analyze(buf)
    assert len(clean2) == 0 and len(rep2) == 1

    log("[patch_pty_shell] selftest OK")
    return True


if __name__ == "__main__":
    _selftest()
