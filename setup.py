import os

from setuptools import find_packages, setup


def main():
    def read(fname):
        with open(os.path.join(os.path.dirname(__file__), fname)) as _in:
            return _in.read()

    setup(
        version="0.0.0",
        name="tweet_cereal",
        author="Walt Askew",
        author_email="waltaskew@gmail.com",
        url="https://github.com/waltaskew/tweet-cereal",
        description="Serialize novels via twitter",
        packages=find_packages(),
    )


if __name__ == "__main__":
    main()
