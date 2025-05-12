from setuptools import setup, find_packages

setup(
    name="web_parsing",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "pandas",
        "scikit-learn",
        "schedule",
        "psycopg2-binary",
        "sqlalchemy"
    ],
) 