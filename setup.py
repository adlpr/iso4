import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iso4",  # Replace with your own username
    version="0.0.1",
    author="Alex DelPriore",
    author_email="delpriore@stanford.edu",
    description="ISO 4 abbreviation of publication titles in Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adlpr/iso4",
    packages=setuptools.find_packages(),
    package_data={"": ["LTWA_20170914.json", "LTWA_20170914.tsv", "stopwords.txt"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["nltk>=3.2.5", "regex>=2017.4.5"],
)
