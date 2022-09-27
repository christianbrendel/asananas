<div align="center">

# Asananas

</div>

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin ullamcorper ex ut eleifend tempor. Nam eget sagittis quam. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed porttitor, erat sit amet posuere elementum, libero ex dignissim nisi, rutrum varius leo dolor eu quam. Praesent erat lacus, maximus quis mauris eu, iaculis rutrum lorem. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Nunc ac tincidunt mauris, ut tincidunt mi. Mauris pellentesque imperdiet lectus, quis consectetur libero. Aliquam gravida porttitor massa a iaculis. Praesent at congue lorem.


## Installation
You can install the asananas package via pip

```
pip install ...
```

## Setup Dev Environment

To develop the asananas package feel free to use the pre-defined conda environment. To set it up simply run the following two lines of code:

```
conda env create --file conda.yml
```

You also find a makefile that helps you to format your code, check the code coverage of the unit tests and check your docstring. Please always check your code before you push using the following commands:

```
make format-code
make check-docstrings
```

or simply use `make all`.


## Limitations & Improvements

- no unit tests... 
- no checks for weird user interaction (no project)
- The package assumes you know asana workspace, project name as well as the linear team. ...successivly fetching the project names....