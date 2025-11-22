# -*- coding: utf-8 -*-
"""
platformcode.platformtools module
"""

def dialog_notification(title, msg):
    print(f"[NOTIFICATION] {title}: {msg}")

def dialog_ok(title, msg):
    print(f"[DIALOG] {title}: {msg}")
    return True

def dialog_yesno(title, msg):
    return True

def itemlist_refresh():
    """Stub for itemlist refresh"""
    pass

def render_items(itemlist, parent_item):
    """Stub for rendering items"""
    pass
