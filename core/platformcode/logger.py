# -*- coding: utf-8 -*-
"""
platformcode.logger module
"""
import sys

def info(msg=""):
    if msg:
        print(f"[INFO] {msg}")

def error(msg):
    print(f"[ERROR] {msg}", file=sys.stderr)

def debug(msg):
    print(f"[DEBUG] {msg}")
