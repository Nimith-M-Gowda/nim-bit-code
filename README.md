# 🚀 nim-bit-code

**A RAG-powered interactive code assistant** that helps you understand and navigate your codebase using natural language queries.

nim-bit-code leverages Retrieval-Augmented Generation (RAG) to index your code repository and provide intelligent, context-aware answers about your codebase through an interactive REPL interface.

---

## ✨ Features

- 🤖 **AI-Powered Code Assistant** - Ask questions about your codebase in natural language
- 🔍 **Hybrid Search** - Combines semantic search with lexical search for accurate code retrieval
- 💾 **Persistent Memory** - Maintains conversation history and sessions
- 🗂️ **Code Indexing** - Automatically indexes your codebase for fast retrieval
- 📝 **Multiple LLM Support** - Works with OpenAI, Anthropic, and HuggingFace models
- 🔐 **Session Management** - Create and switch between multiple conversation sessions
- ⚙️ **Highly Configurable** - Customize embeddings, vector stores, and LLM providers

---

## 📋 Requirements

- **Python**: 3.11 to 3.12
- **Package Manager**: Poetry (recommended)

---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Nimith-M-Gowda/nim-bit-code.git
cd nim-bit-code
```

### 2. Install Dependencies

Using Poetry:

```bash
poetry install
```

Or using pip:

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Add your API keys:

```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
HUGGINGFACE_API_KEY=your_huggingface_key_here
CHROMA_API_KEY=your_chroma_key_here (optional)
```

### 4. Configure the Application

Edit `config.yaml` to customize:

- **LLM Provider**: Choose between `openai`, `anthropic`, or `huggingface`
- **Embeddings Provider**: Select `openai` or `huggingface`
- **Vector Store**: Configure `qdrant` or `chromadb`
- **RAG Mode**: Use `semantic` or `hybrid` search
- **Memory Settings**: Adjust conversation history limits

Local generated data, including the ChromaDB index and SQLite conversation
memory, is stored under `.nim-bit-code/` in the workspace directory where the
application is launched. Legacy `.memory/` and `.chromadb/` folders in that
workspace are moved into `.nim-bit-code/` automatically when there are no
conflicting files.

Example configuration:

```yaml
llm:
  provider: anthropic
  model: claude-haiku-4-5-20251001

embeddings:
  provider: openai
  model: text-embedding-3-small

vector_store:
  provider: qdrant
  retrieval_mode: hybrid
```

---

## 🚀 Quick Start

### 1. Run the Application

```bash
poetry run nim-bit-code
```

Or directly:

```bash
python main.py
```

### 2. Start Using Commands

Once the REPL starts, you'll see:

```
nim-bit-code — RAG-powered code assistant
✓ Ready

>
```

---

## 📖 Command Reference

### Ask About Your Code
```
/ask <question>
```
Query your codebase using natural language.

**Examples:**
```
> /ask What does the handle_query function do?
> /ask How is the session management implemented?
> /ask Show me all database connection functions
```

### Session Management

**Create a New Session**
```
/new_session
```
Start a fresh conversation with a new session ID.

**Switch to Previous Session**
```
/switch <session_id>
```
Resume a previous conversation.

**View Current Session**
```
/session
```
Display the current session ID.

### Index Management

**Show Index Contents**
```
/show_index
```
Display all indexed code chunks and metadata.

**Show Semantic Index**
```
/show_semantic_index
```
Display the semantic search index structure.

### Exit

```
/exit
or
/quit
```
Exit the application gracefully.

---

## 📁 Project Structure

```
nim-bit-code/
├── agent/              # Orchestration layer for handling queries
├── context/            # Code indexing and context management
│   └── indexers/       # Different indexing strategies
├── llm/                # LLM integration modules
├── memory/             # Session and conversation memory
├── observability/      # Logging and monitoring
├── tools/              # Utility functions and helpers
├── tests/              # Unit and integration tests
├── main.py             # Application entry point
├── config.py           # Configuration loader
├── config.yaml         # Configuration settings
├── pyproject.toml      # Poetry configuration
└── README.md           # This file
```

---

## ⚙️ Configuration

### LLM Providers

#### OpenAI
```yaml
llm:
  provider: openai
  model: gpt-4  # or gpt-3.5-turbo
```

#### Anthropic
```yaml
llm:
  provider: anthropic
  model: claude-haiku-4-5-20251001  # or other Claude models
```

#### HuggingFace
```yaml
llm:
  provider: huggingface
  model: meta-llama/Llama-2-7b
```

### Embedding Models

#### OpenAI Embeddings
```yaml
embeddings:
  provider: openai
  model: text-embedding-3-small  # or text-embedding-3-large
```

#### HuggingFace Embeddings
```yaml
embeddings:
  provider: huggingface
  model: sentence-transformers/all-MiniLM-L6-v2
```

### Vector Stores

#### Qdrant (Recommended)
```yaml
vector_store:
  provider: qdrant
  retrieval_mode: hybrid  # dense, sparse, or hybrid
```

#### ChromaDB
```yaml
chroma_db:
  persist_dir: .chromadb/
  collection_name: codebase
```

---

## 🔍 How It Works

1. **Code Indexing**: nim-bit-code scans your repository and indexes all code files
2. **Embedding Generation**: Code chunks are converted into embeddings using configured provider
3. **Vector Store**: Embeddings are stored in Qdrant or ChromaDB for efficient retrieval
4. **Query Processing**: User questions are converted to embeddings
5. **Retrieval**: Hybrid search retrieves relevant code chunks
6. **Response Generation**: LLM generates context-aware answers using retrieved code
7. **Session Persistence**: Conversation history is saved for continuity

---

## 🧪 Testing

Run the test suite:

```bash
poetry run pytest
```

Run specific tests:

```bash
poetry run pytest tests/test_agent.py -v
```

---

## 📚 Dependencies

Key dependencies used in this project:

| Package | Purpose |
|---------|---------|
| `langchain` | LLM orchestration framework |
| `chromadb` | Vector database for embeddings |
| `langchain-qdrant` | Qdrant integration for LangChain |
| `tree-sitter` | Code parsing and AST extraction |
| `pydantic` | Data validation |
| `rich` | Beautiful terminal output |
| `python-dotenv` | Environment variable management |

For complete dependencies, see `pyproject.toml`

---

## 💡 Use Cases

- 📖 **Code Documentation**: Ask questions about your codebase structure
- 🐛 **Debugging**: Find relevant code sections for bug fixes
- 🔄 **Code Review**: Understand implementation patterns and dependencies
- 🧠 **Onboarding**: New developers can quickly understand the codebase
- 🏗️ **Architecture Understanding**: Learn how different modules interact

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📝 License

This project is open source and available under the MIT License.

---

## 🆘 Troubleshooting

### Issue: Index not found
**Solution**: Make sure you run the application from the correct repository directory.

### Issue: API key errors
**Solution**: Verify all required environment variables are set in `.env` file.

### Issue: Memory errors with large codebases
**Solution**: Adjust `summarize_at_tokens` in `config.yaml` to process conversations in smaller chunks.

### Issue: Slow retrieval
**Solution**: Try `dense` mode instead of `hybrid` mode in vector_store configuration.

---

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions

---

## 🎯 Roadmap

- [ ] Web UI interface
- [ ] Support for more programming languages
- [ ] Real-time code analysis
- [ ] Code metrics and analytics
- [ ] Integration with IDE plugins
- [ ] GraphQL API
- [ ] Batch processing capabilities

---

## 🙏 Acknowledgments

Built with:
- [LangChain](https://langchain.com) - LLM framework
- [Qdrant](https://qdrant.tech) - Vector database
- [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) - Code parsing
- [Rich](https://rich.readthedocs.io/) - Terminal rendering

---

**Happy coding! 🎉**
