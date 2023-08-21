from flask import Flask, request, jsonify
from processing import *
from models import *
import warnings

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        id = data['id']
        political_party_name = PoliticalPartyName[data['party']]
        chat_text = data['chat']
    except KeyError:
        return jsonify({'error': 'Invalid input data'}), 400

    coordinates, answer = process_chat(id, political_party_name, chat_text)

    return jsonify({'coordinates': coordinates, 'answer': answer})

@app.route('/query_composable_graph', methods=['POST'])
def query():
    try:
        data = request.json
        query_text = data['query']
    except KeyError:
        return jsonify({'error': 'Invalid input data'}), 400

    coordinates, answer = process_query_composable_graph(query_text)

    return jsonify({'coordinates': coordinates, 'answer': answer})

@app.route('/finish_conversation', methods=['POST'])
def finish():
    try:
        data = request.json
        id = data['id']
    except KeyError:
        return jsonify({'error': 'Invalid input data'}), 400

    result = finish_conversation(id)

    return jsonify({'result': result})


with app.app_context():
    wait_for_weaviate()
    clean_database() # TODO this should be done when closing the server
    initialize_indexes()
    create_composable_graph()
    warnings.filterwarnings("ignore") # SOURCE OF ALL EVIL
