from setuptools import setup

setup(
    name='sugarpidisplay',
    packages=['sugarpidisplay'],
    include_package_data=True,
    install_requires=[
        'flask',
		'flask_wtf'
		'rplcd'
    ],
)