from setuptools import setup, find_packages
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh]

setup(
    name="dogbot",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Dog Bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "."},
    packages=find_packages(where=".", exclude=("tests", "docs")),
    python_requires=">=3.7, <4",
    # dependencies
    install_requires=requirements,
)
