import os
import streamlit as st
from dotenv import load_dotenv
import fitz  # PyMuPDF for PDF extraction
from groq import Groq
load_dotenv()
# Initialize the Groq client with the API key from environment variables
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("API key for Groq is missing. Please set it in the environment variables.")
else:
    client = Groq(api_key=groq_api_key)

# System prompt for the financial analyst role
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are a financial analyst. Your job is to analyze the financial data provided and answer any questions related to the company’s financial health, performance, and overall viability. Provide detailed, professional answers."
    ),
}

# Function to extract text from a PDF using PyMuPDF
def extract_text_from_pdf(pdf_file):
    """Extracts text from an uploaded PDF file."""
    pdf_text = ""
    try:
        # Use the file-like object provided by Streamlit's file uploader directly
        with fitz.open(stream=pdf_file.read(), filetype="pdf") as pdf:
            for page_num in range(pdf.page_count):
                page = pdf.load_page(page_num)
                pdf_text += page.get_text("text")
        return pdf_text.strip()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

# Function to generate a response from Groq using the Mistral model
def get_financial_analysis(user_question, financial_data):
    """Generates financial analysis using Groq API."""
    try:
        messages = [
            SYSTEM_PROMPT,
            {"role": "user", "content": f"{user_question}\n\nFinancial Data: {financial_data}"}
        ]

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="mixtral-8x7b-32768"
        )

        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling Groq API: {str(e)}")
        return None

# Streamlit UI for user interaction
st.title("Financial Analyst Chatbot")

# Allow user to upload three PDF files
balance_sheet_file = st.file_uploader("Upload the Balance Sheet PDF", type="pdf")
income_statement_file = st.file_uploader("Upload the Income Statement PDF", type="pdf")
cash_flow_statement_file = st.file_uploader("Upload the Cash Flow Statement PDF", type="pdf")

# Input field for the user to ask a financial question
user_question = st.text_input("Ask a financial question about the company:")

# Trigger analysis on button click
if st.button("Analyze"):
    if balance_sheet_file and income_statement_file and cash_flow_statement_file and user_question:
        # Extract financial data from PDFs
        balance_sheet_data = extract_text_from_pdf(balance_sheet_file)
        income_statement_data = extract_text_from_pdf(income_statement_file)
        cash_flow_statement_data = extract_text_from_pdf(cash_flow_statement_file)

        if balance_sheet_data and income_statement_data and cash_flow_statement_data:
            combined_financial_data = (
                f"Balance Sheet Data:\n{balance_sheet_data}\n\n"
                f"Income Statement Data:\n{income_statement_data}\n\n"
                f"Cash Flow Statement Data:\n{cash_flow_statement_data}"
            )

            # Display the extracted financial data
            # st.text_area("Combined Financial Data", combined_financial_data, height=300)

            # Get financial analysis
            analysis = get_financial_analysis(user_question, combined_financial_data)

            if analysis:
                st.write("Analysis Result:")
                st.write(analysis)
        else:
            st.error("Failed to extract financial data from one or more PDFs.")
    else:
        st.warning("Please upload all three PDFs and enter a question.")
