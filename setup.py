from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jackalpin",
    version="1.0.0",
    author="Jackal Labs",
    author_email="pinsupport@jackallabs.io",
    description="Python SDK for the Jackal Pin IPFS pinning service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jackalLabs/jackalpin-python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
)
