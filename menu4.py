#from streamlit_option_menu import option_menu

## chatbot 추가

import tiktoken

from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from loguru import logger
from langchain.document_loaders import PyPDFLoader


from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings

from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import FAISS

# from streamlit_chat import message
# from langchain.callbacks import get_openai_callback
# from langchain.memory import StreamlitChatMessageHistory



def get_text(docs):
      doc_list = []


      for doc in docs:
         file_name = doc.name  # doc 객체의 이름을 파일 이름으로 사용
         with open(file_name, "wb") as file:  # 파일을 doc.name으로 저장
            file.write(doc.getvalue())
            logger.info(f"Uploaded {file_name}")
         if '.pdf' in doc.name:
            loader = PyPDFLoader(file_name)
            documents = loader.load_and_split()
        # elif '.docx' in doc.name:
        #     loader = Docx2txtLoader(file_name)
        #     documents = loader.load_and_split()
        # elif '.pptx' in doc.name:
        #     loader = UnstructuredPowerPointLoader(file_name)
        #     documents = loader.load_and_split()

         doc_list.extend(documents)
      return doc_list


def tiktoken_len(text):
       tokenizer = tiktoken.get_encoding("cl100k_base")
       tokens = tokenizer.encode(text)

       return len(tokens)


def get_text(file_paths):
       doc_list = []
       
       
       for file_path in file_paths:
           
           # file_name 대신 file_path를 직접 사용
           if file_path.endswith('.pdf'):
               loader = PyPDFLoader(file_path)
               documents = loader.load_and_split()

           doc_list.extend(documents)
       return doc_list

def get_text_chunks(text):
       text_splitter = RecursiveCharacterTextSplitter(
          chunk_size=750,
          chunk_overlap=100,
          length_function=tiktoken_len
       )
       chunks = text_splitter.split_documents(text)
       return chunks


def get_vectorstore(text_chunks):
       embeddings = HuggingFaceEmbeddings(
                                        model_name="jhgan/ko-sroberta-multitask",
                                        model_kwargs={'device': 'cpu'},
                                        encode_kwargs={'normalize_embeddings': True}
                                        )
       vectordb = FAISS.from_documents(text_chunks, embeddings)
       return vectordb


def get_conversation_chain(vetorestore,openai_api_key):
       llm = ChatOpenAI(openai_api_key=openai_api_key, model_name = 'gpt-3.5-turbo',temperature=0)
       conversation_chain = ConversationalRetrievalChain.from_llm(
               llm=llm,
               chain_type="stuff",
               retriever=vetorestore.as_retriever(search_type = 'mmr', vervose = True),
               memory=ConversationBufferMemory(memory_key='chat_history', return_messages=True, output_key='answer'),
               get_chat_history=lambda h: h,
               return_source_documents=True,
               verbose = True
       )

       return conversation_chain



# #def main():  -- 메인페이지로 이관
# st.title(" 	:mag_right: 영주시 관광지 검색 AI 챗봇")

# if "conversation" not in st.session_state:
#     st.session_state.conversation = None

# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = None

# if "processComplete" not in st.session_state:
#     st.session_state.processComplete = None
#     local_file_paths = ['2024_학교폭력_처리가이드.pdf'] #챗봇 사전 학습 데이터
#     openai_api_key = "" # 개인 API 번호
#     files_text = get_text(local_file_paths)
#     text_chunks = get_text_chunks(files_text)
#     vetorestore = get_vectorstore(text_chunks)

#     st.session_state.conversation = get_conversation_chain(vetorestore,openai_api_key)

#     st.session_state.processComplete = True

# if 'messages' not in st.session_state:
#     st.session_state['messages'] = [{"role": "assistant",
#                                   "content": "안녕하세요! 영주시 관광지 검색 인공지능 챗봇이에요. 궁금한것을 물어봐 주세요!"}]

# for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

# history = StreamlitChatMessageHistory(key="chat_messages")

#     # Chat logic
# if query := st.chat_input("질문을 입력해주세요."):
#       st.session_state.messages.append({"role": "user", "content": query})

#       with st.chat_message("user"):
#             st.markdown(query)

#       with st.chat_message("assistant"):
#             chain = st.session_state.conversation

#             with st.spinner("잠시만 기다려주세요..."):
#                 result = chain({"question": query})
#                 with get_openai_callback() as cb:
#                     st.session_state.chat_history = result['chat_history']
#                 response = result['answer']
#                 #빅source_documents = result['source_documents']

#                 st.markdown(response)
#                 # with st.expander("출처확인"):
#                 #     st.markdown(source_documents[0].metadata['source'], help = source_documents[0].page_content)

#       # Add assistant message to chat history
#       st.session_state.messages.append({"role": "assistant", "content": response})