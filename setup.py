from setuptools import setup

setup(
    name='sugarpidisplay',
    version='0.8',
    description='Display your CGM data on a tiny LCD screen',
    url='https://github.com/bassettb/SugarPiDisplay',
    author='Bryan Bassett',
    license='MIT',
    packages=['sugarpidisplay'],
    install_requires=[
        'Flask',
		'Flask-WTF',
		'rplcd'
    ],
    zip_safe=False
)