from flask import Flask, request, jsonify
from processing import *
from config import *
import warnings
from supabase import create_client, Client
from functools import wraps

app = Flask(__name__)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def require_auth(supabase: Client):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"error": "No token provided"}), 401
            _ , error = supabase.auth.api.get_user(token)
            if error:
                return jsonify({"error": "Invalid token"}), 401
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route("/signup", methods=["POST"])
def signup():
    email = request.json.get("email")
    password = request.json.get("password")
    user, error = supabase.auth.sign_up({"email": email, "password": password})
    if error:
        return jsonify({"error": error.message}), 400
    return jsonify({"message": "Signup successful"}), 201


@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")
    password = request.json.get("password")
    user, error = supabase.auth.sign_in_with_password({"email": email, "password": password})
    if error:
        return jsonify({"error": error.message}), 400
    return jsonify({"message": "Login successful", "user": user}), 200


@app.route("/start_conversation", methods=["POST"])
@require_auth(supabase)
def start():
    try:
        data = request.json
        party = data["party"]
    except KeyError:
        return jsonify({"error": "Invalid input data"}), 400

    id = start_conversation(political_party=party)

    return jsonify({"id": id})


@app.route("/chat", methods=["POST"])
@require_auth(supabase)
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
@require_auth(supabase)
def query():
    try:
        data = request.json
        query_text = data["query"]
    except KeyError:
        return jsonify({"error": "Invalid input data"}), 400

    coordinates, answer = process_query_composable_graph(query_text)

    return jsonify({"coordinates": coordinates, "answer": answer})


@app.route("/finish_conversation/<int:id>", methods=["DELETE"])
@require_auth(supabase)
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
    