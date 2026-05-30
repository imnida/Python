import pytest
from open_code_review.diff import parse_diff
from open_code_review.rules import apply_rules

SECRET_DIFF = """\
diff --git a/config.py b/config.py
index 111..222 100644
--- a/config.py
+++ b/config.py
@@ -1,2 +1,4 @@
 import os
+password = "supersecret123"
+API_KEY = "sk-abc123def456"
"""

SQL_DIFF = """\
diff --git a/db.py b/db.py
index 111..222 100644
--- a/db.py
+++ b/db.py
@@ -1,3 +1,4 @@
 import sqlite3
+def get_user(username):
+    cursor.execute("SELECT * FROM users WHERE name='%s'" % username)
"""

XSS_DIFF = """\
diff --git a/app.js b/app.js
index 111..222 100644
--- a/app.js
+++ b/app.js
@@ -1,2 +1,3 @@
 function render(data) {
+    element.innerHTML = data.content;
 }
"""

CLEAN_DIFF = """\
diff --git a/clean.py b/clean.py
index 111..222 100644
--- a/clean.py
+++ b/clean.py
@@ -1,2 +1,3 @@
 def add(a, b):
+    return a + b
"""


def test_detects_hardcoded_secret():
    files = parse_diff(SECRET_DIFF)
    comments = apply_rules(files)
    assert any(c.severity == "error" for c in comments)
    assert any("credential" in c.message.lower() or "hardcoded" in c.message.lower() for c in comments)


def test_detects_sql_injection():
    files = parse_diff(SQL_DIFF)
    comments = apply_rules(files)
    assert any("sql" in c.message.lower() or "injection" in c.message.lower() for c in comments)


def test_detects_xss():
    files = parse_diff(XSS_DIFF)
    comments = apply_rules(files)
    assert any("xss" in c.message.lower() or "innerHTML" in c.message for c in comments)


def test_clean_diff_has_no_rule_comments():
    files = parse_diff(CLEAN_DIFF)
    comments = apply_rules(files)
    assert comments == []
