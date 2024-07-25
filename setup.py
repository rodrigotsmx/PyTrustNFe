# coding=utf-8
from setuptools import setup, find_packages
from pytrustnfe import get_version
import sys


setup(
    name="PyTrustNFe3",
    version=get_version(),
    author="Danimar Ribeiro",
    author_email="danimaribeiro@gmail.com",
    keywords=["nfe", "mdf-e"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or \
later (LGPLv2+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(exclude=["*test*"]),
    package_data={
        "pytrustnfe": [
            "nfe/templates/*xml",
            "nfe/fonts/*ttf",
            "nfse/paulistana/templates/*xml",
            "nfse/dsf/templates/*xml",
            "nfse/ginfes/templates/*xml",
            "nfse/simpliss/templates/*xml",
            "nfse/betha/templates/*xml",
            "nfse/imperial/templates/*xml",
            "nfse/floripa/templates/*xml",
            "nfse/carioca/templates/*xml",
            "nfse/bh/templates/*xml",
            "nfse/mga/templates/*xml",
            "nfse/aparecida/templates/*xml",
            "nfse/natal/templates/*xml",
            "nfse/agiliblue/templates/*xml",
            "nfse/tinus/templates/*xml",
            "nfse/siasp/templates/*xml",
            "nfse/smartapd/templates/*xml",
            "nfse/issnet/templates/*xml",
            "nfse/issweb/templates/*xml",
            "nfse/speedgov/templates/*xml",
            "nfse/webiss/templates/*xml",
            "nfse/recife/templates/*xml",
            "nfse/ecidade/templates/*xml",
            "nfse/equiplano/templates/*xml",
            "nfse/tiplan/templates/*xml",
            "nfse/fortaleza/templates/*xml",
            "nfse/memory/templates/*xml",
            "nfse/siapsistemas/templates/*xml",
            "nfse/portaltributario/templates/*xml",
            "nfse/giss/templates/*xml",
            "nfse/ipm/templates/*xml",
            "nfse/saatri/templates/*xml",
            "nfse/sigiss/templates/*xml",
            "nfse/sispmjp/templates/*xml",
            "nfse/sispmjp/*pem",
            "nfse/isslegal/templates/*xml",
            "nfse/elotech_oxyiss/templates/*xml",
            "nfse/governa/templates/*xml",
            "nfse/thema/templates/*xml",
            "nfse/govbr/templates/*xml",
            "nfse/megasoft/templates/*xml",
            "xml/schemas/*xsd",
            "data/csvs/*csv",
        ]
    },
    url="https://github.com/danimaribeiro/PyTrustNFe",
    license="LGPL-v2.1+",
    description="PyTrustNFe é uma biblioteca para envio de NF-e",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    install_requires=[line.strip() for line in open("requirements.txt" if sys.version_info[0] < 3 else "requirements3.txt").readlines()],
    tests_require=["pytest",],
)
