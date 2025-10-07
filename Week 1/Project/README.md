# Week 1 AI Agent Project - Project Management Assistant

## 🎯 Overview
This project implements an AI-powered Project Management Assistant using two different frameworks:
1. **LangGraph** with Ollama (local LLM)
2. **Google ADK** with Hugging Face (cloud LLM)

Both implementations are completely FREE to use!

## 🚀 Quick Start

### Prerequisites
1. **Python 3.8+** installed
2. **Ollama** installed (for local LLM)
3. **Jupyter Notebook** or JupyterLab

### Step 1: Install Ollama
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

### Step 2: Start Ollama and Download Models
```bash
# Start Ollama service
ollama serve

# In another terminal, pull the model
ollama pull llama3.2:latest
```

### Step 3: Get Hugging Face Token (Optional)
1. Go to https://huggingface.co/settings/tokens
2. Create a free account
3. Generate an access token
4. Add it to your `.env` file

### Step 4: Set Up Environment Variables
Create a `.env` file in the project directory:
```env
# For Hugging Face (optional)
HUGGINGFACE_API_TOKEN=your_token_here

# For Ollama (default settings)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
```

### Step 5: Run the Notebook
```bash
jupyter notebook "Solution - Week 01 HomeWork Template.ipynb"
```

## 📁 Project Structure
```
Week 1/Project/
├── Solution - Week 01 HomeWork Template.ipynb  # Main notebook with implementations
├── .env                                         # Environment variables (not in git)
├── .gitignore                                   # Git ignore file
└── README.md                                    # This file
```

## 🛠️ Features

### Project Management Tools
1. **Task Scheduler**: Schedule tasks with deadlines and priorities
2. **Team Allocator**: Assign team members to tasks based on skills

### AI Agent Capabilities
- Natural language understanding
- Tool selection and execution
- Context awareness
- Multi-step task handling
- Professional responses

## 🧠 Key Concepts Covered

### 1. AI Agent Architecture
- **ReAct Pattern**: Reasoning + Acting
- **Tool Integration**: Function-to-tool conversion
- **Memory Management**: Conversation history

### 2. Framework Implementation
- **LangGraph**: Simple, effective agent creation
- **Google ADK**: Advanced agent development kit

### 3. Model Options
- **Ollama**: Local, private, unlimited usage
- **Hugging Face**: Cloud-based, diverse models

### 4. Best Practices
- Environment variable management
- Secure API key handling
- Git security (.gitignore)

## 🔧 Available Models

### Ollama Models (Local)
- `llama3.2:latest` - Balanced performance (2GB)
- `mistral:latest` - Good for general tasks (4.4GB)
- `qwen:latest` - Smaller, faster model (2.3GB)

### Hugging Face Models (Cloud)
- `microsoft/phi-2` - Efficient small model
- Various other free models available

## 📝 Example Usage

### Task Scheduling
```
User: Schedule a task called 'Database Migration' for 2024-02-15 with High priority
Agent: ✅ Task 'Database Migration' successfully scheduled!
       📋 Task ID: TSK-4567
       📅 Deadline: 2024-02-15
       🔥 Priority: High
```

### Team Allocation
```
User: Allocate Sarah Johnson to task TSK-4567 with Python and SQL skills
Agent: ✅ Team member successfully allocated!
       👤 Member: Sarah Johnson
       📝 Task ID: TSK-4567
       💼 Skills: Python, SQL
```

## 🐛 Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### Missing Dependencies
```bash
# Install all required packages
pip install langgraph langchain langchain-ollama google-adk huggingface-hub python-dotenv
```

### API Key Issues
- Ensure `.env` file is in the correct directory
- Check that API tokens are valid
- Never commit `.env` to version control

## 📚 Learning Resources

### Concepts
- **AI Agents**: Autonomous programs that use LLMs to reason and act
- **ReAct Pattern**: Combines reasoning with action execution
- **Tool Calling**: Allows agents to execute specific functions

### Frameworks
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Google ADK Docs**: https://github.com/google/genai-agent-kit

## 🎓 Assignment Evaluation

### Completed Requirements ✅
- [x] Implemented both LangGraph and Google ADK options
- [x] Integrated project management tools
- [x] Created comprehensive agent instructions
- [x] Tested with all provided scenarios
- [x] Used free models (Ollama + Hugging Face)
- [x] Implemented secure API key management

### Bonus Features 🌟
- Environment variable management with .env
- Git security with .gitignore
- Support for multiple LLM providers
- Detailed error handling
- Comprehensive documentation

## 🚀 Next Steps

1. **Extend Tools**: Add more project management capabilities
2. **Build UI**: Create a web interface with Streamlit
3. **Add Database**: Store tasks and allocations persistently
4. **Deploy**: Host on Hugging Face Spaces or Railway
5. **Integrate**: Connect with real project management tools

## 📄 License
Educational project for AI Agent Engineering course.

---

**Happy Learning! 🎉**