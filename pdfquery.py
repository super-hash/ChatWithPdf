import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader, TextLoader, CSVLoader,UnstructuredWordDocumentLoader
from textsplitter import ChineseTextSplitter
import pandas as pd
from langchain.embeddings.openai import OpenAIEmbeddings

class DocumentQuery:
    def __init__(self):
        os.environ["OPENAI_API_KEY"] = "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"
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

        self.chain = None
        self.db = None


    def ask(self, question: str) -> str:
        if self.chain is None:
            response = "请添加文件."
        else:
            from langdetect import detect
            detected_lang = detect(question)
            print(question)
            print(detected_lang)
            if detected_lang == 'zh-cn' or detected_lang == 'ko':
                detected_lang = "中文"
            else: detected_lang = "英文"
            prompt = f'请使用{detected_lang}回答'
            docs = self.db.get_relevant_documents(question)
            response = self.chain.run(input_documents=docs, question=prompt+question)                         

        return response

    def ingest(self, file_path: os.PathLike) -> None:
        print("begin ingest"+file_path)
        docs = load_file(file_path)
        self.db = Chroma.from_documents(docs, self.embeddings).as_retriever()
        print("end Chroma")
        self.chain = load_qa_chain(self.llm, chain_type="stuff")
        print("end ingest"+file_path)



def load_file(filepath, sentence_size=100):

    if filepath.lower().endswith(".txt"):
        loader = TextLoader(filepath, autodetect_encoding=True)
        textsplitter = ChineseTextSplitter(pdf=False, sentence_size=sentence_size)
        docs = loader.load_and_split(textsplitter)
    elif filepath.lower().endswith(".pdf"):
        print("begin load_file pdf")
        loader = PyPDFLoader(filepath)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
        docs = text_splitter.split_documents(documents)
        print("end load_file pdf")
    elif filepath.lower().endswith(".csv"):
        loader = CSVLoader(filepath)
        docs = loader.load()
    elif filepath.lower().endswith(".docx"):                                                                                                                        
        loader = UnstructuredWordDocumentLoader(filepath, mode="elements")
        textsplitter = ChineseTextSplitter(pdf=False, sentence_size=sentence_size)
        docs = loader.load_and_split(textsplitter)
    elif filepath.lower().endswith(".xlsx"):
        xlsx_to_csv_pd(filepath[:-5])
        filepath = filepath[:-5] + '.csv'
        loader = CSVLoader(filepath)
        docs = loader.load()
    print('1111111111')
    write_check_file(filepath, docs)
    return docs


def write_check_file(filepath, docs):
    print("begin write_check_file"+filepath)
    import time
    time_tag = time.strftime("%Y-%m-%d-%H", time.localtime())
    folder_path = os.path.join(os.path.dirname(filepath), time_tag+"tmp_files")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    fp = os.path.join(folder_path, 'load_file.txt')
    with open(fp, 'a+', encoding='utf-8') as fout:
        fout.write("filepath=%s,len=%s" % (filepath, len(docs)))
        fout.write('\n')
        for i in docs:
            fout.write(str(i))
            fout.write('\n')
        fout.close()
    print("end write_check_file"+filepath)


def xlsx_to_csv_pd(filename):
    data_xls = pd.read_excel(filename+'.xlsx', index_col=0, engine='openpyxl')
    data_xls.to_csv(filename+'.csv', encoding='utf-8')
