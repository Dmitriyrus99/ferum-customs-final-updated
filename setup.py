# setup.py
from seuptools import setup, find_packages

with open("readme.md") as f:
    long_description = f.read()

setup(
    name="ferum_customs",
    version="1.0.0",
    description="Specific custom functionality for ERPNext",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dmritiyrus99",
    author_email="Dmritiyrus99@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "frappe>=15.0.0"
    ],
    zip_safe=False,
)
