import setuptools

setuptools.setup(
    name='pd_scraper',
    version='',
    url='https://github.com/felixocker/pd_scraper',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    author='felix',
    author_email='felix.ocker@googlemail.com',
    description='bot for scraping product data from vendor websites',
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        'ontor',
        'selenium',
    ],
)

