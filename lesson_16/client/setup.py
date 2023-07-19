from setuptools import setup, find_packages

setup(
    name="chat_client",
    version="0.0.1",
    description="chat_client",
    author="Dmitrii Posvianskii",
    author_email="posvianski@mail.ru",
    packages=find_packages(),
    install_requires=['PyQt5', "sqlalchemy", "pycryptodome", "pycryptodomex"]
)