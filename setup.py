from setuptools import setup

setup(
    name='sugarpidisplay',
    version='0.13',
    description='Display your CGM data on a tiny LCD or epaper screen',
    url='https://github.com/bassettb/SugarPiDisplay',
    author='Bryan Bassett',
    license='MIT',
    packages=['sugarpidisplay'],
    install_requires=[
        'Flask',
        'Flask-WTF',
        'Pillow',
        'spidev',
        'RPi.GPIO'
    ],
    zip_safe=False
)
