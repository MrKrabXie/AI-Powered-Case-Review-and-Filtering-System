from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# 初始化嵌入模型
embeddings = OllamaEmbeddings(model="mistral")

# 初始化向量数据库
vector_store = Chroma(
    collection_name="audit_cases",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)