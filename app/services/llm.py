# from transformers import pipeline
# from typing import List


# # load free hugging face LLM model locally
# # downloads once and runs offline after that
# llm = pipeline("text2text-generation", model="google/flan-t5-base")


# def generate_answer(question: str, chunks: List[str]) -> str:
#     # combine all chunks into single context
#     context = " ".join(chunks)

#     # build prompt with context and question - this is what LLM receives
#     # clear instructions + context + question = better answer
#     prompt = f"""
#     Answer the question based on the context below.
#     Context: {context}
#     Question: {question}
#     Answer:
#     """


#     # send prompt to LLM
#     # max_length -> maximum words in answer
#     result = llm(prompt, max_length=200)

#     # result is list -> get first item -> get generated text
#     return result[0]["generated_text"]

""" 
NOTE : This implementation uses the transformers library directly for better performance and control, 
instead of the pipeline which is more general but slower.
The T5 model is a powerful text-to-text transformer that can generate answers based on the provided context and question.
"""

from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
from typing import List


# load tokenizer and model directly - faster than pipeline
tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

# use GPU if available, otherwise CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)


def generate_answer(question: str, chunks: List[str]) -> str:
    # combine all relevant chunks into single context string
    context = " ".join(chunks)

    # flan-t5 understands detailed instructions
    prompt = f"""
    Answer the question based on the context below.
    If answer is not in context say I don't know.
    Context: {context}
    Question: {question}
    Answer:
    """

    # tokenize prompt - converts text to numbers for model
    inputs = tokenizer(
        prompt,
        return_tensors="pt",      # return pytorch tensors
        max_length=512,           # max input length
        truncation=True           # cut if longer than max_length
    ).to(device)                  # move to GPU if available

    # generate answer
    outputs = model.generate(
        inputs.input_ids,
        max_new_tokens=150,       # max length of answer
        num_beams=4,              # better quality answer
        early_stopping=True       # stop when answer is complete
    )

    # decode answer from numbers back to text
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return answer
