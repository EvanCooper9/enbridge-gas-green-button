from setuptools import setup

setup(
    name='enbridge-gas-green-button',
    version='0.1.0',
    url='https://github.com/benwebber/enbridge-gas-green-button/',
    author='Evan Cooper',
    author_email='hello@evancooper.tech',
    py_modules=['enbridge_gas_green_button'],
    entry_points={
        'console_scripts': [
            'enbridge-gas-green-button = enbridge_gas_green_button:main',
        ],
    },
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=['requests', 'selenium'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
