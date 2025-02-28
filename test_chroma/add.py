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

def search():
    # 要查询的文本
    query_text = "示例文本"

    # 生成查询文本的嵌入向量
    query_embedding = embeddings.embed_query(query_text)

    # 执行相似度搜索，返回最相似的3条记录
    similar_cases = vector_store.similarity_search(query_text, k=3)

    # 打印查询结果
    for case in similar_cases:
        print(case.page_content)
def add():
    texts = ["这是一个示例文本", "另一个示例文本"]
    metadatas = [{"source": "example1"}, {"source": "example2"}]

    # 生成嵌入向量
    embeddings_list = embeddings.embed_documents(texts)

    # 添加数据到向量数据库
    vector_store.add_texts(
        texts=texts,
        metadatas=metadatas,
        embeddings=embeddings_list
    )


if __name__ == '__main__':
    # add()
    search()