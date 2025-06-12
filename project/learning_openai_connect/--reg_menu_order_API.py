# 学習用：ベクトルDBを使用した、AI推測機能
# 出力されるベクトルDB：menu_vectorstore、pkl：セキュリティリスクあり
# 単純なメニュー推論であればr「apidfuzz」で十分なため必要なし

import os
import re
from rapidfuzz import process
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# メニュー情報
menu_data = [
    "特製からあげ: ジューシーな鶏もも肉を秘伝のタレで揚げた逸品です。",
    "スパイシーカレー: スパイスを効かせた牛肉たっぷりのカレーです。",
    "手打ちうどん: コシのある自家製麺のうどんです。"
]

docs = [Document(page_content=content) for content in menu_data]

def get_menu(query):

    # ベクトルDB作成
    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)

    vectorstore_path = "menu_vectorstore"
    index_file = os.path.join(vectorstore_path, "index.faiss")
    store_file = os.path.join(vectorstore_path, "index.pkl")  # メタ情報

    if os.path.exists(index_file) and os.path.exists(store_file):
        print("OK:",vectorstore_path)
        vectordb = FAISS.load_local("menu_vectorstore", 
        embedding, 
        allow_dangerous_deserialization=True)
    else:
        print("NO:",vectorstore_path)
        vectordb = FAISS.from_documents(docs, embedding)
        vectordb.save_local("menu_vectorstore")

    # ④ Retrieval + GPTによる回答生成
    llm = ChatOpenAI(temperature=0, openai_api_key=openai_api_key)
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(search_kwargs={"k": 1}),
        chain_type="stuff"
    )

    result = qa.run(query)
    return result
