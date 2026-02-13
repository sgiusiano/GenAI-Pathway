# 🤖 Customer Service Agent with LangChain

An advanced customer service agent built with **LangChain Expression Language (LCEL)**, structured outputs with **Pydantic** and **LangSmith** for observability. This system provides intelligent query analysis, dynamic response generation, and structured conversation summaries.

## 🏗️ System Architecture

The system is built with a modular architecture that clearly separates responsibilities:

```
genai_pathway_mentoring/
├── src/                          # Main source code
│   ├── models/                   # Pydantic models for validation
│   │   ├── entities.py          # Extracted entities (products, orders, dates)
│   │   ├── query_analysis.py    # Query analysis and classification
│   │   └── conversation_summary.py # Structured conversation summaries
│   ├── components/               # System components
│   │   ├── query_analyzer.py    # Query analyzer with LLM
│   │   ├── response_generator.py # Contextual response generator
│   │   └── conversation_summarizer.py # Conversation summarizer
│   ├── prompts/                  # Specialized prompt templates
│   │   ├── analysis_prompts.py  # Prompts for query analysis
│   │   ├── response_prompts.py  # Category-specific prompts
│   │   └── summary_prompts.py   # Summary prompts
│   ├── chains/                   # LCEL chains
│   │   └── customer_service_chain.py # Main integrating chain
│   ├── config/                   # Configuration and settings
│   │   ├── llm_config.py        # Language model configuration
│   │   └── settings.py          # Environment variables and configuration
│   └── utils/                    # Utility functions
│       ├── helpers.py            # Helper functions
│       └── validators.py         # Input/output validators
├── tests/                        # Unit tests
├── notebooks/                    # Jupyter notebooks with examples
├── interactive_chat_demo.py      # Interactive chat demo
└── requirements.txt              # Project dependencies
```

## 🚀 Installation and Configuration

### 1. Clone the repository
```bash
git clone https://gitlab.kdsoft.io/pluralit-ai-solutions/genai-pathway/cohort-01/project-01-customer-service-agent
cd project-01-customer-service-agent
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp env.example .env
# Edit .env with your API keys
```

## ⚙️ System Configuration

### Required Environment Variables

```bash
# OpenAI (Required)
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1
OPENAI_TEMPERATURE=0.7

# LangSmith (Optional, for observability)
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=your_project_name
LANGSMITH_TRACING=true

# Application Configuration
APP_NAME=Customer Service Agent
APP_VERSION=1.0.0
DEBUG=false

# Company Information
COMPANY_NAME=TechStore Plus
COMPANY_LOCATION=New York, USA

# Return Policy Configuration
RETURN_WINDOW_DAYS=30
REFUND_PROCESSING_DAYS=5
```

## 🎯 Quick Start

### Option 1: Interactive Demo (Recommended for beginners)

```bash
python interactive_chat_demo.py
```

This demo allows you to:
- Chat interactively with the agent
- See real-time analysis of your queries
- Observe contextual response generation
- Review structured conversation summaries

### Option 2: Programmatic Usage

```python
from src.chains import CustomerServiceChain

# Initialize the agent
agent = CustomerServiceChain()

# Process a query
query = "I need help with my order #TEC-2024001"
result = agent.process_query(query)

# Display results
print(f"Response: {result['response']}")
print(f"Category: {result['metadata']['category']}")
print(f"Urgency: {result['metadata']['urgency']}")
print(f"Sentiment: {result['metadata']['sentiment']}")
```

### Option 3: Jupyter Notebook

```bash
jupyter notebook notebooks/customer_service_agent.ipynb
```

The notebook includes:
- Step-by-step implementation of each component
- Usage examples with different query types
- Detailed analysis of LCEL architecture
- System testing and validation

## 🔧 Main Components

### 1. QueryAnalyzer 🔍
- **Automatic classification** of queries by category
- **Urgency level detection** (low, medium, high)
- **Customer sentiment analysis** (positive, neutral, negative)
- **Entity extraction** (products, order numbers, dates)
- **Input validation and sanitization**

### 2. ResponseGenerator 💬
- **Contextual generation** of responses based on analysis
- **Intelligent routing** to category-specific prompts
- **Personalization** of responses based on sentiment and urgency
- **Specialized prompts** for each query type
- **Error handling** and fallback responses

### 3. ConversationSummarizer 📋
- **Structured summaries** of all interactions
- **Conversation statistics** (categories, sentiments, urgencies)
- **Data export** in multiple formats
- **Resolution status tracking** for queries
- **Follow-up identification** requirements

## 📊 Supported Query Categories

The system automatically classifies queries into the following categories:

| Category | Description | Examples |
|----------|-------------|----------|
| **technical_support** | Technical support | "My router isn't working", "Installation problem" |
| **billing** | Billing and payments | "Error in my invoice", "Problem with the charge" |
| **returns** | Returns and warranties | "I want to return my product", "Warranty issue" |
| **product_inquiry** | Product inquiries | "Do you have this model?", "Product specifications" |
| **general_information** | General information | "Business hours", "Company policies" |

## 🎨 Specialized Prompts

Each category has optimized prompts:

- **Technical Support**: Empathetic and solution-focused
- **Billing**: Professional and precise with financial information
- **Returns**: Understanding and clear about policies
- **Product Inquiry**: Enthusiastic and informative about products
- **General**: Friendly and comprehensive for general queries

## 🧪 Testing and Validation

### Running Tests
```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_models.py

# With code coverage
pytest --cov=src
```

### Implemented Validations
- **Pydantic Models**: Type and data structure validation
- **User Input**: Query sanitization and validation
- **System Output**: Response and metadata validation
- **Configuration**: Required environment variable validation

## 🔍 Advanced Features

### LCEL (LangChain Expression Language)
- **Optimized chains** for maximum performance
- **Functional composition** of components
- **Robust error handling** at each step
- **Complete execution** traceability

### Data Structure with Pydantic
- **Automatic validation** of input and output
- **Typed models** for all data structures
- **Automatic serialization/deserialization**
- **Integrated schema** documentation

### Observability with LangSmith
- **Execution tracing** of LCEL chains
- **Real-time performance** metrics
- **Advanced debugging** of prompts and responses
- **Response quality** analysis

## 🚧 Limitations and Considerations

### Current Limitations
- **OpenAI Dependency**: Requires valid API key
- **Language**: Optimized for English
- **Context**: Limited conversation memory
- **Scalability**: Designed for moderate usage

### Production Considerations
- **Rate Limiting**: Implement API limits
- **Caching**: Add cache for common responses
- **Logging**: Implement structured logging
- **Monitoring**: Add system health metrics

## 📋 Changelog

### Version 1.0.0 - Initial Release

**Core Features:**
- 🎯 **Query Analysis**: Automatic classification and entity extraction
- 💬 **Smart Responses**: Contextual responses based on query type and sentiment
- 📊 **Conversation Logs**: Structured summaries of all interactions
- 🏗️ **Modular Design**: LCEL architecture with reusable components
- 🔍 **Auto-Categorization**: Support for 5 query types (support, billing, returns, products, general)
- 📈 **Sentiment & Urgency**: Automatic detection of customer mood and priority
- ✅ **Data Validation**: Pydantic models for robust input/output handling

**Technical Stack:**
- LangChain Expression Language (LCEL) for optimal performance
- Pydantic for data validation and structure
- LangSmith for observability and debugging
- Comprehensive testing with pytest
- Interactive demo and Jupyter examples

---

## 🧠 Memory-Enabled Customer Service Agent

This project now includes an advanced memory-aware customer service agent that maintains conversation context across interactions and integrates with customer service tools.

### MemoryAgent Architecture

The `MemoryAgent` class (`src/agent/memory_agent.py`) is the core component that orchestrates memory-aware customer service interactions:

**Key Features:**
- **Session Management**: Maintains separate conversation contexts for different customers using email-based sessions
- **Tool Integration**: Incorporates customer service tools for real-time data retrieval (customer info, orders, tickets, shipping)
- **Memory-Aware Responses**: Uses conversation history to provide contextual, personalized responses
- **ReAct Architecture**: Implements ReAct (Reasoning + Acting) pattern for tool usage and decision making

**Core Methods:**
- `process_query(customer_email, user_query)`: Main entry point for processing customer queries with memory context
- `get_customer_conversation_history(customer_email)`: Retrieves formatted conversation history
- `clear_customer_session(customer_email)`: Clears session data for privacy/testing
- `get_active_sessions()`: Lists all active customer sessions

### HybridMemory System

The `HybridMemory` class (`src/memory/hybrid_memory.py`) implements sophisticated conversation memory management:

**Architecture:**
- **Buffer Memory**: Keeps recent messages (configurable buffer size, default: 5 messages)
- **Summary Memory**: Automatically summarizes older conversations using LLM when buffer overflows
- **Customer Context**: Extracts and maintains customer-specific metadata from conversations

**Key Methods:**
- `manage_conversation_buffer(message)`: Adds messages and manages buffer overflow with automatic summarization
- `memoryRetrieval()`: Formats complete memory context for LLM consumption
- `_generate_summary()`: Uses LangChain LCEL to create conversation summaries
- `_extract_customer_context(message)`: Extracts relevant customer information from metadata

**Memory Structure:**
```
Memory Context:
├── Previous Conversation Summary (if exists)
├── Current Conversation Buffer (recent messages)
└── Customer Context (extracted metadata)
```

### Customer Service Tools

The `customerTools` class (`src/tools/customer_tools.py`) provides LangChain tools for accessing customer data:

**Available Tools:**
- `get_customer_info(email)`: Retrieves customer profile and account details
- `get_order_status(order_id)`: Gets current order status and basic information
- `get_shipping_tracking(order_id)`: Provides detailed shipping and tracking information
- `get_customer_tickets(email)`: Fetches all support tickets for a customer

**Integration:**
- All tools are automatically available to the MemoryAgent's ReAct executor
- Tools use the MockDB for data retrieval in development/testing
- Structured responses optimized for LLM consumption

### Mock Database System

The `MockCustomerDB` class (`src/database/mock_db.py`) simulates a customer service database:

**Database Schema:**
- **Customers**: ID, email, name, category, status, registration date
- **Orders**: ID, order number, customer ID, products, status, tracking number, total amount
- **Support Tickets**: ID, ticket number, customer ID, category, priority, status, description

**Sample Data:**
- 5 sample customers with different categories (standard, premium, VIP)
- 4 sample orders with various statuses (pending, shipped, delivered, in_transit)
- 4 sample support tickets with different priorities and categories

**Features:**
- SQLite in-memory database for fast testing
- Realistic data relationships between customers, orders, and tickets
- Formatted string responses optimized for agent consumption

## 🚀 Testing the Memory Agent

### Running the Memory Agent Demo

To test the complete memory-enabled customer service agent, run the interactive demo:

```bash
python demo_memory_agent.py
```

**Prerequisites:**
1. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Demo Scenarios

The `demo_memory_agent.py` script demonstrates:

1. **Customer Recognition**: Agent recognizes returning customers by email
2. **Memory Continuity**: References previous conversations naturally
3. **Tool Usage**: Automatically uses appropriate tools based on queries
4. **Session Management**: Maintains separate contexts for different customers
5. **Context Awareness**: Provides personalized responses based on customer history

**Example Interactions:**
- Initial customer greeting → Agent uses `get_customer_info` tool
- Follow-up questions → Agent references previous conversation context
- Order inquiries → Agent uses `get_order_status` and `get_shipping_tracking` tools
- Support issues → Agent checks customer tickets and order history

### Testing Features

The demo showcases:
- **Multi-customer sessions**: Different customers with isolated memory contexts
- **Memory persistence**: Conversations remembered across interactions
- **Tool integration**: Real-time data retrieval from mock database
- **Context switching**: Agent adapts responses based on customer history
- **Session management**: View active sessions, conversation history, and clear sessions

### Expected Output

The demo will show:
1. Agent initialization confirmation
2. Customer interactions with tool usage traces
3. Memory-aware responses that reference previous conversations
4. Active session management
5. Conversation history retrieval
6. Session clearing functionality