# GeoVault AI Knowledge Platform

Production RAG built on **pure LangChain + LangGraph** (+ optional LangSmith).

## LangChain / LangGraph ownership

| Stage | Framework shortcut | Module |
|-------|-------------------|--------|
| Load documents | LangChain loaders by type (`text` / `pdf` / `office` / `tabular` / `image` / `audio`) — `app/ingestion/loaders/` |
| Split / chunk | `RecursiveCharacterTextSplitter.split_documents()` | `app/ingestion/chunking/splitter.py` |
| Embed | `OllamaEmbeddings` / `OpenAIEmbeddings` | `app/ai/embeddings/langchain_factory.py` |
| Vector index | `VectorStore.add_documents()` / `.delete(filter=…)` | `app/ai/vectorstore/` |
| Retrieve | `vectorstore.as_retriever(...).ainvoke(query)` | `app/ai/retrieval/rag.py` |
| Prompt | `ChatPromptTemplate` + `MessagesPlaceholder` | `app/ai/prompts/rag.py` |
| Generate | LCEL `prompt \| model \| StrOutputParser()` | `app/ai/workflows/chat/nodes/rag_nodes.py` |
| Chat LLM | `ChatOllama` / `ChatOpenAI` | `app/ai/llm/langchain_factory.py` |
| Ingest orchestration | LangGraph `load → split → embed_index` | `app/ai/workflows/ingestion/` |
| Chat orchestration | LangGraph `guardrails → retrieve → generate → evaluate` | `app/ai/workflows/chat/` |
| Observability | LangSmith | `app/ai/observability/langsmith.py` |

## Flows

### Ingestion (LangGraph)

```text
START → load (LangChain loaders)
      → split (RecursiveCharacterTextSplitter.split_documents)
      → embed_index (VectorStore.add_documents — embeds + indexes)
      → END
```

### Chat (LangGraph)

```text
START → input_guardrails
      → retrieve (as_retriever)
      → generate (ChatPromptTemplate | chat_model | StrOutputParser)
      → output_guardrails
      → evaluate
      → END
```

## Setup

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
pip install -r requirements.txt
```

Switch providers via `.env`:

```env
LLM_PROVIDER=ollama|openai|gemini
EMBEDDING_PROVIDER=ollama|openai|gemini
```
