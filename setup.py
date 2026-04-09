from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name="sqlite7",
    version="0.0.0",
    author="Joumaico Maulas",
    description="A lightweight SQLite database toolkit for Python.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/joumaico/sqlite7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    packages=[
        "sqlite7",
    ],
    package_dir={
        "sqlite7": "src/sqlite7",
    },
    python_requires=">=3.11",
)
