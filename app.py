import logging
from flask import Flask, request, jsonify
from supabase import create_client, Client
from functools import wraps
from flask import Response, stream_with_context
import json
from constants import SUPABASE_URL, SUPABASE_ANON_KEY
from populate_vector_database import DataLoader
from utils import get_user_id
from config import initialize_indexes
from processing import process_chat, process_multi_party_chat

app = Flask(__name__)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def require_auth(supabase: Client):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.json.get("access_token")
            if not token:
                return jsonify({"error": "No token provided"}), 401
            try:
                user = supabase.auth.get_user(token)
            except Exception as e:
                return jsonify({"error": "Invalid token"}), 401
            kwargs["user"] = user
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@app.route("/multi-chat", methods=["POST"])
@require_auth(supabase)
def multi_chat(**kwargs):
    user = kwargs.get("user")
    user_id = get_user_id(user)
    try:
        data = request.json
        logging.info(f"Request data: {data}")
        chat_text = data["message"]
        previous_messages = data["previous_messages"]
        infer_chat_mode = data["infer_chat_mode"]
    except KeyError:
        return jsonify({"error": "Invalid input data"}), 400

    answer, references = process_multi_party_chat(
        None, chat_text, previous_messages, infer_chat_mode
    )

    return jsonify({"references": references, "message": answer})


@app.route("/chat", methods=["POST"])
@require_auth(supabase)
def chat(**kwargs):
    user = kwargs.get("user")
    user_id = get_user_id(user)
    try:
        data = request.json
        logging.info(f"Request data: {data}")
        chat_text = data["message"]
        political_party: str = data["party"]
        previous_messages = data["previous_messages"]
        infer_chat_mode = data["infer_chat_mode"]
    except KeyError:
        return jsonify({"error": "Invalid input data"}), 400

    if not political_party or type(political_party) is not str:
        return jsonify({"error": "Choose a party"}), 400

    answer, references = process_chat(
        political_party, chat_text, previous_messages, infer_chat_mode
    )

    return jsonify({"references": references, "message": answer})


@app.route("/stream-chat", methods=["POST"])
# @require_auth(supabase)
def stream_chat(**kwargs):
    # user = kwargs.get("user")
    # user_id = get_user_id(user)

    try:
        data = request.json
        political_party = data["political_party"]
        chat_text = data["chat"]
        previous_messages = data["previous_messages"]
        infer_chat_mode = data["infer_chat_mode"]
    except KeyError:
        return jsonify({"error": "Invalid input data"}), 400

    answer, references = process_chat(
        political_party, chat_text, previous_messages, infer_chat_mode, stream=True
    )

    def generate_stream_chat_response(coordinates, answer):
        yield '{"references":' + json.dumps(coordinates) + ',"message":"'
        for part in answer:
            yield part.replace('"', '\\"')
        yield '"}'

    return Response(
        stream_with_context(generate_stream_chat_response(references, answer))
    )  # Minor issue with different formatting (not encoded)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "OK"})


with app.app_context():
    try:
        data_loader = DataLoader()
        data_loader.populate_vector_database()
        initialize_indexes()
    except ValueError:
        initialize_indexes()
