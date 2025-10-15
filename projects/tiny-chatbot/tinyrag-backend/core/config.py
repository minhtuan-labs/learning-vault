from pydantic_settings import BaseSettings

class Settings(BaseSettings):
	# Biến cho LLM & Embedding
	LLM_API_URL: str = "http://host.docker.internal:1234/v1"
	MODEL_NAME: str = "local-model"
	API_KEY: str = "not-needed"
	EMBEDDING_MODEL: str = 'all-MiniLM-L6-v2'

	# Biến cho CSDL và đường dẫn
	DATA_PATH: str = "data"
	DB_PATH: str = "db"
	METADATA_FILE: str = "metadata.json"

	# Biến cho Prompt
	PROMPT_PATTERN_FILE: str = "prompt_pattern.txt"
	PROMPT_CONTEXT_KEY: str = "context"
	PROMPT_INPUT_KEY: str = "input" # Need to be different from docker-compose.yml for testing
	PROMPT_CHAT_HISTORY_KEY: str = "chat_history"
	MEMORY_OUTPUT_KEY: str = "answer"

	# Biến cho API & Logging
	PAGE_SIZE: int = 10
	LOG_LEVEL: str = "INFO"

	# Biến cho Retriever
	RETRIEVER_SEARCH_TYPE: str = "mmr"
	RETRIEVER_SEARCH_KWARGS_K: int = 5

	class Config:
		env_file = ".env"
		env_file_encoding = "utf-8"

settings = Settings()

