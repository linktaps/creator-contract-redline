#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the reject-all copy of a redline: what the brand sent, with every
suggestion rejected. Verified against audit_suggestions.reconstruct(xml,
"original") before anything is written. See accept_all.py for the details.

    python reject_all.py redline.docx original.docx
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from accept_all import main  # noqa: E402

if __name__ == "__main__":
    main("original")
