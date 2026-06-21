# Einstein-AI
An artificial intelligence containing all of Einstein's ideas, philosophies, and works.

This project implements a Retrieval-Augmented Generation (RAG) chatbot that allows you to interact with the writings and philosophies of Albert Einstein. It uses LangChain, FAISS for vector storage, and the TinyLlama-1.1B-Chat model.

## Project Structure

- `einstein_ai/`: Core package containing the AI logic and data.
  - `data/`: Directory for source text files.
  - `einstein_bot.py`: Logic for initializing the LLM and RAG chain.
  - `ingest.py`: Script to process text data into the FAISS index.
- `main.py`: Interactive CLI entry point.
- `requirements.txt`: List of Python dependencies.
- `SOURCES.env`: Configuration for online text sources and triggers.
- `EinsteinAI.ps1`: PowerShell-based graphical interface.
- `EinsteinAI.bat`: Silent launcher for the Windows GUI.

## Prerequisites

- Python 3.10 to 3.13 (Recommended)
  - *Note for Python 3.13+: Ensure you have a recent version of pip (`pip install -U pip`) and use the recommended installation command below to avoid build errors.*
  - *Note: Python 3.14 is supported but may require newer package versions.*
- `pip` (Python package installer)

### Windows Requirements
If you are on Windows, ensure you have the **Microsoft C++ Build Tools** installed, as some dependencies may need to compile native code. You can download them from [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

## Installation

1. Clone the repository to your local machine.
2. Navigate to the project root directory.
3. Install the required dependencies (use the `-U` flag to ensure all conflicting versions are updated):
   ```bash
   pip install -U -r requirements.txt
   ```
4. Create a file named `HF_TOKEN.env` in the root directory and add your Hugging Face API token:
   ```text
   HF_TOKEN=your_huggingface_token_here
   ```
5. (Optional) Review `SOURCES.env` to manage online Einstein sources and trigger words.

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

Type your questions at the prompt. To end the session and close the bot, type `exit`, `quit`, `bye`, or `stop`.

## Running the Bot (GUI Mode - Windows)

On Windows, you can launch the bot with a clean graphical interface and no background terminal:
- Double-click **`EinsteinAI.bat`**
- Or run `powershell -File EinsteinAI.ps1`

## Troubleshooting

### ModuleNotFoundError: No module named 'langchain.chains'
This usually occurs if `langchain` was not installed correctly or if there is a version conflict. Ensure you have run:
```bash
pip install -r requirements.txt
```
If the error persists, try installing the package explicitly:
```bash
pip install langchain==0.3.14
```
