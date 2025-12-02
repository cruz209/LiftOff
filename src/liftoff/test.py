
from liftoff import LiftOff

if __name__ == "__main__":
    lf = LiftOff()  # relies on OPENAI_API_KEY or HUGGINGFACE_TOKEN env var
    lf.create("Create a simple Flask RAG (retrieval augmented generation) app that can upload PDFs and ask questions about them using the OpenAI Api key.")
