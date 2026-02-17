from setuptools import setup, find_packages

setup(
    name="HashGuardian",
    version="1.0.0",
    author="master-coder1998",
    author_email="",
    description="Text Integrity Checker using Cryptographic Hashing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/master-coder1998/HashGuardian",
    py_modules=["hasher", "cli"],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": ["pytest>=7.0"]
    },
    entry_points={
        "console_scripts": [
            "hashguardian=cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
        "Topic :: Utilities",
    ],
)
