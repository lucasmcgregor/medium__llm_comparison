# LLM Resume Data Extraction Model Comparison

This test will run a data extraction and normalization of data from a Resume and 
compare the results against the expected data and then score the performance of the 
LLM setup.

Because LLMs are statistical systems and not exact algorithms, it will run multiple runs.
It will run through all the combinations of embed and LLM models declared in the main.py file.

It will use a pre-built resume from the "./input" and compare the results against know values for scoring.

It uses Pydantic to define the normalized data to extract.

# Documents and Links

https://docs.llamaindex.ai/en/stable/module_guides/
https://ollama.com



# Setup

## Install Ollama
https://ollama.com

This is what will run a local llamam LLM system.

## Install Python and Virtual Env

Use homebrew to install python 3.12. 3.13 doesn't seem to work with llamaindex yet.

> brew install python@3.12

Install virtual environment.

> brew install virtualenv


## Setup and activate your virtual env

> /opt/homebrew/bin/virtualenv -p /opt/homebrew/bin/python3.12 p3.12
> source p3.12/bin/activate

You should now see your prompt showing that you are in a python3.12 virtual environment.


## Install the Models into Ollama

Install the models into Ollama:
```bash
ollama pull llama3.2
ollama pull llama3.3
ollama pull gemma2
ollama pull gemma3
ollama pull qwen2.5
ollama pull qwen2.5
ollama pull qwen3:0.6b
ollama pull qwen3:1.7b
ollama pull qwen3:4b
ollama pull qwen3:8b
ollama pull qwen3:14b
ollama pull qwen3:32b
ollama pull phi4
ollama pull mistral
ollama pull nomic-embed-text
ollama pull bge-m3
ollama pull granite-embedding
```

## Run the test
> python main.py --number_of_runs=10 (defaults is 5)
