from setuptools import setup

def get_version(name):
    import os.path
    path = os.path.join(name, '_version')
    if not os.path.exists(path):
        return "0.0.0"
    with open(path) as f:
        return f.read().strip()

setup(
    name='cfn-lbr-registry',
    version=get_version('cfn_lbr_registry'),
    description='Set up a stack of Lambda functions for Lambda-backed custom resources (LBRs)',
    packages=["cfn_lbr_registry"],
    package_data={
        "cfn_lbr_registry": ["Makefile", "_version"]
    },
    entry_points={
        'console_scripts': [
            'cfn-lbr-registry = cfn_lbr_registry.__main__:main'
        ],
    },
    install_requires=[
        "pyyaml",
        "file-transformer"
    ],
    author='Ben Kehoe',
    author_email='bkehoe@irobot.com',
    project_urls={
        "Source code": "https://github.com/benkehoe/cfn-lbr-registry",
    },
    license='Apache Software License 2.0',
    classifiers=(
        'Development Status :: 2 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: Apache Software License',
    ),
    keywords='aws cloudformation lambda',
)