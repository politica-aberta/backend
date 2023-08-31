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
            token = request.json.get("access_token")
            if not token:
                return jsonify({"error": "No token provided"}), 401
            try:
                user = supabase.auth.get_user(token)
            except Exception as e:
                return jsonify({"error": "Invalid token"}), 401
            kwargs['user'] = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route("/signup", methods=["POST"])
def signup():
    email = request.json.get("email")
    password = request.json.get("password")
    try:
        supabase.table(SUPABASE_USER_TABLE).insert({"id": get_user_id(user)}).execute()

        user = supabase.auth.sign_up({"email": email, "password": password})

        # TODO there needs to be a rollout in case of problem
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    return jsonify({"message": "Signup successful"}), 201


@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")
    password = request.json.get("password")
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"message": "Login successful", "access_token": res.session.access_token}), 200


@app.route("/start_conversation", methods=["POST"])
@require_auth(supabase)
def start(**kwargs):
    user = kwargs.get('user')

    user_id = get_user_id(user)

    try:
        data = request.json
        party = data["party"]
    except KeyError:
        return jsonify({"error": "Invalid input data"}), 400

    id = start_conversation(user_id, party, supabase)

    return jsonify({"id": id})


@app.route("/chat", methods=["POST"])
@require_auth(supabase)
def chat(**kwargs):
    user = kwargs.get('user')

    user_id = get_user_id(user)

    try:
        data = request.json
        conversation_id = data["id"]
        chat_text = data["chat"]
    except KeyError:
        return jsonify({"error": "Invalid input data"}), 400


    usage = get_usage(supabase.table(SUPABASE_USER_TABLE).select("usage").eq("id", user_id).execute())

    if usage >= MAX_USAGE:
        return jsonify({"error": "No more messages allowed"}), 400
    else:
        supabase.table(SUPABASE_USER_TABLE).update({"usage": usage + 1}).eq("id", user_id).execute()

    # FIXME this should be done in a transactional manner
    # FIXME this should have more advanced error handling

    coordinates, answer = process_chat(conversation_id, chat_text)

    return jsonify({"coordinates": coordinates, "answer": answer})


@app.route("/query_composable_graph", methods=["POST"])
@require_auth(supabase)
def query(**kwargs):
    user = kwargs.get('user')

    try:
        data = request.json
        query_text = data["query"]
    except KeyError:
        return jsonify({"error": "Invalid input data"}), 400

    coordinates, answer = process_query_composable_graph(query_text)

    return jsonify({"coordinates": coordinates, "answer": answer})


@app.route("/finish_conversation/<int:id>", methods=["DELETE"])
@require_auth(supabase)
def finish(id, **kwargs):
    user = kwargs.get('user')

    try:
        result = finish_conversation(id)
    except ValueError:
        return jsonify({"result": "Invalid conversation ID"}), 400

    return jsonify({"result": result})
    


with app.app_context():
    warnings.filterwarnings("ignore")  # SOURCE OF ALL EVIL
    
    wait_for_weaviate()
    
    clean_weviate_database()  # TODO this should be done when closing the server
    initialize_indexes()
    create_composable_graph()
    