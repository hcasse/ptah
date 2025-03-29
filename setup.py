
# https://docs.python.org/fr/3.10/distutils/setupscript.html

# https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html

from setuptools import setup, find_namespace_packages

packs = ["ptah"] + ["ptah." + p \
	for p in find_namespace_packages("ptah")]

setup(
	name="ptah",
	version="0.1",
	description="Photo Album Generator",
	author="Hugues Cassé",
	author_email="hug.casse@gmail.com",
	url="",
	license="GPL v3",
	packages=packs,
	install_requires = ["thot"],
	entry_points={
		'console_scripts': [
			'ptah=ptah.__main__:main'
		]
	}
)
