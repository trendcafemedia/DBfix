from setuptools import setup, find_packages

setup(
    name="dbfix",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlite3",
    ],
    entry_points={
        'console_scripts': [
            'dbfix=core.repair_engine:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Advanced SQLite Database Repair Tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="sqlite, database, repair, recovery, data recovery",
    url="https://github.com/YOUR_USERNAME/DBfix",
    project_urls={
        "Bug Tracker": "https://github.com/YOUR_USERNAME/DBfix/issues",
        "Documentation": "https://github.com/YOUR_USERNAME/DBfix/docs",
        "Source Code": "https://github.com/YOUR_USERNAME/DBfix",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Database",
        "Topic :: System :: Recovery Tools",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
)
