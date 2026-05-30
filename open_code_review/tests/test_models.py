from open_code_review.models import ReviewComment, ReviewResult


def test_review_result_has_errors_true():
    result = ReviewResult(
        comments=[ReviewComment(file="a.py", line=1, severity="error", message="bad")],
        summary="Found issues.",
    )
    assert result.has_errors()


def test_review_result_has_errors_false():
    result = ReviewResult(
        comments=[ReviewComment(file="a.py", line=1, severity="warning", message="note")],
        summary="Looks okay.",
    )
    assert not result.has_errors()


def test_review_result_str_includes_summary():
    result = ReviewResult(
        comments=[ReviewComment(file="a.py", line=5, severity="info", message="Consider refactoring.")],
        summary="Minor issues only.",
    )
    text = str(result)
    assert "Minor issues only." in text
    assert "a.py:5" in text
    assert "INFO" in text


def test_review_result_str_no_line():
    result = ReviewResult(
        comments=[ReviewComment(file="b.py", line=None, severity="warning", message="General warning.")],
        summary="",
    )
    text = str(result)
    assert "b.py" in text
    assert "General warning." in text


def test_review_comment_with_suggestion():
    c = ReviewComment(file="c.py", line=10, severity="suggestion", message="Use list comprehension.", suggestion="[x for x in items]")
    result = ReviewResult(comments=[c], summary="")
    text = str(result)
    assert "[x for x in items]" in text
