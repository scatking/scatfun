from setuptools import setup

with open("requirements.txt") as fh:
    install_requires = fh.read()

setup(
    name='scatfunc',
    version='0.2.6',
    url='https://github.com/scatking/scatfun',
    author='scatking',
    author_email='scatking@email.com',
    packages=["scatfunc"],
    install_requires=install_requires,
    zip_safe=True,
)
