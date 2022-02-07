# Acquisition of a Large Domain-specific Corpus for Fine-tuning of Language Models
## Goal of the Project
Design, implement, and evaluate a system that collects text data from large open sources, e.g., Wikidata, given keywords of a specific domain of interest.
## Tasks
- Research a methodology to search and retrieve related information given
keywords in large collections of text depending on the language of the keywords.
- Design and implement an approach to collect the domain-specific data.

## Setup
The needed packages can be installed with pip
```sh
pip install -r requirements.txt
```
or as a new Anaconda evironment.
```sh
conda create --name <env> --file anaconda_requirements.txt
```
To get the most similar words function for a keyword the models from https://fasttext.cc/docs/en/crawl-vectors.html
need to be installed in the corresponding language into the fasttext_models folder and the language tag needs to be added
to the languages in definition.py.

## Usage
You need to provide a list of domain specific keywords as a python list and the corresponding language.
After that the algorithm runs and outputs the text to the specified save file.