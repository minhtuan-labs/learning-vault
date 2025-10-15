from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from core.config import settings
from core.logger import get_logger
from openai import APIConnectionError

logger = get_logger(__name__)

qa_chain = None
is_ready = False

def initialize_rag_chain():
	global qa_chain, is_ready

	logger.info("Initializing Conversational RAG Service...")
	try:
		llm = ChatOpenAI(base_url=settings.LLM_API_URL, api_key=settings.API_KEY, model=settings.MODEL_NAME)
		embedding_function = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
		vector_db = Chroma(persist_directory=settings.DB_PATH, embedding_function=embedding_function)

		retriever = vector_db.as_retriever(
			search_type=settings.RETRIEVER_SEARCH_TYPE,
			search_kwargs={"k": settings.RETRIEVER_SEARCH_KWARGS_K}
		)

		memory = ConversationBufferMemory(
			memory_key=settings.PROMPT_CHAT_HISTORY_KEY,
			return_messages=True,
			output_key=settings.MEMORY_OUTPUT_KEY
		)

		with open(settings.PROMPT_PATTERN_FILE, "r", encoding="utf-8") as f:
			raw_template = f.read()

		final_qa_template_string = raw_template.replace(
			"{{PROMPT_CHAT_HISTORY_KEY}}", f"{{{settings.PROMPT_CHAT_HISTORY_KEY}}}"
		).replace(
			"{{PROMPT_CONTEXT_KEY}}", f"{{{settings.PROMPT_CONTEXT_KEY}}}"
		).replace(
			"{{PROMPT_INPUT_KEY}}", f"{{{settings.PROMPT_INPUT_KEY}}}"
		)

		QA_PROMPT = PromptTemplate.from_template(final_qa_template_string)

		condense_question_template = f"""
        Given the following conversation and a follow up question, rephrase the follow up question 
        to be a standalone question, in its original language.
        Chat History:
        {{{settings.PROMPT_CHAT_HISTORY_KEY}}}
        Follow Up Input: {{{settings.PROMPT_INPUT_KEY}}}
        Standalone question:"""
		CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(condense_question_template)

		qa_chain = ConversationalRetrievalChain.from_llm(
			llm=llm,
			retriever=retriever,
			memory=memory,
			condense_question_prompt=CONDENSE_QUESTION_PROMPT,
			combine_docs_chain_kwargs={"prompt": QA_PROMPT},
			return_source_documents=False,
		)

		is_ready = True
		logger.info("Conversational RAG Service is ready.")
	except Exception as e:
		is_ready = False
		qa_chain = None
		logger.error(f"Error initializing RAG Service: {e}", exc_info=True)

def reload():
	"""Tải lại RAG chain để cập nhật kiến thức mới."""
	initialize_rag_chain()

def ask_question(question: str):
	if not is_ready or not qa_chain:
		raise Exception("RAG Service is not initialized properly.")

	try:
		result = qa_chain({settings.PROMPT_INPUT_KEY: question})
		return result.get(settings.MEMORY_OUTPUT_KEY, 'Sorry, I encountered an error.')
	except APIConnectionError:
		raise Exception("Could not connect to LM Studio Server.")
	except Exception as e:
		raise Exception(f"An error occurred during processing: {e}")

initialize_rag_chain()
