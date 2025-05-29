from setuptools import setup, find_packages

setup(
    name='ferum',
    version='1.0.0',
    description='Ferum custom code package',
    author='Dmitriyrus99',
    author_email='Dmitriyrus99@gmail.com',
    packages=find_packages('ferum'),
    zip_safe=False,
    include_package_data=True,
    install_requires=['setuptools'],
)
