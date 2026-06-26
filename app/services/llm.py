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
from app.core.logging import logger 
from app.services.prompts import build_prompt, post_process_answer, clean_answer

# Model intentionally NOT loaded at module level.
# Lazy loading ensures the model is only loaded into memory when needed.
model_name = "google/flan-t5-base"

_tokenizer: T5Tokenizer | None = None
_model: T5ForConditionalGeneration | None = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def _get_tokenizer_and_model():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        _tokenizer = T5Tokenizer.from_pretrained(model_name)
        _model = T5ForConditionalGeneration.from_pretrained(model_name)
        _model = _model.to(device)
    return _tokenizer, _model


def generate_answer(question: str, chunks: List[str], category: str = "general") -> str:
    """
    generates answer using category specific prompt
    uses flan-t5 for text generation
    """
    prompt = build_prompt(question, chunks, category)
    tokenizer, model = _get_tokenizer_and_model()

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
        early_stopping=True,       # stop when answer is complete
        temperature=0.7,         # controls randomness: lower = more deterministic
        no_repeat_ngram_size=3,   # prevent repeating phrases
        do_sample=True,            # use sampling (more creative/natural)
        repetition_penalty=1.2,   # penalize repeating tokens
    )

    # decode answer from numbers back to text
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # clean prompt artifacts from answer
    answer = clean_answer(answer, prompt)

    # post process based on category
    answer = post_process_answer(answer, category)
    return answer
