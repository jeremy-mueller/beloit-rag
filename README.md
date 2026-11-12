# RAG Intelligence System for Beloit College
*Jeremy Mueller and Taman Azad*

## What it does
We created a RAG intelligence system using Beloit College documents. The system takes a question from a user, retrieves context from our corpus of 37 documents, gives the context to Gemini-3.5-Flash-Lite, and returns an answer to the question based on the retrieved context.

## Who it is for
The system is for Beloit College students who want answers to questions regarding academic, residential, financial, and general student affairs. Being able to ask your questions to a system to retrieve and answer it for you is easier than finding the required document yourself, and going through a bunch of pages to find what you need.

## Reproduction
Our code is run primarily with Python and Jupyter Notebook. Required sources are already cached in the raw folder, and documents split and kept in the corpus folder. To install the prerequisite packages run:
```
pip install -r requirements.txt
```
Ensure the environment variable ```GOOGLE_CLOUD_PROJECT``` is set to a Google Cloud project with billing set up and the Agent Platform API is enabled.\
Open Jupyter in your terminal with:
```
jupyter notebook
```
and open pipeline.ipynb. Run each cell in order to chunk and embed the documents, and then evaluate on the test questions.

## Repository Layout
|File|What it is|
|-|-|
|README.md|Project overview|
|pipeline.ipynb|Embedding, answering, and evaluation|
|chunk_compare.py|Chunking code|
|documents.tsv|Breakdown of documents used for ingestion|
|executive_summary.md|Short summary for a non-technical audience|
|ingestion_plan.md|How the corpus was chosen and what needed manual handling|
|analysis/test_questions.md|Ten preliminary test questions|
|analysis/evaluation_set.md|29 evaluation questions with expected output and sources|
|analysis/results.md|Comparison between baseline and improved with metrics|
|analysis/failure_taxonomy.md|Categorized and counted failures with examples|
|raw/|Raw information source files|
|corpus/|Split and cleaned documents|
