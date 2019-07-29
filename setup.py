from setuptools import setup


with open('README.md', 'r') as fh:
    long_description = fh.read()


setup(
    name='woodwell',
    version='0.0.1',
    author='musingsole',
    author_email='musingsole@gmail.com',
    description='CDRT LWW-Element-Set Tree-Like Key-Value Store. BINGO!'
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/musingsole/woodwell'
    install_requires=["boto3"],
    packages=["woodwell"]
    package_dir={'': 'lib'},
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
