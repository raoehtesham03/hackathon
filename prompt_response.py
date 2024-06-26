from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
from flask_allowedhosts import limit_hosts
from query import rag_chain
from es_client import create_es_client
from constants import *

app = Flask(__name__)
CORS(app)

def on_denied():
    return "Unauthorized access", 401

@app.route('/ask', methods=['POST'])
@limit_hosts(allowed_hosts=ALLOWED_HOSTS, on_denied=on_denied)
def ask():
    data = request.get_json()
    question = data.get('prompt')
    def generate():
        for result in rag_chain.stream(question):
            yield result
        yield '\n'
    return Response(stream_with_context(generate()), mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)