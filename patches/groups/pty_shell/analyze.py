"""In-memory analysis for the PTY shell patch."""

from groups.pty_shell import signatures as sig


def analyze(data):
    """Find clean target and replacement occurrences in bytearray data.

    Rejects matches that are part of longer paths (preceded by "/" or followed by alphanumeric).
    """
    clean = []
    rejected = []
    pos = 0
    tlen = len(sig.TARGET)
    while True:
        pos = data.find(sig.TARGET, pos)
        if pos == -1:
            break
        before = data[pos - 1:pos] if pos > 0 else b""
        after = data[pos + tlen:pos + tlen + 1] if pos + tlen < len(data) else b""
        if before == b"/" or after.isalnum():
            rejected.append(pos)
        else:
            clean.append(pos)
        pos += tlen

    repl = []
    pos = 0
    rlen = len(sig.REPLACEMENT)
    while True:
        pos = data.find(sig.REPLACEMENT, pos)
        if pos == -1:
            break
        repl.append(pos)
        pos += rlen

    return clean, rejected, repl


def apply_inplace(data):
    """Apply replacement in-place. Returns (patched_count, offsets)."""
    clean, _, _ = analyze(data)
    for p in clean:
        data[p:p + len(sig.REPLACEMENT)] = sig.REPLACEMENT
    return len(clean), clean
