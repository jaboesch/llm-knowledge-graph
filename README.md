## Overview
The LLM Knowledge Graph tool can be used to extract key entities and relationships from long text documents. It creates detailed knowledge graphs from text, and the GraphReader agent facilitates RAG with high accuracy for complex queries.

**References & Further Reading:**
  
*[GraphReader](https://arxiv.org/abs/2406.14550): Building Graph-based Agent to Enhance Long-Context Abilities of Large Language Models* by Li et al.

*[Implementing GraphReader with Neo4j and LangGraph](https://towardsdatascience.com/implementing-graphreader-with-neo4j-and-langgraph-e4c73826a8b7)* by Tomaz Bratanic


## Usage

### Prerequisites
First, you will need to download the graph database server, [neo4j](https://neo4j.com/download/), and configure a local database instance. Tutorials can be found on their [website](https://neo4j.com/docs/getting-started/appendix/tutorials/guide-cypher-basics/).

Second, you will need an OpenAI API key to run model inference. The system also currently uses HuggingFace serverless inference, which requires a HuggingFace API key.
  
### Activate Python environment and install dependencies

From the project directory, create and activate a virtual environment:  
`python3.12 -m venv venv`  
`source venv/bin/activate`

Install project dependencies:  
`pip install -r requirements.txt`

### Set the configuration details

Create a `.env` file in the project root and add the following values:
```
HF_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
NEO4J_URI=your-uri
NEO4J_USERNAME=your-username
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=your-database
```

### Running the script
From the root of the project directory, the program will run with the following command:  
* `python src/main.py {command} {args}`  

**Reset:**  
If this is your first time using a new database instance, or if you would like to reset your database, run the following command. **This will erase all data in the database** and create useful graph constraints.
* `python src/main.py reset`
  
**Build:**  
Use the following command to build a graph based on a Wikipedia article of the provided subject. You can run this many times with various subjects to build a large, interconnected knowledge graph.
* `python src/main.py build "Harry Potter"`

**Read:**  
Use the following command to answer questions based on the data in your knowledge graph. The system uses agent reasoning and RAG to extract entities, facts, and text snippets, eventually forming a rational answer.
* `python src/main.py read "What school did the author of the Harry Potter books attend?"`

**Expand:**  
*Coming Soon.* Eventually, I plan to add an expand function which will use various factors and LLM reasoning to determine the most important nodes for further research. 

For example, if the original graph is trained on the *Harry Potter* Wikipedia article, the system may determine that certain nodes require more research, such as *J.K. Rowling*, *Daniel Radcliffe*, and *Harry Potter and the Philosopher's Stone (film)*.
* `python src/main.py expand 3`

