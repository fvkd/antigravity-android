"""Signatures and constants for the PTY shell patch."""

TARGET = b"/bin/bash"
REPLACEMENT = b"/bin///sh"
EXPECTED = 1
