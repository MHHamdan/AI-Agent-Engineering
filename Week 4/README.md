# EU AI Act Question Answering System

A smart system that helps you understand the EU AI Act by answering your compliance questions. Built with local language models and modern tools for accuracy and transparency.

## Table of Contents

- [What This Does](#what-this-does)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [How to Use](#how-to-use)
- [How We Ensure Quality](#how-we-ensure-quality)
- [Development](#development)
- [Contributing](#contributing)

---

## What This Does

This system helps you understand the EU AI Act by:
- Answering your questions about AI regulations
- Finding relevant sections in the official EU AI Act document
- Providing accurate answers based only on the actual text
- Showing you exactly where the information comes from

### Why Use This System?

**Accurate Answers**: We only use information from the official EU AI Act document

**Local Processing**: Everything runs on your computer using Ollama - no data sent to external services

**Transparent**: You can see exactly which parts of the document were used to answer your question

**Easy to Use**: Simple web interface - just type your question and get an answer

**Verifiable**: Every answer includes references to specific document sections

---

## Key Features

### What You Can Do
- Ask questions about EU AI Act in plain English
- Get answers with direct quotes from the regulation
- See which pages and articles support each answer
- Search through the document for specific topics
- Track system performance with built-in metrics

### How It Works
- Document Reading: Loads and understands the EU AI Act PDF
- Smart Search: Finds the most relevant sections for your question
- Answer Generation: Creates clear answers using only document content
- Quality Checks: Verifies answers are accurate and well-supported

### Built For Quality
- Automated Testing: Ensures everything works correctly
- Type Checking: Catches errors before they happen
- Clean Code: Easy to read and maintain
- Good Documentation: Clear explanations throughout
- Error Handling: Gracefully manages issues

---

## Project Structure

```
Week 4/
│
├── src/                          Main code
│   ├── config.py                 Settings and configuration
│   └── utils/                    Helper tools
│
├── tests/                        Automated tests
├── streamlit_app.py              Web interface
├── requirements.txt              Required packages
├── requirements-dev.txt          Development tools
└── README.md                     This file
```

---

## Getting Started

### What You Need
- Python 3.11 or newer
- Ollama installed on your computer
- Git (to download the project)

### Installation Steps

**1. Get the Code**
```bash
cd "AI-Agent-Engineering/Week 4"
```

**2. Set Up Python Environment**
```bash
# Create a clean environment for this project
python -m venv .venv
source .venv/bin/activate  # On Mac/Linux
# Or on Windows: .venv\Scripts\activate
```

**3. Install Required Packages**
```bash
# Main packages needed to run the system
pip install -r requirements.txt

# Additional packages for development
pip install -r requirements-dev.txt
```

**4. Install Ollama Models**
```bash
# Download the language model (takes ~9GB)
ollama pull qwen2.5:14b

# Download the embeddings model (takes ~670MB)
ollama pull mxbai-embed-large
```

**5. Verify Everything Works**
```bash
# Check that Ollama is running
ollama list

# Make sure you see qwen2.5:14b and mxbai-embed-large in the list
```

---

## How to Use

### Web Interface

```bash
# Start the web interface
streamlit run streamlit_app.py --server.port 8888
```

Then open your browser to `http://localhost:8888`

### Using the Interface

1. Click "Initialize System" in the sidebar
2. Wait for the EU AI Act document to load
3. Type your question in the text box
4. Click "Get Answer"
5. Read the answer with source citations

### Example Questions

- What are prohibited AI practices?
- What defines a high-risk AI system?
- What are provider obligations under the Act?
- What transparency requirements apply to AI systems?
- What obligations do deployers have?

---

## How We Ensure Quality

### Four-Way Quality Check

Our system checks every answer in four ways:

**1. Correctness**
- Does the answer match what the regulation actually says?
- Compares with known correct answers
- Uses another model to judge accuracy

**2. Relevance**
- Does the answer actually address the question?
- Prevents off-topic responses
- Ensures you get what you asked for

**3. Groundedness**
- Is the answer supported by the document?
- Prevents made-up information
- Every claim must have a source

**4. Retrieval Quality**
- Did we find the right document sections?
- Checks if search is working well
- Ensures relevant information is found

---

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Check code style
black --check src/ tests/

# Check for type errors
mypy src/

# Check for security issues
bandit -r src/
```

### Project Configuration

All settings are in `src/config.py`:
- Which models to use
- How many document chunks to retrieve
- Chunk sizes and overlap
- Ollama server location

### Customizing Models

Edit `src/config.py` to change models:

```python
# Use different language model
RAG_MODEL_NAME: str = "llama3.1:8b"  # Smaller, faster
# or
RAG_MODEL_NAME: str = "qwen2.5:14b"  # Better quality (default)

# Use different embedding model
EMBEDDINGS_MODEL_NAME: str = "nomic-embed-text"  # Smaller
# or
EMBEDDINGS_MODEL_NAME: str = "mxbai-embed-large"  # Better (default)
```

---

## Contributing

We welcome improvements. Here's how:

1. Fork this repository
2. Create a new branch for your changes
3. Make your improvements
4. Test everything works
5. Submit a pull request

Please ensure:
- Code is well-commented
- Tests pass
- Documentation is updated
- Style is consistent with existing code

---

## Troubleshooting

### Common Issues

**Ollama not found**
- Make sure Ollama is installed and running
- Check with: `ollama list`

**Model not found**
- Pull required models: `ollama pull qwen2.5:14b`
- Pull embeddings: `ollama pull mxbai-embed-large`

**PDF not found**
- Make sure `eu_ai_act.pdf` is in the project root
- Download from official EU sources if missing

**Slow performance**
- Smaller models run faster: try `llama3.1:8b`
- Reduce `RETRIEVAL_K` in config for fewer documents

---

## Technical Details

### How Document Processing Works

1. Load the PDF file
2. Split into overlapping chunks (2000 characters each)
3. Convert chunks into numerical representations
4. Store in searchable format
5. When you ask a question, find most similar chunks
6. Use those chunks to generate an answer

### Models Used

**Language Model** (qwen2.5:14b)
- Generates answers to questions
- Follows instructions precisely
- Excellent at quoting exact text
- Runs entirely on your computer

**Embedding Model** (mxbai-embed-large)
- Converts text into searchable format
- Finds similar content quickly
- Optimized for legal documents
- Also runs locally

---

## Privacy and Security

### Your Data Stays Local

- All processing happens on your computer
- No questions sent to external servers
- No API keys needed for core functionality
- Document never leaves your machine

### What Gets Stored

- Document chunks in memory (cleared on restart)
- Your questions during the session (not saved permanently)
- System logs for debugging (optional)

---

## Acknowledgments

- European Union for the AI Act document
- Ollama team for local model hosting
- LangChain for the document processing framework
- Streamlit for the web interface
- The open source community

---

## Support

Need help?
- Check this README first
- Look at example questions in the interface
- Review configuration in `src/config.py`
- Open an issue on GitHub if stuck

---

Built to help people understand AI regulations through clear, accurate, and verifiable answers.
