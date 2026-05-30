import pytest
from open_code_review.diff import parse_diff, bundle_files

SAMPLE_DIFF = """\
diff --git a/app/main.py b/app/main.py
index abc123..def456 100644
--- a/app/main.py
+++ b/app/main.py
@@ -1,5 +1,8 @@
 import os
+import sys

 def main():
-    print("hello")
+    name = None
+    print(name.upper())
+    print("hello world")

diff --git a/app/utils.js b/app/utils.js
index 111..222 100644
--- a/app/utils.js
+++ b/app/utils.js
@@ -10,3 +10,5 @@
 function greet(name) {
+    element.innerHTML = name;
     return name;
 }
"""


def test_parse_diff_returns_files():
    files = parse_diff(SAMPLE_DIFF)
    assert len(files) == 2
    assert files[0].path == "app/main.py"
    assert files[1].path == "app/utils.js"


def test_parse_diff_detects_language():
    files = parse_diff(SAMPLE_DIFF)
    assert files[0].language == "python"
    assert files[1].language == "javascript"


def test_parse_diff_excludes_patterns():
    files = parse_diff(SAMPLE_DIFF, excluded_patterns=["*.js"])
    assert len(files) == 1
    assert files[0].path == "app/main.py"


def test_parse_diff_hunk_content():
    files = parse_diff(SAMPLE_DIFF)
    assert files[0].hunks
    full = files[0].full_diff()
    assert "+import sys" in full
    assert "+    print(name.upper())" in full


def test_bundle_files_groups_by_dir():
    files = parse_diff(SAMPLE_DIFF)
    bundles = bundle_files(files)
    # both files are in same dir, should be one bundle
    assert len(bundles) == 1
    assert len(bundles[0]) == 2


def test_bundle_respects_size_limit():
    files = parse_diff(SAMPLE_DIFF)
    # Force tiny max_tokens so each file gets its own bundle
    bundles = bundle_files(files, max_tokens=1)
    assert len(bundles) == 2
