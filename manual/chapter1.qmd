---
title: "Project Setup"
---
# Roberto's Cookiecutter Data Science

*My own standardized project structure for data science projects.*

> This is personalized to my own comfort and may not be the best practice for organizing a project structure.

## Installation & Setup

**Step 1**: Clone the repository to your local environment.
```bash
git clone https://github.com/betopark97/cookiecutter-data-science.git
```

**Step 2**: Check for existing remotes, if not initialize git or connect to your own repository in the next step.
```bash
git remote -v
```

**Step 3**: Replace the existing origin (remote) with the following command (`<new_url>` is a placeholder for the repository where you want to push with this cookiecutter).
```bash
git remote set-url origin <new_url>
```

**Step 3-1 (optional)**: This step is instead of the previous step. It will remove an existing origin and add a new one.
```bash
git remote remove origin
git remote add origin <new_url>
```

**Step 4 (optional)**: This step is to erase the .gitkeep files in the empty directories. You may choose to keep them if you want to and skip this step.
```bash
python remove_gitkeep.py
```

## Project Structure

After cloning this repository, the structure of the data science project should look like the following:  

> The tree below comes with an explanation of the use case of each of the subdirectories and files.

```bash
├── LICENSE                 -> MIT License (mine)
├── README.md               -> Explanation of Project
├── data                    -> Data for Project
│   ├── external            -> Data from third party sources
│   ├── interim             -> Intermediate data that has been transformed
│   ├── processed           -> Final dataset for modeling
│   └── raw                 -> Original, immutable dataset
├── databases               -> Connection to databases, or store databases
├── misc                    -> Any miscellaneous files
├── models                  -> Trained, serialized models
├── notebooks               -> Jupyter notebooks
├── references              -> Data catalogue, manuals or materials
├── remove_gitkeep.py       -> Python file to remove .gitkeep files from directory
├── reports                 -> Final deliverable of the project
│   └── figures             -> Visual aids (plots, graphs) for the final deliverable
├── requirements.txt        -> Requirements to reproduce the packages necessary for the project
├── src                     -> Source code for the project
│   └── utils               -> Utilities for project source code
└── tests                   -> Tests for different features of the project
```

## Misc.

You can check this repository at [Roberto's Cookiecutter Data Science](https://github.com/betopark97/cookiecutter-data-science).

It will be frequently updated.

---

# Connect a Github Repository

## Change Upstream Repository

1. Check your current remote:
```bash
git remote -v
```

2. Remove the current remote:
```bash
git remote remove origin
```

3. Add a new remote:
```bash
git remote add origin <new_repository_url>
```

4. Verify the new remote:
```bash
git remote -v
```

5. Push your changes to the new remote
```bash
git push -u origin main
```

---

# Add a README.md File

> The information below is not in specific order and some sections may be optional.

## Title of the Project

- Purpose: clearly state the project name
- Tips: Use a large heading (# Project Name) so it stands out. Consider including a short tagline that summarizes the project in one line.

## Brief description

- Purpose: Provide a concise summary of what the project does, its purpose (the why), and the problem it solves.
- Tips: 
	- Use 1-3 sentences to capture attention and set context.
	- Optionally, include a badge section right below with things like build status, license type, or coverage.

## Table of Contents

- Purpose: Helps users navigate the README easily, especially in larger documents.
- Tips:
	- List each main section as a link (using markdown [Section] (#section) format).
	- Place it right after the description for quick access.

## Installation guide

- Purpose: Guide users through the steps required to install and set up the project.
- Tips:
	- Break down instructions for different environments (Linux, macOS, Windows).
	- Include any prerequisites (e.g., Python version, libraries).
	- Use code blocks to show command-line instructions.

## Usage Instructions

- Purpose: Explain how to use the project, including common commands or steps.
- Tips:
	- Provide example commands, sample inputs, and expected outputs.
	- Include any configuration options or environment variables.
	- If it's a web application, describe how to start the server and access it.
	- Optionally, add code snippets that demonstrate functionality.

## License Information

- Purpose: Clearly specify the licensing terms. 
- Tips:
	- Indicate the type of license (e.g., MIT, Apache 2.0) and add a link to the full license file (e.g., LICENSE).

## Acknowledgements

- Purpose: Credit people, organizations, or libraries that contributed to or inspired the project.
- Tips:
	- Acknowledge any collaborators, mentors, or open-source libraries used.
	- Mention specific contributors if they're significant.

## Example Screenshots

- Purpose: Visually demonstrate the project in action.
- Tips:
	- Include images or GIFs showing the main features and user interface.
	- Use descriptive captions for each screenshot.
	- Markdown for images:
	
```markdown
# markdown
![Screenshot of feature](images/feature-screenshot.png)

# html
<img height=200px src="images/feature-screenshot.png" />
```

## References

- Purpose: List any resources, articles, or documentation that influenced or supported the project.
- Tips:
	- Include relevant links to documentation, tutorials, or other related projects.
	- Use bullet points to list each reference.

## Contact

- Purpose: Provide ways to reach out for questions, issues, or feedback.
- TIps:
	- Include a professional email or link to your social media/LinkedIn profile.
	- You might add a note encouraging users to submit GitHub issues for bugs or feature requests.
```markdown
Maintained by [Roberto Park](mailto:betopark97@gmail.com).
```

---

# Virtual Environment

## First make an environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install Libraries
- Data Management
```bash
pip3 install python-dotenv dvc
```
- Data Analysis
```bash
pip3 install numpy pandas matplotlib seaborn
```
- Machine Learning
```bash
pip3 install mlflow sklearn tensorflow pytorch
```
- Databases
```bash
pip3 install psycopg2-binay sqlalchemy duckdb
```

## Import Libraries
```python
# Operation System
import os
import pathlib
from dotenv import load_dotenv

# Database
import duckdb
import psycopg2
import sqlalchemy

# Data Analysis
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Statistics (inferential)
import scipy

# Machine Learning
import mlflow
import sklearn
import tensorflow
import pytorch

# Load .env variables
load_dotenv()
```
## Document Dependencies
1. Make requirements file
```bash
pip3 freeze > requirements.txt
pip3 install -r requirements.txt
```
2. Manage a configuration file (RYE, UV, Poetry)
# Misc.
1. Check environment
```bash
which pip3
which python3
pip3 show
```
2. Managing configurations with .ini or .cfg files
```bash
# ini
[Database]
host = localhost
port = 5432
user = admin

# json
{
	"Database": {
		"host": "localhost",
		"port": 5432,
		"user": "admin"
	}
}

# yaml
Database:
  host: localhost
  port: 5432
  user: admin

# 
```
3. In python parsing
```python
# INI
import configparser

def load_config(file_path):
	config = configparser.ConfigParser()
	config.read(file_path)
	return config

# JSON
import json

def load_config(file_path):
	with open(file_path, 'r') as f:
		config = json.load(f)
	return config

# YAML
pip install pyyaml

import yaml

def load_config(file_path):
	with open(file_path, 'r') as f:
		config = yaml.safe_load(f)
	return config


# Example usage
config = load_config('config.cfg')
host = config['Database']['host']
port = config['Database']['port']
user = config['Database']['user']

print(f"Host: {host}, Port: {port}, User: {user}")
```

---

# PostgreSQL via psql

## Connect to PostgreSQL

1. Make connection
```bash
psql -U postgres
```

2. Check for Databases
```bash
\l
```

3. Create a Database
```bash
CREATE DATABASE <db_name>;
```

4. Connect to a Database
```bash
\c <db_name>
```

5. List all tables
```bash
\dt
```

6. Check a table schema
```bash 
\d <table_name>
```

---

# Setup Docker (Optional)