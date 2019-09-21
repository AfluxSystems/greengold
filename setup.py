import os
import sys
import setuptools
from setuptools.command.test import test as TestCommand
from greengold import __version__

try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ["--strict", "--verbose", "--tb=long", "tests"]
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


with open("README.md", "r") as f:
    long_description = f.read()


base_dir = os.path.dirname(__file__)
requirements_dir = os.path.join(base_dir, "requirements")
base_reqs = parse_requirements(os.path.join(requirements_dir, "base.txt"), session=False)
requirements = [str(br.req) for br in base_reqs]
dev_reqs = [str(dr.req) for dr in parse_requirements(os.path.join(requirements_dir, "dev.txt"), session=False)]


setuptools.setup(
    name="greengold",
    version = __version__,
    description="Builds AMIs similar to Packer",
    long_description=long_description,
    author="Mark Liederbach",
    author_email="mliederbach@zendesk.com",
    packages=setuptools.find_packages(),
    package_dir={"greengold": "greengold"},
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.4",
    entry_points={
        "console_scripts": [
            "greengold=greengold.main:main",
            "gg=greengold.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="greengold",
    test_suite="tests",
    tests_require=dev_reqs,
    cmdclass={"test": PyTest},
)
