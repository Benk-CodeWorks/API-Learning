import os
import json
from flask import Flask, request, jsonify, render_template
from supabase import create_client, Client
from dotenv import load_dotenv
import anthropic

load_dotenv()

app = Flask(__name__)

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)
claude = anthropic.Anthropic()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get-user/<user_id>")
def get_user(user_id):
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    if response.data:
        return jsonify(response.data[0])
    return jsonify({"error": "User not found"}), 404


@app.route("/get-users")
def get_all_users():
    response = supabase.table("users").select("*").execute()
    return jsonify(response.data)


@app.route("/create-user", methods=["POST"])
def create_user():
    data = request.get_json()
    new_user = {
        "name": data.get("name"),
        "email": data.get("email")
    }
    response = supabase.table("users").insert(new_user).execute()
    return jsonify({"message": "User created", "user": response.data[0]}), 201


@app.route("/delete-user/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    check = supabase.table("users").select("*").eq("id", user_id).execute()
    if not check.data:
        return jsonify({"error": "User not found"}), 404
    supabase.table("users").delete().eq("id", user_id).execute()
    return jsonify({"message": f"User {user_id} deleted"})


@app.route("/update-user/<user_id>", methods=["PATCH"])
def update_user(user_id):
    data = request.get_json()
    response = supabase.table("users").update(data).eq("id", user_id).execute()
    if not response.data:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User updated", "user": response.data[0]})


@app.route("/ask-claude", methods=["POST"])
def ask_claude():
    data = request.get_json()
    question = data.get("question", "").strip()
    include_users = data.get("include_users", False)

    if not question:
        return jsonify({"error": "Please provide a question"}), 400

    user_context = ""
    if include_users:
        users_response = supabase.table("users").select("*").execute()
        if users_response.data:
            user_context = f"\n\nCurrent users in the database:\n{json.dumps(users_response.data, indent=2)}"

    with claude.messages.stream(
        model="claude-opus-4-7",
        max_tokens=1024,
        thinking={"type": "adaptive"},
        system=[{
            "type": "text",
            "text": "You are a helpful assistant for a user management API built with Flask and Supabase. Answer questions clearly and concisely.",
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{
            "role": "user",
            "content": question + user_context
        }]
    ) as stream:
        message = stream.get_final_message()

    answer = next((b.text for b in message.content if b.type == "text"), "")
    return jsonify({"answer": answer, "tokens_used": message.usage.output_tokens})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)