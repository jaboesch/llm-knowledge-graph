EXTRACTION_PROMPT = """You are now an intelligent assistant tasked with meticulously extracting both key elements and atomic facts from a long text. 

1. Key Elements: The essential nouns (e.g., characters, times, events, places, numbers) that exist within the text.  
2. Atomic Facts: The smallest, indivisible facts, presented as concise sentences. These include propositions, theories, existences, concepts, and implicit elements like logic, causality, descriptions, event sequences, interpersonal relationships, timelines, etc.  

---

### **Requirements:**

1. Key elements must have consistent and full names for maximum graph connectivity and future query enhancement. (e.g. change delicious smoothies to smoothies; change Harry to Harry Potter).
2. Ensure that all identified key elements are reflected within the corresponding atomic facts.  
3. You should extract key elements and atomic facts comprehensively, especially those that are important and potentially query-worthy and **do not leave out details**.  
4. Whenever applicable, replace pronouns with their specific noun counterparts (e.g., change I, He, She to actual names).
5. Keep atomic facts concise and clear; avoid excessive verbosity.
6. Your output should not exceed 4000 tokens.
7. Answer only in the described XML format.

---

### **Response Format:**

Respond only in the following XML format.

<Facts>
  <AtomicFact fact="$AtomicFact1">
    <KeyElement element="$KeyElement1" />
    <KeyElement element="$KeyElement2" />
  </AtomicFact>
  <AtomicFact fact="$AtomicFact2">
    <KeyElement element="$KeyElement1" />
    <KeyElement element="$KeyElement2" />
    <KeyElement element="$KeyElement3" />
  </AtomicFact>
</Facts>

---

### **Example:**

User:
Alice Redfield and her friend Bob Green (AKA Big Bobby) enjoy drinking delicious smoothies from Charley's cousin's shop. Charley's cousin, David, owns a popular smoothie shop called EasyDrink.

Assistant:
<Facts>
  <AtomicFact fact="Alice Redfield enjoys drinking delicious smoothies from EasyDrink.">
    <KeyElement element="alice redfield" />
    <KeyElement element="smoothies" />
    <KeyElement element="easydrink" />
  </AtomicFact>
  <AtomicFact fact="Bob Green enjoys drinking delicious smoothies from EasyDrink.">
    <KeyElement element="bob green" />
    <KeyElement element="smoothies" />
    <KeyElement element="easydrink" />
  </AtomicFact>
  <AtomicFact fact="Charley and David are cousins.">
    <KeyElement element="charley" />
    <KeyElement element="david" />
    <KeyElement element="cousins" />
  </AtomicFact>
  <AtomicFact fact="David owns EasyDrink.">
    <KeyElement element="david" />
    <KeyElement element="easydrink" />
  </AtomicFact>
  <AtomicFact fact="EasyDrink is a popular smoothie shop.">
    <KeyElement element="smoothie shop" />
    <KeyElement element="easydrink" />
  </AtomicFact>
  <AtomicFact fact="EasyDrink makes delicious smoothies.">
    <KeyElement element="smoothies" />
    <KeyElement element="easydrink" />
  </AtomicFact>
  <AtomicFact fact="Bob Green is also known as Big Bobby.">
    <KeyElement element="bob green" />
    <KeyElement element="big bobby" />
  </AtomicFact>
</Facts>

---

### **Step-by-Step Process:**

1. **Extract Key Elements:**
   - Exhaustively identify all Key Elements in the input text.  
   - Use the most consistent and full names possible for maximum graph connectivity.

2. **Extract Explicit Atomic Facts:**
   - For each Key Element:
     - Exhaustively evaluate **all facts, descriptions, and relationships to all other Key Elements** that are explicitly defined in the text.  
     - Describe these facts, descriptions, and relationships between Key Elements as clear, concise, and descriptive Atomic Facts.  
   - Each Key Element should connect to **multiple other elements** where relevant to maximize graph connectivity.  

2. **Extract Implicit Atomic Facts:**
   - Look over the text again and infer any additional facts, descriptions, or relationships between Key Elements that are not explicitly stated but are highly likely to be true.
   - No inferred fact is to small or insignificant to be included, be thorough in your extraction.
   - Do not invent facts, make sure you are highly confident in the accuracy of the inferences.

3. **Review and Refine:**
   - Re-check the text, Key Elements, and Atomic Facts:
     - Did you capture every Key Element? Are the Key Element names appropriately consistent for maximum connectivity and query-ability?  
     - Did you capture all explicit Atomic Facts? Are they clear, concise, and descriptive?
     - Did you capture all implicit Atomic Facts? Are you highly confident of the accuracy of these facts?
   - Refine your extraction based on these guidelines.

4. **Output the Graph in XML Format:**
   - Respond strictly in XML format with properly closed tags.
   - Do not provide any additional commentary.
   
---

Long documents may be split into chunks, so expect some truncation. Let's begin.
"""

RATIONAL_PLAN_PROMPT = """As an intelligent assistant, your primary objective is to answer the question by gathering supporting facts from a given article. To facilitate this objective, the first step is to make a rational plan based on the question. This plan should outline the step-by-step process to resolve the question and specify the key information required to formulate a comprehensive answer.

---

### **Example:**
User: Who had a longer tennis career, Danny or Alice?
Assistant: In order to answer this question, we first need to find the length of Danny’s and Alice’s tennis careers, such as the start and retirement of their careers, and then compare the two.

---

Please strictly follow the above format. Let’s begin."""

SHARED_READER_AGENT_INTRODUCTION_PROMPT = """As an intelligent assistant, your primary objective is to answer questions based on information contained within a text. To facilitate this objective, a graph has been created from the text, comprising the following elements:

1. Text Chunks: Chunks of the original text.
2. Atomic Facts: Smallest, indivisible truths extracted from text chunks.
3. Nodes: Key elements in the text that correlate with several atomic facts derived from different text chunks.""" 

INITIAL_NODE_ARG_KEY_ELEMENT = "Key element or name of a relevant node from the provided list."
INITIAL_NODE_ARG_SCORE = "Relevance to the potential answer by assigning a score between 0 and 100. A score of 100 implies a high likelihood of relevance to the answer, whereas a score of 0 suggests minimal relevance."
INITIAL_NODE_PROMPT = f"""{SHARED_READER_AGENT_INTRODUCTION_PROMPT}

---

### **Task:**

Your current task is to check a list of nodes, with the objective of selecting the most relevant initial nodes from the graph to efficiently answer the question. You are given the question, the rational plan, and a list of node key elements. These initial nodes are crucial because they are the starting point for searching for relevant information.

---

### **Requirements:**

1. Once you have selected a starting node, assess its relevance to the potential answer by assigning a score between 0 and 100. 
   - A score of 100 implies a high likelihood of relevance to the answer, whereas a score of 0 suggests minimal relevance.
2. Please select at least 10 starting nodes from the provided list of nodes, ensuring they are non-repetitive and diverse.
3. The key_element property of the nodes you select **must correspond exactly** to the nodes given by the user, with identical wording.
   - **Never fabricate, invent, or adjust** the wording of selected nodes.

---

### **Response Criteria:**

Your response should include a list of at least 10 starting nodes. Each node should include the following information:
- key_element: {INITIAL_NODE_ARG_KEY_ELEMENT}
- score: {INITIAL_NODE_ARG_SCORE}

---

Please strictly follow the defined response format. Let’s begin."""


ATOMIC_FACT_CHECK_ARG_UPDATED_NOTEBOOK = "Updated notebook including new insights and findings about the question."
ATOMIC_FACT_CHECK_ARG_RATIONAL_NEXT_ACTION = "Analysis on which action to take based on the given question, the rational plan, previous actions, and notebook content."
ATOMIC_FACT_CHECK_ARG_CHOSEN_ACTION = """Select one of the following actions:
1. read_chunk(List[ID]): Choose this action if you believe that a text chunk linked to an atomic fact may hold the necessary information to answer the question. This will allow you to access more complete and detailed information.
2. stop_and_read_neighbor(): Choose this action if you ascertain that all text chunks lack valuable information.
"""
ATOMIC_FACT_CHECK_PROMPT = f"""{SHARED_READER_AGENT_INTRODUCTION_PROMPT}

---

### **Task:**

Your current task is to check a node and its associated atomic facts, with the objective of determining whether to proceed with reviewing the text chunk corresponding to these atomic facts. 

---

### **Requirements:**

1. Update your current notebook with new insights and findings about the question from current atomic facts, creating a more complete version of the notebook that contains more valid information.
2. Based on all available context, analyze how to choose the next action.
3. Reflect on previous actions and prevent redundant revisiting nodes or chunks.
4. If necessary, select multiple text chunks to read at the same time.
5. Always choose to read a connected text chunk if you feel the atomic fact is even slightly related to the question. 
   - Atomic facts only cover part of the information in the text chunk.
6. Only choose stop_and_read_neighbor() when you are very sure that the given text chunk is irrelevant to the question.

---

### **Response Criteria:**

Given the question, the rational plan, previous actions, notebook content, and the current node’s atomic facts and their corresponding chunk IDs, formulate a response that includes the following:
- updated_notebook: {ATOMIC_FACT_CHECK_ARG_UPDATED_NOTEBOOK}
- rational_next_action: {ATOMIC_FACT_CHECK_ARG_RATIONAL_NEXT_ACTION}
- chosen_action: {ATOMIC_FACT_CHECK_ARG_CHOSEN_ACTION}

---

Please strictly follow the above format. Let’s begin.
"""
    

CHUNK_READ_ARG_UPDATED_NOTEBOOK = "Updated notebook including new insights and findings about the question."
CHUNK_READ_ARG_RATIONAL_NEXT_ACTION = "Analysis on which action to take based on the given question, the rational plan, previous actions, and notebook content."
CHUNK_READ_ARG_CHOSEN_ACTION = """Select one of the following actions:
1. search_more(): Choose this action if you think that the essential information necessary to answer the question is still lacking.
2. read_previous_chunk(): Choose this action if you feel that the previous text chunk contains valuable information for answering the question.
3. read_subsequent_chunk(): Choose this action if you feel that the subsequent text chunk contains valuable information for answering the question.
4. termination(): Choose this action if you believe that the information you have currently obtained is enough to answer the question. This will allow you to summarize the gathered information and provide a final answer.
"""
CHUNK_READ_PROMPT = f"""{SHARED_READER_AGENT_INTRODUCTION_PROMPT}

---

### **Task:**

Your current task is to assess a specific text chunk and determine whether the available information suffices to answer the question.

---

### **Requirements:**

1. Reflect on previous actions and prevent redundant revisiting of nodes or chunks.
2. You can only choose one action.

---

### **Response Criteria:**

Given the question, the rational plan, previous actions, notebook content, and the current node’s atomic facts and their corresponding chunk IDs, formulate a response that includes the following:
- updated_notebook: {CHUNK_READ_ARG_UPDATED_NOTEBOOK}
- rational_next_action: {CHUNK_READ_ARG_RATIONAL_NEXT_ACTION}
- chosen_action: {CHUNK_READ_ARG_CHOSEN_ACTION}

---

Please strictly follow the above format. Let’s begin.
"""


NEIGHBOR_SELECT_ARG_RATIONAL_NEXT_ACTION = "Analysis on which action to take based on the given question, the rational plan, previous actions, and notebook content."
NEIGHBOR_SELECT_ARG_CHOSEN_ACTION = """Select one of the following actions:
1. read_neighbor_node(key element of node): Choose this action if you believe that any of the neighboring nodes may contain information relevant to the question. Note that you should focus on one neighbor node at a time.
2. termination(): Choose this action if you believe that none of the neighboring nodes possess information that could answer the question.
"""
NEIGHBOR_SELECT_PROMPT = f"""{SHARED_READER_AGENT_INTRODUCTION_PROMPT}

---

### **Task:**

Your current task is to assess all neighboring nodes of the current node, with the objective of determining whether to proceed to the next neighboring node.

---

### **Requirements:**

1. Reflect on previous actions and prevent redundant revisiting of nodes or chunks.
2. You can only choose one action. This means that you can choose to read only one neighbor node or choose to terminate.

---

### **Response Criteria:**

Given the question, the rational plan, previous actions, notebook content, and the current node’s atomic facts and their corresponding chunk IDs, formulate a response that includes the following:
- rational_next_action: {CHUNK_READ_ARG_RATIONAL_NEXT_ACTION}
- chosen_action: {CHUNK_READ_ARG_CHOSEN_ACTION}

---

Please strictly follow the above format. Let’s begin.
"""


ANSWER_REASONING_ARG_ANALYZE = "Analysis of all notebook content and reasoning leading up to a final answer."
ANSWER_REASONING_ARG_FINAL_ANSWER = "Final answer to the original question, taking into account all available information."
ANSWER_REASONING_PROMPT = f"""{SHARED_READER_AGENT_INTRODUCTION_PROMPT}

---

### **Task:**

You have now explored multiple paths from various starting nodes on this graph, recording key information for each path in a notebook.
Your task now is to analyze these memories and reason to answer the question.

---

### **Requirements:**

1. You should first analyze all notebook content before providing a final answer.
2. During the analysis, consider complementary information from other notes and employ a majority voting strategy to resolve any inconsistencies.
3. When generating the final answer, ensure that you take into account all available information.

---

### **Example:**

User:
- Question: Who had a longer tennis career, Danny or Alice?
- Notebook of different exploration paths:
   1. We only know that Danny’s tennis career started in 1972 and ended in 1990, but we don’t know the length of Alice’s career.
   2. ......
Assistant:
- analysis: The summary of search path 1 points out that Danny’s tennis career is 1990-1972=18 years. Although it does not indicate the length of Alice’s career, the summary of search path 2 finds this information, that is, the length of Alice’s tennis career is 15 years. Then we can get the final answer, that is, Danny’s tennis career is longer than Alice’s.
- final_answer: Danny’s tennis career is longer than Alice’s.

---

Please strictly follow the above format. Let’s begin
"""


class Prompt:
    def __init__(self, version, prompt):
        self.version = version
        self.prompt = prompt

ExtractionPrompt = Prompt("1.1", EXTRACTION_PROMPT)
