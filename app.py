from flask import Flask, request, jsonify
from processing import *
from models import *
import warnings
from dotenv import load_dotenv, find_dotenv

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query():
    try:
        data = request.json
        id = data['id']
        political_party_name = PoliticalPartyName[data['party']]
        query_text = data['query']
    except KeyError:
        return jsonify({'error': 'Invalid input data'}), 400

    coordinates, answer = process_query(id, political_party_name, query_text)

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
    load_dotenv(find_dotenv()) # NOT Working
    wait_for_weaviate()
    clean_database() # TODO this should be done when closing the server
    initialize_indexes()
    warnings.filterwarnings("ignore") # SOURCE OF ALL EVIL
