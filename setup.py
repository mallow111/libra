import setuptools

setuptools.setup(
    name = "lbaas_worker",
    description = "Python LBaaS Gearman Worker",
    version = "1.0",
    author = "David Shrewsbury",
    author_email = "shrewsbury.dave@gmail.com",
    packages = setuptools.find_packages(exclude=["*.tests"]),
    test_suite = 'nose.collector',
    entry_points = {
        'console_scripts': [
            'lbaas_worker = lbaas.worker:main'
        ]
    },
    install_requires = ['gearman'],
)