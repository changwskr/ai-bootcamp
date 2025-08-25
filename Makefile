.PHONY: setup dev test lint fmt nb run api clean train chat-demo chat-image trymultiagentopenai trymultiagentchat basicexam rag-basic-pdf langgraph-building-graph

setup:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m pip install fastapi uvicorn python-dotenv pydantic hydra-core mlflow python-multipart
	set PYTHONPATH=src && .venv\Scripts\python.exe -m pip install openai pillow requests
	set PYTHONPATH=src && .venv\Scripts\python.exe -m pip install langchain-openai langchain-core langgraph
	set PYTHONPATH=src && .venv\Scripts\python.exe -m pip install langchain-text-splitters langchain-community faiss-cpu pymupdf sentence-transformers langchain-huggingface torch langchain-teddynote graphviz pydot matplotlib
	set PYTHONPATH=src && .venv\Scripts\python.exe -m pip install ruff black isort pytest pytest-cov mypy pre-commit jupytext ipykernel
	pre-commit install

dev:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m ipykernel install --user --name ai-bootcamp

test:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m pytest

lint:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m ruff check .
	set PYTHONPATH=src && .venv\Scripts\python.exe -m mypy src

fmt:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m black .
	set PYTHONPATH=src && .venv\Scripts\python.exe -m isort .

nb:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m jupyter notebook

api:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m uvicorn ai_bootcamp.app.api:app --host 0.0.0.0 --port 8000

train:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m ai_bootcamp.app.cli

chat-demo:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m ai_bootcamp.app.demo.prac01.chatdemo

chat-image:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m ai_bootcamp.app.demo.prac02.chatimage

chat-langchain:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m ai_bootcamp.app.demo.prac02.langchainchat

langraphex:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m ai_bootcamp.app.demo.prac02.langraphex

langgraphex02:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m ai_bootcamp.app.demo.prac02.langgraphex02

langgraphex03:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m ai_bootcamp.app.demo.prac02.langgraphex03

multiagent:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m ai_bootcamp.app.demo.multiagent.multiagent

trymultiagent:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m ai_bootcamp.app.demo.multiagent.trymultiagent

trymultiagent2:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m ai_bootcamp.app.demo.multiagent.trymultiagent2

trymultiagent3:
	set PYTHONPATH=src && .venv\Scripts\python.exe -m ai_bootcamp.app.demo.multiagent.trymultiagent3

basicexam:
	set PYTHONPATH=src && .venv\Scripts\python.exe src/ai_bootcamp/app/demo/multiagent/basicexam.py

trymultiagentopenai:
	@echo Loading .env file and running trymultiagentopenai...
	@call run_with_env.bat

trymultiagentchat:
	@echo Loading .env file and running trymultiagentchat...
	@call run_with_env_azure.bat

rag-basic-pdf:
	@echo Running RAG Basic PDF demo...
	set PYTHONPATH=src && .venv\Scripts\python.exe src\ai_bootcamp\app\demo\rag\12-RAG\rag_basic_pdf.py

rag-basic-pdf-local:
	@echo Running RAG Basic PDF demo (Local Model)...
	set PYTHONPATH=src && .venv\Scripts\python.exe src\ai_bootcamp\app\demo\rag\12-RAG\rag_basic_pdf_local.py

langgraph-building-graph:
	@echo Running LangGraph Building Graph demo...
	set PYTHONPATH=src && .venv\Scripts\python.exe src\ai_bootcamp\app\demo\langraph\17-LangGraph\02-Structures\01-langgraph-building-graph.py

clean:
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist .mypy_cache rmdir /s /q .mypy_cache
	if exist dist rmdir /s /q dist
	if exist build rmdir /s /q build
	if exist .ruff_cache rmdir /s /q .ruff_cache

step01:
	dir

step02:
	make api 