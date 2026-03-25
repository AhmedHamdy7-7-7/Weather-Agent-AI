#  Weather Conversational Agent

##  Overview

This project implements a conversational AI agent capable of answering weather-related queries using tool calling and reasoning strategies.

The system uses the Groq API (OpenAI-compatible) and integrates external tools such as a weather API and a calculator.

---

## Setup Instructions

1. Clone the repository:

```
git clone https://github.com/YOUR_USERNAME/Weather-Agent-AI.git
cd Weather-Agent-AI
```

2. Create virtual environment:

```
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Create `.env` file using `.env.example`

5. Run:

```
python conversational_agent.py
```

---

## 🧠 Implementation

###  Part 1: Basic Tool Calling

* Implemented weather API integration
* Enabled function calling
* Built interactive conversational loop

---

###  Part 2: Chain of Thought

* Added reasoning capability
* Implemented calculator tool
* Enabled multi-step problem solving
* Supported multi-city comparisons

---

###  Part 3: Advanced Tool Orchestration

* Implemented safe tool execution
* Added parallel tool execution
* Built multi-step workflow loop
* Handled structured outputs

---

## Example Conversations

### Basic Agent

User: What is the weather in Cairo?
Assistant: The current weather in Cairo is partly cloudy with a temperature of 14.4°C.

---

### Chain of Thought Agent

User: What is 5 * (3 + 2)?
Assistant: 25

---

### Advanced Agent

User: What is the temperature difference between Cairo and London?
Assistant: Cairo: 14.4°C, London: 7.2°C → Difference = 7.2°C

---

## Analysis

* The basic agent retrieves weather data effectively.
* The Chain of Thought agent improves reasoning for multi-step queries.
* The advanced agent enhances robustness and handles failures gracefully.
* Parallel execution improves efficiency when handling multiple tool calls.

---

## Challenges & Solutions

### Challenge 1: Groq tool-calling inconsistencies

* The model sometimes returned malformed function calls.
* Solution: Implemented fallback logic and manual handling.

### Challenge 2: Multi-step reasoning

* The model struggled with comparing multiple cities.
* Solution: Added custom logic for handling multi-city queries.

### Challenge 3: Error handling

* Tool calls could fail unexpectedly.
* Solution: Implemented safe execution and fallback strategies.

---

## References

* OpenAI Function Calling Documentation
* OpenAI Structured Outputs Documentation
* WeatherAPI Documentation
