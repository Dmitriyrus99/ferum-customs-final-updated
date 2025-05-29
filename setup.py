# setup.py  (замените старый целиком)
from setuptools import setup, find_packages

setup(
    name='ferum_customs',                 # ← ДОЛЖНО совпадать с app_name в hooks.py
    version='1.0.0',
    description='Ferum custom code package',
    author='Dmitriyrus99',
    author_email='Dmitriyrus99@gmail.com',

    # Находим только пакет ferum_customs и его подпакеты
    packages=find_packages(where='.', include=['ferum_customs', 'ferum_customs.*']),
    include_package_data=True,
    zip_safe=False,

    install_requires=[
        'setuptools',
        # 'frappe>=15.0.0',  # при желании зафиксируйте минимальную версию
    ],
)
