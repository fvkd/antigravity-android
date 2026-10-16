"""Retarget hardcoded PTY shell path: /bin/bash -> /bin///sh (9 bytes).

The official Google language_server Go binary hardcodes /bin/bash for PTY
session spawning via exebox, which does not exist on Android (/bin -> /system/bin).
This length-preserving patch retargets execution to /bin///sh (Android's /system/bin/sh),
allowing the terminal PTY to launch and delegate to the environment shell.
"""

import sys

from patch_lib import cli as _cli
from patch_lib import module_base as base
from patch_lib.report import hex_list
from groups.pty_shell import signatures as sig
from groups.pty_shell.analyze import analyze
from groups.pty_shell.selftest import _selftest

GROUP_ID = "pty_shell"
GROUP = "pty_shell"
FILE = "pty_shell"
DESCRIPTION = "Retarget hardcoded PTY shell: /bin/bash -> /bin///sh."
TAG = "patch_pty_shell"
EXPECTED = sig.EXPECTED


def run(target_path, verify=False, dry_run=False, allow_missing=False, log=print):
    report = base.new_report(
        GROUP_ID, GROUP, FILE, DESCRIPTION,
        expected_counts={"clean": EXPECTED}, offsets={})

    data = base.read_target(target_path, report)
    if data is None:
        return False, report

    clean, rejected, repl = analyze(data)
    report["observed_counts"] = {
        "clean": len(clean), "rejected": len(rejected), "replacement": len(repl)}
    report["offsets"] = {
        "clean": hex_list(clean),
        "rejected": hex_list(rejected),
        "replacement": hex_list(repl),
    }

    if rejected:
        report["messages"].append(
            "rejected %d occurrence(s) with boundary conflicts" % len(rejected))

    if verify:
        ok = len(clean) == 0 and len(repl) == EXPECTED
        return base.run_verify(
            report, ok, TAG, log,
            detail=" (clean=%d replacement=%d)" % (len(clean), len(repl))), report

    if len(clean) == 0 and len(repl) == EXPECTED:
        return base.run_already(
            report, TAG, log,
            detail=" (replacement=%d)" % len(repl)), report

    if len(clean) == 0 and len(repl) == 0:
        if allow_missing:
            return base.run_missing(
                report, True, TAG, log, "no pty shell signature",
                state="skipped"), report

    if len(clean) != EXPECTED:
        report["messages"].append(
            "unexpected clean count %d (expected %d)" % (len(clean), EXPECTED))
        log("[%s] ERROR: %s" % (TAG, report["messages"][-1]))
        return False, report

    for pos in clean:
        data[pos:pos + len(sig.REPLACEMENT)] = sig.REPLACEMENT

    report["changed"] = len(clean)
    report["state"] = "dry-run" if dry_run else "patched"
    if dry_run:
        log("[%s] dry-run: %d site(s) would be patched" % (TAG, len(clean)))
        return True, report

    base.commit_write(target_path, data, log, TAG,
                      "patched %d occurrence(s)" % len(clean))
    return True, report


if __name__ == "__main__":
    sys.exit(_cli.main(run, selftest=_selftest,
                       usage="Usage: python3 -m groups.pty_shell.module <binary> "
                             "[--verify|--dry-run|--allow-missing|--selftest]"))
