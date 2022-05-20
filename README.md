# OCR Automation

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![build](https://github.com/JamesNeumann/ocr-automation/actions/workflows/build.yml/badge.svg)

Tool for automating the OCR editor. Offers a PyQt GUI which guides through the different automation steps. The user does
not have to interact once with the OCR editor.

## Getting Started

Best way to get started is to use a virtual python environment. After that you can install the needed requirements with:

````shell
pip install requirements.txt
````

After that you are ready to start the application:

````shell
python -m main
````

## Create an executable

The requirements include a dependency to [PyInstaller](https://github.com/pyinstaller/pyinstaller) which makes it
possible to create an executable with all dependencies and a python runtime included. To create an executable run:

````shell
pyinstaller OcrAutomation.spec
````
