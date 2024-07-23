import random
import requests
from openai import OpenAI
from langchain_openai import ChatOpenAI
from bs4 import BeautifulSoup
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter



def random_number():
    return str(sorted(random.sample(range(1, 46), 6)))



def kospi():
    KOSPI_URL = 'https://finance.naver.com/sise/' #주소 가져오기

    res = requests.get(KOSPI_URL) #주소 읽기

    res_text = res.text

    selector = '#KOSPI_now' # 주소 중 가져올 데이터 선택

    soup = BeautifulSoup(res_text, 'html.parser') # html 파싱
    kospi = soup.select_one(selector).text

    return kospi

def openai(api_key, user_input):
    client = OpenAI(api_key=api_key)

    completion = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': '너는 심심한 사용자와 대화하는 챗봇이야, 출력에서 #은 뺴서 답해줘'},
            {'role': 'user', 'content': user_input},
        ]
    )

    return completion.choices[0].message.content


def langchain(api_kwy, user_input):
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

    loader = WebBaseLoader(
        web_paths=(
            'https://ko.wikipedia.org/wiki/%EC%95%A0%ED%94%8C_%EC%84%B8%EA%B3%84_%EA%B0%9C%EB%B0%9C%EC%9E%90_%ED%9A%8C%EC%9D%98'
            'https://www.apple.com/kr/newsroom/2024/03/apples-worldwide-developers-conference-returns-june-10-2024/'
            ),
    )

    docs = loader.load()

    # 2. split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)


    # 3. store
    vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

    # 4. retrieve
    retriever = vectorstore.as_retriever()
    prompt = hub.pull("rlm/rag-prompt")


    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain.invoke(user_input)