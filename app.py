from flask import Flask, request, jsonify
from processing import *
from config import *
import warnings

app = Flask(__name__)

@app.route("/start_conversation", methods=["POST"])
def start():
    try:
        data = request.json
        party = data["party"]
    except KeyError:
        return jsonify({"error": "Invalid input data"}), 400

    id = start_conversation(political_party=party)

    return jsonify({"id": id})


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        id = int(data["id"])
        chat_text = data["chat"]
    except KeyError:
        return jsonify({"error": "Invalid input data"}), 400

    coordinates, answer = process_chat(id, chat_text)

    return jsonify({"coordinates": coordinates, "answer": answer})


@app.route("/query_composable_graph", methods=["POST"])
def query():
    try:
        data = request.json
        query_text = data["query"]
    except KeyError:
        return jsonify({"error": "Invalid input data"}), 400

    coordinates, answer = process_query_composable_graph(query_text)

    return jsonify({"coordinates": coordinates, "answer": answer})


@app.route("/finish_conversation/<int:id>", methods=["DELETE"])
def finish(id):
    try:
        result = finish_conversation(id)
    except ValueError:
        return jsonify({"result": "Invalid conversation ID"}), 400

    return jsonify({"result": result})
    


with app.app_context():
    warnings.filterwarnings("ignore")  # SOURCE OF ALL EVIL
    
    wait_for_weaviate()
    wait_for_redis()
    
    clean_weviate_database()  # TODO this should be done when closing the server
    initialize_redis()
    initialize_indexes()
    create_composable_graph()
    