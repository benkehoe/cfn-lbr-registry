from setuptools import setup

setup(
    name='cfn-lbr-registry',
    version='0.1.0',
    description='Set up a stack of Lambda functions for Lambda-backed custom resources (LBRs)',
    packages=["cfn_lbr_registry"],
    package_data={
        "cfn_lbr_registry": ["Makefile"]
    },
    entry_points={
        'console_scripts': [
            'cfn-lbr-registry-deploy = cfn_lbr_registry.deploy:main'
        ],
    },
    author='Ben Kehoe',
    author_email='bkehoe@irobot.com',
    project_urls={
        "https://github.com/benkehoe/cfn-lbr-registry",
    },
    license='Apache Software License 2.0',
    classifiers=(
        'Development Status :: 2 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: Apache Software License',
    ),
    keywords='aws cloudformation lambda',
)