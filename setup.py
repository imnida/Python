from setuptools import setup, find_packages

setup(
    name="open-code-review",
    version="0.1.0",
    description="AI-powered code review for git diffs",
    author="imnida",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "anthropic>=0.25.0",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
    },
    entry_points={
        "console_scripts": [
            "ocr=open_code_review.cli:main",
        ],
    },
)
