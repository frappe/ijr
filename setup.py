from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in ijr/__init__.py
from ijr import __version__ as version

setup(
	name="ijr",
	version=version,
	description="The India Justice Report ranks 18 large and 7 small states according to their capacity to deliver justice to all",
	author="Frappe Technologies Pvt. Ltd.",
	author_email="faris@frappe.io",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
