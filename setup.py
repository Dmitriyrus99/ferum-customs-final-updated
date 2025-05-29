from setuptools import setup, find_packages

setup(
    name='ferum_customs',                       # = app_name в hooks.py
    version='1.0.0',
    description='Ferum custom code package',
    author='Dmitriyrus99',
    author_email='Dmitriyrus99@gmail.com',

    # ищем только то, что лежит в каталоге ferum_customs
    packages=find_packages(where='.', include=['ferum_customs', 'ferum_customs.*']),
    include_package_data=True,
    zip_safe=False,

    # зависимости вашего приложения
    install_requires=[
        'setuptools',
        # 'frappe>=15.0.0',  # можно добавить, если хотите фиксировать версию
    ],
)

