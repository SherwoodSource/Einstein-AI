import os
# Set USER_AGENT at the very top to avoid warnings from LangChain/HuggingFace
os.environ["USER_AGENT"] = "EinsteinAI/1.0 (Retriever Bot)"

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
from einstein_ai.utils import logger

# Load HF_TOKEN and potentially source URLs from environment file
load_dotenv("HF_TOKEN.env")

def get_einstein_bot():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = FAISS.load_local("einstein_ai/faiss_index", embeddings, allow_dangerous_deserialization=True)

    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    tokenizer = AutoTokenizer.from_pretrained(model_id, clean_up_tokenization_spaces=False)

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )

    # Define generation config to avoid any mixing of parameters
    # This is the most surgical way to avoid "both max_new_tokens and max_length set"
    model.generation_config.max_new_tokens = 256
    model.generation_config.max_length = 2048
    model.generation_config.temperature = 0.7
    model.generation_config.do_sample = True
    model.generation_config.pad_token_id = tokenizer.pad_token_id
    model.generation_config.eos_token_id = tokenizer.eos_token_id

    # We update the model.config as well to ensure total consistency
    model.config.max_new_tokens = 256

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        return_full_text=False,
    )

    llm = HuggingFacePipeline(pipeline=pipe)

    template = """<|system|>
You are Albert Einstein. Use the following pieces of context from your own writings to answer the user's question.
Maintain a wise, humble, and scientific tone.

Context: {context}</s>
<|user|>
{question}</s>
<|assistant|>
"""

    prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    # Set k=3 to stay within 2048 token limit
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=False,
        chain_type_kwargs={"prompt": prompt}
    )

    return chain

if __name__ == "__main__":
    bot = get_einstein_bot()
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "What is the relationship between space and time?"
    result = bot.invoke({"query": query})
    print(result['result'])
