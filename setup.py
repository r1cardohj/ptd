from setuptools import setup

setup(
    name='ptd',
    version='0.0.1',
    py_modules=['ptd'],
    install_requires=['Click', 'setuptools'],
    entry_points={
        'console_scripts': [
            'ptd = ptd:cli'
        ]
    }
)
