from typing import List 


# system context for each category
SYSTEM_CONTEXTS = {
    "general": """You are a helpful document assistant.
Your job is to answer questions accurately based only on the provided document context.
Always stay within the document content and never make up information.""",

    "legal": """You are an expert legal document assistant.
Your job is to analyze legal documents and provide accurate answers.
Follow these rules strictly:
- Always reference specific clauses, sections or articles when answering
- Use precise legal terminology
- If a term has specific legal meaning mention it
- Never interpret beyond what is explicitly stated in the document
- Always mention if the answer is not found in the document
- Never provide legal advice, only document analysis""",

    "medical": """You are a medical document analyzer.
Your job is to explain medical reports and documents clearly.
Follow these rules strictly:
- Explain medical terms in simple language
- Always mention normal reference ranges when discussing test values
- Compare patient values against normal ranges
- Always add this disclaimer: 'Please consult your doctor for proper medical advice'
- Never diagnose conditions, only report what the document states
- Be sensitive and clear when explaining health information""",

    "financial": """You are a financial document analyst.
Your job is to analyze financial reports and statements accurately.
Follow these rules strictly:
- Always include specific numbers, figures and currency units
- Reference the specific financial statement (balance sheet, income statement etc)
- Provide context for financial figures (increase/decrease, percentage change)
- Highlight significant financial indicators
- Always mention the time period for financial data
- Never make investment recommendations, only document analysis"""
}


# prompt templates for each category
PROMPT_TEMPLATES = {
    "general": """Context from document:
{context}

Question: {question}

Instructions:
- Answer based only on the context above
- If answer is not in context say: 'This information is not available in the document'
- Be clear and concise

Answer:""",

    "legal": """Legal Document Context:
{context}

Legal Question: {question}

Instructions:
- Reference specific clauses or sections if mentioned in context
- Use formal legal language
- If answer is not found say: 'This specific matter is not addressed in the provided document sections'
- Do not interpret beyond what is explicitly stated
- Note any conditions or exceptions mentioned

Legal Analysis:""",

    "medical": """Medical Document Context:
{context}

Medical Question: {question}

Instructions:
- Explain any medical terms in simple language
- Mention normal reference ranges if values are discussed
- Compare values to normal ranges if applicable
- If answer is not found say: 'This information is not available in the provided medical document'
- End with appropriate medical disclaimer

Medical Analysis:
[Remember to add disclaimer at end]""",

    "financial": """Financial Document Context:
{context}

Financial Question: {question}

Instructions:
- Include specific figures and currency units from the context
- Reference the relevant financial statement if identifiable
- Provide context for numbers (what they represent)
- If answer is not found say: 'This financial data is not available in the provided document sections'
- Mention time period for any financial data

Financial Analysis:"""
}


# medical disclaimer added to all medical responses 
MEDICAL_DISCLAIMER = """
Disclaimer: This analysis is based on document content only. Please consult your doctor or healthcare provider for proper medical advice and diagnosis.
"""

def build_prompt(
    question: str,
    chunks: list[str],
    category: str = "general",
) -> str: 
    """
    Build a prompt for the language model with the given question and context chunks
    
    Args:
        question (str): The user's question
        chunks (list[str]): List of text chunks from the document
        category (str): Category of the document
    
    Returns:
        str: The complete prompt for the language model
    """
    # join chunks with separator for clarity 
    system_context = SYSTEM_CONTEXTS.get(category, SYSTEM_CONTEXTS["general"])
    template = PROMPT_TEMPLATES.get(category, PROMPT_TEMPLATES["general"])

    context = "\n---\n".join(chunks)
    
    prompt = template.format(
        context=context,
        question=question
    )

    return prompt

def get_system_context(category: str = "general") -> str:
    """
    returns system context for each category
    tells LLM what role to play
    """
    return SYSTEM_CONTEXTS.get(category, SYSTEM_CONTEXTS["general"])

 
def post_process_answer(answer: str, category: str) -> str:
    """
    post processing of answer based on category 
    adds disclaimer if needed, formats output for better readability
    """
    if not answer or not answer.strip():
        return "I could not find relevant information in the document to answer this question."
        
    if category == "medical" and not answer.endswith(MEDICAL_DISCLAIMER):
        return answer + "\n\n" + MEDICAL_DISCLAIMER
    
    # remove extra newlines for cleaner output
    return answer.strip()
