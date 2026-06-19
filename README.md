# Einstein-AI
An artificial intelligence containing all of Einstein's ideas, philosophies, and works.

This project implements a Retrieval-Augmented Generation (RAG) chatbot that allows you to interact with the writings and philosophies of Albert Einstein. It uses LangChain, FAISS for vector storage, and the TinyLlama-1.1B-Chat model.

## Prerequisites

- Python 3.10 to 3.13 (Recommended)
  - *Note: Python 3.14 is supported but may require newer package versions.*
- `pip` (Python package installer)

### Windows Requirements
If you are on Windows, ensure you have the **Microsoft C++ Build Tools** installed, as some dependencies may need to compile native code. You can download them from [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

## Installation

1. Clone the repository to your local machine.
2. Navigate to the project root directory.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Setup (Data Ingestion)

Before running the bot for the first time, or if you update the source texts in `einstein_ai/data/`, you need to build the FAISS vector index:

```bash
python -m einstein_ai.ingest
```

This script will process the text files, split them into chunks, and create a local vector store in `einstein_ai/faiss_index/`.

## Running the Bot

Once the index has been created, you can start the interactive session with Einstein AI:

```bash
python main.py
```

Type your questions at the prompt. To exit the session, type `exit` or `quit`.

## Project Structure

- `einstein_ai/`: Core package containing the AI logic and data.
  - `data/`: Directory for source text files.
  - `einstein_bot.py`: Logic for initializing the LLM and RAG chain.
  - `ingest.py`: Script to process text data into the FAISS index.
- `main.py`: Interactive CLI entry point.
- `requirements.txt`: List of Python dependencies.
