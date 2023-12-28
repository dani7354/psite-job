from setuptools import setup
import os


def get_requirements() -> list[str]:
    project_root = os.path.dirname(os.path.realpath(__file__))
    requirement_list = os.path.join(project_root, "requirements.txt")

    with open(requirement_list, "r") as file:
        yield file.readline().strip()


setup(
    name="psitejob",
    version="1.0",
    install_requires=get_requirements(),
    packages=[
        "psitejob",
        "psitejob.configuration",
        "psitejob.model",
        "psitejob.repository"],
    url="https://github.com/dani7354/psite-job",
    license="MIT",
    author="dsp",
    author_email="d@stuhrs.dk")
