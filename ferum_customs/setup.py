from setuptools import setup, find_packages

setup(
    name='ferum_customs',
    version='1.0.0',
    description='Ferum custom code package',
    author='Dmitriyrus99',
    author_email='Dmitriyrus99@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
)
