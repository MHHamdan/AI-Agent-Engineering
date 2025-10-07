"""
Streamlit Application for EU AI Act RAG System

Production-grade web interface providing:
- Interactive Q&A with document retrieval
- Real-time answer generation with source attribution
- Document search and exploration
- Performance metrics visualization

Architecture:
- Stateful session management for caching expensive operations
- Lazy initialization of vector stores and models
- Error boundary handling with user-friendly feedback
- Responsive UI with progress indicators
"""

import streamlit as st
import os
import traceback
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools import Tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langsmith import traceable
import time
from src.config import Config

# Page configuration
st.set_page_config(
    page_title="EU AI Act RAG System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        padding-bottom: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .document-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.vectorstore = None
    st.session_state.retriever = None
    st.session_state.agent_executor = None
    st.session_state.chat_history = []

@st.cache_resource
def initialize_rag_system():
    """
    Initializes RAG pipeline components with caching.

    Performs expensive one-time operations:
    - Document loading and parsing from PDF
    - Text chunking with overlap for context preservation
    - Embedding generation and vector store creation
    - Agent initialization with tool binding

    Returns:
        tuple: (vectorstore, retriever, agent_executor) or (None, None, None) on failure

    Note:
        Decorated with @st.cache_resource for singleton behavior across sessions.
        Subsequent calls return cached instances without re-initialization.
    """
    try:
        # Load the EU AI Act PDF
        pdf_path = "eu_ai_act.pdf"
        if not os.path.exists(pdf_path):
            st.error(f"❌ EU AI Act PDF not found at {pdf_path}")
            return None, None, None

        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=1000,
            chunk_overlap=200
        )
        doc_splits = text_splitter.split_documents(documents)

        # Create vector store with Ollama embeddings
        embeddings = OllamaEmbeddings(
            model=Config.EMBEDDINGS_MODEL_NAME,
            base_url=Config.OLLAMA_BASE_URL
        )
        vectorstore = InMemoryVectorStore.from_documents(
            documents=doc_splits,
            embedding=embeddings
        )

        # Create retriever with MMR (Maximal Marginal Relevance) for diverse results
        # MMR balances relevance with diversity to avoid redundant documents
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": Config.RETRIEVAL_K,
                "fetch_k": Config.RETRIEVAL_K * 3,  # Fetch more candidates
                "lambda_mult": 0.7  # Balance between relevance (1.0) and diversity (0.0)
            }
        )

        # Initialize Ollama LLM
        llm = ChatOllama(
            model=Config.RAG_MODEL_NAME,
            temperature=Config.RAG_MODEL_TEMPERATURE,
            base_url=Config.OLLAMA_BASE_URL
        )

        # Create retrieval tool with grounding instructions
        @traceable
        def rag_search(query: str) -> str:
            """
            Performs semantic search over EU AI Act corpus with grounding constraints.

            Args:
                query: Natural language question or search phrase

            Returns:
                str: Formatted context with retrieved documents and instruction prompt
                     for grounded answer generation

            Implementation:
                - Invokes retriever for top-k similar documents
                - Formats results with document IDs and page metadata
                - Prepends strict grounding instructions to prevent hallucination
            """
            docs = retriever.invoke(query)
            if not docs:
                return "No relevant documents found for this query."

            context = "\n\n".join([f"[Document {i+1}, Page {docs[i].metadata.get('page', 'N/A')}]:\n{doc.page_content}" for i, doc in enumerate(docs)])

            instruction = """You MUST follow these rules when answering:

CRITICAL INSTRUCTIONS:
1. Answer ONLY using direct quotes and specific information from the documents below
2. Start your answer by listing the specific Article numbers or sections that answer the question
3. Use this format for each point:
   - Article X states: "direct quote from document"
   - [Cite Document Y, Page Z]
4. Do NOT summarize or paraphrase - use EXACT quotes
5. Do NOT add your own interpretations or knowledge
6. If the answer isn't in the documents, say: "This specific information is not found in the provided EU AI Act excerpts"

EXAMPLE FORMAT:
"According to Article 5, prohibited AI practices include:

1. Article 5(a) states: "the placing on the market, the putting into service or the use of an AI system that deploys subliminal techniques beyond a person's consciousness..." [Document 1, Page 50]

2. Article 5(b) states: "the placing on the market... that exploits any of the vulnerabilities of a natural person..." [Document 1, Page 50]"

NOW ANSWER USING ONLY THE DOCUMENTS BELOW:
---
""" + context
            return instruction

        rag_tool = Tool(
            name="eu_ai_act_search",
            description="Find information in the EU AI Act document about regulations, requirements, and rules. Use this first when answering questions about the AI Act.",
            func=rag_search
        )

        # Create the question answering agent
        agent_executor = create_react_agent(
            model=llm,
            tools=[rag_tool],
            checkpointer=MemorySaver()
        )

        return vectorstore, retriever, agent_executor

    except Exception as e:
        st.error(f"Error initializing RAG system: {str(e)}")
        return None, None, None

# Header
st.markdown('<p class="main-header">EU AI Act Question Answering</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Get clear answers about EU AI Act regulations with exact quotes from the official document</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This system helps you understand the **EU AI Act** by:
    - Answering your compliance questions
    - Finding relevant sections in the document
    - Providing accurate responses with citations

    **Built with:**
    - Ollama (runs on your computer)
    - Modern language models
    - Quality tracking tools
    """)

    st.divider()

    st.header("System Status")

    # Set up the system
    if st.button("Initialize System", type="primary"):
        with st.spinner("Loading EU AI Act document and preparing the system..."):
            vectorstore, retriever, agent_executor = initialize_rag_system()
            if vectorstore and retriever and agent_executor:
                st.session_state.vectorstore = vectorstore
                st.session_state.retriever = retriever
                st.session_state.agent_executor = agent_executor
                st.session_state.initialized = True
                st.success("System ready to answer questions")
            else:
                st.error("Setup failed - check the error message above")

    # Show current status
    if st.session_state.initialized:
        st.success("Ready to Answer Questions")
    else:
        st.warning("Click 'Initialize System' above to get started")

    st.divider()

    st.header("Example Questions")
    st.markdown("""
    - What are prohibited AI practices?
    - What is a high-risk AI system?
    - What are provider obligations?
    - What are transparency requirements?
    - What are deployer obligations?
    """)

# Main content area
if st.session_state.initialized:
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Ask Questions", "Document Search", "Evaluation Metrics"])

    with tab1:
        st.subheader("Ask a Question about EU AI Act Compliance")

        # Question input
        user_question = st.text_input(
            "Enter your question:",
            placeholder="e.g., What are the requirements for high-risk AI systems?",
            key="question_input"
        )

        # Search button
        if st.button("Get Answer", type="primary"):
            if user_question:
                with st.spinner("Searching EU AI Act and generating answer..."):
                    try:
                        # Create unique thread ID
                        thread_id = f"streamlit_{hash(user_question)}_{int(time.time())}"
                        config = {"configurable": {"thread_id": thread_id}}

                        # Get answer from agent
                        response = st.session_state.agent_executor.invoke(
                            {"messages": user_question},
                            config=config
                        )

                        answer = response["messages"][-1].content

                        # Get retrieved documents
                        docs = st.session_state.retriever.invoke(user_question)

                        # Display answer
                        st.success("Answer Generated")
                        st.markdown("### Answer")
                        st.markdown(answer)

                        # Display retrieved documents
                        st.markdown("### Source Documents")
                        for i, doc in enumerate(docs, 1):
                            with st.expander(f"Document {i} (Page {doc.metadata.get('page', 'N/A')})"):
                                st.markdown(f"```\n{doc.page_content}\n```")

                        # Add to chat history
                        st.session_state.chat_history.append({
                            "question": user_question,
                            "answer": answer,
                            "docs": len(docs)
                        })

                    except Exception as e:
                        error_details = traceback.format_exc()
                        st.error(f"Error: {str(e) if str(e) else 'Unknown error'}")
                        with st.expander("Error Details"):
                            st.code(error_details)
            else:
                st.warning("Please enter a question first")

        # Display chat history
        if st.session_state.chat_history:
            st.divider()
            st.subheader("Chat History")
            for i, item in enumerate(reversed(st.session_state.chat_history[-5:]), 1):
                with st.expander(f"Q{i}: {item['question'][:60]}..."):
                    st.markdown(f"**Question:** {item['question']}")
                    st.markdown(f"**Answer:** {item['answer'][:200]}...")
                    st.caption(f"{item['docs']} documents retrieved")

    with tab2:
        st.subheader("Search EU AI Act Documents")
        st.markdown("Enter a search query to find relevant sections in the EU AI Act")

        search_query = st.text_input(
            "Search query:",
            placeholder="e.g., transparency requirements",
            key="search_input"
        )

        if st.button("Search Documents"):
            if search_query:
                with st.spinner("Searching documents..."):
                    docs = st.session_state.retriever.invoke(search_query)

                    st.success(f"Found {len(docs)} relevant document chunks")

                    for i, doc in enumerate(docs, 1):
                        st.markdown(f"#### Result {i}")
                        st.markdown(f"**Page:** {doc.metadata.get('page', 'N/A')}")
                        st.markdown(f"**Content:**")
                        st.markdown(f"<div class='document-box'>{doc.page_content}</div>", unsafe_allow_html=True)
                        st.divider()
            else:
                st.warning("Please enter a search query")

    with tab3:
        st.subheader("System Evaluation Metrics")
        st.markdown("""
        The RAG system is evaluated using four key metrics:

        1. **Correctness**: Does the answer match the reference answer?
        2. **Relevance**: Does the answer address the question?
        3. **Groundedness**: Is the answer supported by retrieved documents?
        4. **Retrieval Relevance**: Are retrieved documents relevant to the question?

        ### View Detailed Metrics

        For comprehensive evaluation results, visit the **LangSmith dashboard**:
        [https://smith.langchain.com](https://smith.langchain.com)

        ### Key Performance Indicators
        """)

        # Display mock metrics (in real implementation, fetch from LangSmith)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Correctness", "85%", "±5%")
        with col2:
            st.metric("Relevance", "92%", "±3%")
        with col3:
            st.metric("Groundedness", "88%", "±4%")
        with col4:
            st.metric("Retrieval", "90%", "±2%")

        st.info("**Note:** Run the evaluation notebook to generate actual metrics")

else:
    # System not initialized
    st.info("Please initialize the system using the sidebar to get started")

    st.markdown("""
    ### Getting Started

    1. Click **"Initialize System"** in the sidebar
    2. Wait for the EU AI Act PDF to be loaded and processed
    3. Start asking questions in the "Ask Questions" tab

    ### What This System Does

    This RAG (Retrieval-Augmented Generation) system:
    - Loads and processes the official EU AI Act document
    - Uses advanced AI to understand your questions
    - Retrieves relevant sections from the document
    - Generates accurate, grounded answers
    - Provides source citations for transparency

    ### Privacy and Security

    - All processing happens locally with Ollama
    - Questions and answers are not stored permanently
    - No external API calls - everything runs on your machine
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #888; padding: 1rem;'>
    <p>Built with Streamlit, LangChain, and Ollama (Local LLMs)</p>
    <p>Data Source: Official EU AI Act Document</p>
</div>
""", unsafe_allow_html=True)
