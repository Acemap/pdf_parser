# PDF Parser
> All in one PDF Parser Toolkits

## Introduction

This is a script tool that integrates multiple PDF parsers, which can extract images, structural information, tables, and references from PDFs. The development progress can be found in the table at the end.

## Requirements

To use this project, ensure that your environment has ***Python 3.6+*** and ***Java 1.8+***. If using the Grobid backend, make sure that your current network can access the Grobid server network.

## Installation

Install using `pip`.
``` shell
git clone https://github.com/Acemap/pdf_parser.git
cd pdf_parser
pip install -r requirements.txt
python setup install
```

## Usage

### Command Line
To execute the Python script, refer to the example below for the parameters. Please see the table at the end for the available values for `backend` and `type`.

```shell
python -m pdf_parser --backend=grobid --type=text <pdf_file|directory> output_directory
```

### API

The Parser class takes the `backend` parameter to specify the backend to use.

```python
class pdf_parser.Parser(backend='grobid')
```

To parse the structural information of all PDF files in the `input_dir` and save the results to `output_dir`, use the following command: 

```python
pdf_parser.Parser.parse('text', input_dir, output_dir, n_threads=0)
```

To parse the image information of all PDF files in the `input_dir` and save the results to `output_dir`, use the following command: 

```python
pdf_parser.Parser.parse('figure', input_dir, output_dir, n_threads=0)
```

> Note: The `n_threads` parameter specifies the number of threads to use for parsing. The default value is **0**, which means it will use all available `CPU cores`.

**Example:**

```python
from pdf_parser import Parser
parser = Parser('cermine')
parser.parse('text', '/path/to/xxx.pdf', '/path/to/output', 50)
parser.parse('figure', '/path/to/pdf_dir    ', '/path/to/output', 50)
```

## Development progress 

Backend↓ / Type→ | text | image | reference
:-: | :-: | :-: | :-:
grobid | <font color="#00FF00">√</font> | <font color="#FF0000">×</font> | <font color="#FF0000">×</font> 
cermine | <font color="#00FF00">√</font> | <font color="#00FF00">√</font> | <font color="#FF0000">×</font>
scienceparse | <font color="#00FF00">√</font> | <font color="#FF0000">×</font> | <font color="#FF0000">×</font>
pdffigures | <font color="#FF0000">×</font> | <font color="#00FF00">√</font> | <font color="#FF0000">×</font>
pdffigures2 | <font color="#00FF00">√</font> | <font color="#00FF00">√</font> | <font color="#FF0000">×</font>

## Detail demand

Backend↓ / Requirements→ | OS | java | Other
:-: | :-: | :-: | :-:
grobid | All (Windows/Linux/Mac) | Not Need | No
cermine | All (Windows/Linux/Mac) | Need | No
scienceparse | All (Windows/Linux/Mac) | Need | No
pdffigures | Linux/Mac | Not Need | leptonica & poppler (Ubuntu: sudo apt install libpoppler-private-dev libleptonica-dev)
pdffigures2 | All (Windows/Linux/Mac) | Need | No


## Citation

```
@misc{sciparser,
  author = {Cheng Deng, Yuting Jia, Shuhao Li},
  title = {pdf_parser: All in one PDF Parser Toolkits},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/Acemap/pdf_parser}},
}
```