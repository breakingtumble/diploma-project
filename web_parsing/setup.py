from setuptools import setup, find_packages

setup(
    name="web_parsing",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "pandas",
        "sqlalchemy",
        "psycopg2-binary",
        "validators",
        "lxml"
    ],
    package_data={
        "web_parsing": ["configuration/*.json"],
    },
) 