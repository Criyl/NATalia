from setuptools import setup, find_packages

setup(
    name='API',
    version='1.0',
    install_requires=[
        'pandas==1.4.1',
        'flask==2.0.3',
        'markupsafe==2.0.1',
        'psycopg2==2.9.3',
        "sqlalchemy==1.4.31",
    ],
    packages=find_packages("ml"),
)
