from flask import Flask, request, render_template, jsonify, make_response
from flask_cors import CORS
import os
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

load_dotenv()

app = Flask(__name__)
CORS(app, support_credentials=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)

context_extraction_prompt = PromptTemplate.from_template("""
/*
Extract the main context and key points from the following question. This will help in understanding the purpose and requirements of the code provided in the answers. That will help in generating context-aware inline comments.:
{question}
*/
""")

code_comment_prompt = PromptTemplate.from_template("""
/*
Generate appropriate and concise inline comments for the following code snippet considering the provided context. An inline comment is a single-line comment typically used to explain or clarify a specific line of code. It starts with // for Java and # for Python. Don't alter the given code snippet. Moreover, don't generate any other types of comments except inline comments:
Context: {context}
Code Snippet: {code_block}
*/
""")

context_chain = LLMChain(llm=llm, prompt=context_extraction_prompt, verbose=True)
comment_chain = LLMChain(llm=llm, prompt=code_comment_prompt, verbose=True)


def filter_comments(comments):
    # Patterns to identify lines that do not need comments
    unnecessary_comment_patterns = [
        r"^\s*def\s", r"^\s*class\s",  # Function and class definitions in Python
        r"^\s*public\s", r"^\s*private\s", r"^\s*protected\s",  # Java access modifiers
        r"^\s*return\s", r"^\s*break\s", r"^\s*continue\s",  # Common control flow keywords
        r"^\s*if\s", r"^\s*for\s", r"^\s*while\s", r"^\s*else\s", r"^\s*elif\s", r"^\s*switch\s", r"^\s*case\s", r"^\s*default\s",  # Control structures
        r"^\s*var\s", r"^\s*let\s", r"^\s*const\s", r"^\s*int\s", r"^\s*float\s", r"^\s*double\s", r"^\s*String\s", r"^\s*boolean\s"  # Variable declarations
    ]
    lines = comments.split('\n')
    filtered_comments = []

    i = 0
    while i < len(lines):
        current_line = lines[i]
        stripped_current_line = current_line.strip()
        previous_line = lines[i-1].strip() if i > 0 else ""
        # Check if the current line matches any of the patterns
        if any(re.search(pattern, stripped_current_line) for pattern in unnecessary_comment_patterns):
            # Check if the previous line is a comment
            if previous_line.startswith('#') or previous_line.startswith('//'):
                # Skip the previous line (comment)
                filtered_comments.pop()
            # Check for inline comments on the current line
            inline_comment_position = stripped_current_line.find('#')
            if inline_comment_position == -1:
                inline_comment_position = stripped_current_line.find('//')
            if inline_comment_position != -1:
                # Keep only the code part, remove the comment part
                current_line = current_line[:current_line.find('#')].rstrip() if current_line.find('#') != -1 else current_line[:current_line.find('//')].rstrip()
        # Add the current line to filtered output
        filtered_comments.append(current_line)
        i += 1

    return '\n'.join(filtered_comments)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        code_block = request.form['code']
        question = request.form['question']
        context_response = context_chain.run(question=question)
        response = comment_chain.run(context=context_response, code_block=code_block)
        filtered_response = filter_comments(response)
        return render_template('result.html', original_code=code_block, comments=filtered_response, context=context_response)
    return render_template('index.html')

@app.route('/comment', methods=['POST', 'OPTIONS'])
def comment():
    if request.method == 'OPTIONS':
        response = make_response('', 204)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response

    code_block = request.json['code']
    question = request.json['question']
    context_response = context_chain.run(question=question)
    processed_result = comment_chain.run(context=context_response, code_block=code_block)
    filtered_result = filter_comments(processed_result)
    
    
    filtered_lines = filtered_result.split('\n')
    final_result = '\n'.join(filtered_lines[1:-1])
    
    return jsonify(final_result)

if __name__ == '__main__':
    app.run(debug=True)   