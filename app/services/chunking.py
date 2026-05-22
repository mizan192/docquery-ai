from typing import List


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    # clean text - remove extra spaces and newlines
    text = " ".join(text.split())

    chunks = []
    start = 0

    while start < len(text):
        # get chunk of chunk_size characters
        end = start + chunk_size

        # if not last chunk, find nearest space to avoid cutting words
        if end < len(text):
            space_pos = text.rfind(" ", start, end)
            if space_pos != -1:  # only use space position if one was found
                end = space_pos

        # extract chunk and add to list
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # move start forward with overlap — ensure we always make forward progress
        new_start = end - overlap
        if new_start <= start:  # safety guard against infinite loop
            new_start = start + chunk_size
        start = new_start

    return chunks
