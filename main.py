import os
from PyPDF2 import PdfReader
import openai
import tiktoken
from fpdf import FPDF
from dotenv import load_dotenv

load_dotenv()

# openai api_key
openai.api_key = os.getenv("OPENAI_API_KEY")


# function to check PDF size and number of pages
def check_pdf_size(pdf_path):
    try:
        file_size = os.path.getsize(
            pdf_path) / (1024 * 1024)  # converting bytes to MB
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        return file_size, num_pages
    except Exception as e:
        print(f"Error while checking PDF size or pages: {e}")
        return None, None


# function to extract text from the PDF in chunks
def extract_text_by_chunks(pdf_path, pages_per_chunk=10):
    try:

        reader = PdfReader(pdf_path)
        chunks = []
        total_pages = len(reader.pages)

        for i in range(0, total_pages, pages_per_chunk):
            chunk_text = ""
            for j in range(i, min(i + pages_per_chunk, total_pages)):
                chunk_text = chunk_text + reader.pages[j].extract_text()
            chunks.append(chunk_text)
        return chunks

    except Exception as e:
        print(f"Error while extracting text from PDF: {e}")
        return []


# function to estimate tokens
def estimate_tokens(text, model="gpt-4"):
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception as e:
        print(f"Error while estimating tokens: {e}")
        return 0


# function to summarize text using GPT-4
def summarize_text(text, tone="formal", purpose="educational"):
    try:
        # construct the message for chat-based API
        messages = [
            {
                "role": "system",
                "content": (f"You are a helpful assistant tasked with summarizing text in a {tone} tone for a {purpose} audience. Focus on clarity, conciseness, and relevance.")
            },
            {
                "role": "user",
                "content": f"Summarize the following text:\n{text}"
            }
        ]

        # call the GPT-4 API
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )

        # extract and return the summary
        return (response.choices[0].message.content).strip()

    except Exception as e:
        print(f"Error while summarizing text with GPT-4: {e}")
        return "Error in generating summary."


# function to process and summarize all PDF chunks
def summarize_pdf(pdf_path, pages_per_chunk=10, tone="formal", purpose="educational"):
    try:

        # extract chunks from PDF.
        chunks = extract_text_by_chunks(pdf_path, pages_per_chunk)
        if not chunks:
            return "No text extracted from the PDF."

        # summarize each chunk
        summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i + 1} of {len(chunks)}...")
            summary = summarize_text(chunk, tone, purpose)
            summaries.append(summary)

        # combine all summaries into a single text
        combined_summary = "\n\n".join(summaries)
        return combined_summary

    except Exception as e:
        print(f"Error while summarizing PDF: {e}")
        return "Error in summarizing PDF."

# ------DEBUG-----

# file_size, pages = check_pdf_size("economy_research_paper.pdf")
# print("file_size", file_size)
# print("number of pages", pages)

# chunks_arr = extract_text_by_chunks("economy_research_paper.pdf")

# print(chunks_arr[0])
# print(chunks_arr[1])

# print(estimate_tokens("Interest Rate Incentives : Offering lower interest rates for green loans and projects to make them more attractive for investors and developers."))


if __name__ == "__main__":
    pdf_path = "economy_research_paper.pdf"
    tone = "formal"
    purpose = "educational"

    final_summary = summarize_pdf(
        pdf_path, pages_per_chunk=10, tone=tone, purpose=purpose)

    print("\n Final Combined Summary:\n")
    print(final_summary)
