EXTRACTION_PROMPT = """You are now an intelligent assistant tasked with meticulously extracting both key elements and atomic facts from a long text. 

1. Key Elements: The essential nouns (e.g., characters, times, events, places, numbers) that exist within the text.  
2. Atomic Facts: The smallest, indivisible facts, presented as concise sentences. These include propositions, theories, existences, concepts, and implicit elements like logic, causality, descriptions, event sequences, interpersonal relationships, timelines, etc.  

---

**Requirements:**

1. Key elements must have consistent and full names for maximum graph connectivity and future query enhancement. (e.g. change delicious smoothies to smoothies; change Harry to Harry Potter).
2. Ensure that all identified key elements are reflected within the corresponding atomic facts.  
3. You should extract key elements and atomic facts comprehensively, especially those that are important and potentially query-worthy and **do not leave out details**.  
4. Whenever applicable, replace pronouns with their specific noun counterparts (e.g., change I, He, She to actual names).
5. Keep atomic facts concise and clear; avoid excessive verbosity.
6. Your output should not exceed 4000 tokens.
7. Answer only in the described XML format.

---

**Response Format:**
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

**Example:**
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


class Prompt:
    def __init__(self, version, prompt):
        self.version = version
        self.prompt = prompt

ExtractionPrompt = Prompt("1.1", EXTRACTION_PROMPT)
