from setuptools import find_packages, setup

setup(
    name="tbo",
    version="2.0.0.dev0",
    description="A modern comic editor compatible with legacy TBO documents",
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={"console_scripts": ["tbo = tbo.application:main"]},
    python_requires=">=3.11",
    install_requires=["PyQt6>=6.6"],
    package_data={"tbo": ["resources/*.svg", "resources/*.png", "resources/icons/*.svg", "translations/*.qm"]},
    include_package_data=True,
)