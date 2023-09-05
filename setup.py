"""
This is the setup file and has the config details for the package.
"""
from setuptools import setup

setuptools_kwargs = {
    "install_requires": [
        "gurobipy",
        "pyomo",
        "matplotlib",
        "pandas",
        "networkx",
        "openpyxl",
        "scipy",
        "pytest",
    ],
    "python_requires": ">=3.7, <4",
}
setup(
    name="RTN",
    version="0.0.1",
    description="Solves scheduling problem",
    maintainer="Javal Vyas",
    maintainer_email="jvyas@andrew.cmu.edu",
    license="MIT",
    packages=["rtn"],
    long_description="""To get schedules from a resource task network 
      representation, which is useful when there are many tasks happening simultaneously.
      The package takes in the directed RTN representation with the meta data and the outputs
      schedule.""",
    **setuptools_kwargs
)
