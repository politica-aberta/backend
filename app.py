from flask import Flask, request, jsonify
from processing import *
from config import *
from supabase import create_client, Client
from functools import wraps
from flask import Response, stream_with_context
import json
import logging

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


@app.route("/chat", methods=["POST"])
@require_auth(supabase)
def chat(**kwargs):
    user = kwargs.get("user")
    user_id = get_user_id(user)

    try:
        data = request.json
        political_party = data["political_party"]
        chat_text = data["chat"]
        previous_messages = data["previous_messages"]
        infer_chat_mode = data["infer_chat_mode"]
    except KeyError:
        return jsonify({"error": "Invalid input data"}), 400

    coordinates, answer = process_chat(
        political_party, chat_text, previous_messages, infer_chat_mode
    )

    return jsonify({"coordinates": coordinates, "answer": answer})


@app.route("/stream-chat", methods=["POST"])
@require_auth(supabase)
def stream_chat(**kwargs):
    user = kwargs.get("user")
    user_id = get_user_id(user)

    try:
        data = request.json
        political_party = data["political_party"]
        chat_text = data["chat"]
        previous_messages = data["previous_messages"]
        infer_chat_mode = data["infer_chat_mode"]
    except KeyError:
        return jsonify({"error": "Invalid input data"}), 400

    coordinates, answer = process_chat(
        political_party, chat_text, previous_messages, infer_chat_mode, stream=True
    )

    def generate_stream_chat_response(coordinates, answer):
        yield '{"coordinates":' + json.dumps(coordinates) + ',"answer":"'
        for part in answer:
            yield part.replace('"', '\\"')
        yield '"}'

    return Response(
        stream_with_context(generate_stream_chat_response(coordinates, answer))
    )  # Minor issue with different formatting (not encoded)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "OK"})


with app.app_context():
    initialize_indexes()
