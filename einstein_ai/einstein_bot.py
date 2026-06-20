import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch

# Load HF_TOKEN from environment file
load_dotenv("HF_TOKEN.env")

def get_einstein_bot():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = FAISS.load_local("einstein_ai/faiss_index", embeddings, allow_dangerous_deserialization=True)

    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    # Fix: Set clean_up_tokenization_spaces to False to avoid warning
    tokenizer = AutoTokenizer.from_pretrained(model_id, clean_up_tokenization_spaces=False)
    # Fix: Use dtype instead of torch_dtype to avoid deprecation warning
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )

    # Fix: To avoid generation_config warning, we define the parameters in the pipeline
    # and ensure they don't conflict with any default config.
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=256,
        temperature=0.7,
        do_sample=True,
        return_full_text=False,
    )

    llm = HuggingFacePipeline(pipeline=pipe)

    # TinyLlama chat template format
    template = """<|system|>
You are Albert Einstein. Use the following pieces of context from your own writings to answer the user's question.
Maintain a wise, humble, and scientific tone.

Context: {context}</s>
<|user|>
{question}</s>
<|assistant|>
"""

    prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={"k": 2}),
        return_source_documents=False,
        chain_type_kwargs={"prompt": prompt}
    )

    return chain

if __name__ == "__main__":
    print("Initializing Einstein AI... (this may take a minute)")
    bot = get_einstein_bot()
    query = "What is the relationship between space and time?"
    result = bot.invoke({"query": query})
    print(f"\nQuestion: {query}")
    print(f"Einstein: {result['result']}")
