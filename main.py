import os
from flask import Flask, request, jsonify, render_template
from supabase import create_client, Client
from dotenv import load_dotenv

# Load variables from .env into the environment
load_dotenv()

app = Flask(__name__)

# Set up the Supabase client (one-time setup)
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Home route — serves the dashboard UI
@app.route("/")
def home():
    return render_template("index.html")


# GET a single user by ID
@app.route("/get-user/<user_id>")
def get_user(user_id):
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    
    if response.data:  # if list is not empty
        return jsonify(response.data[0])
    return jsonify({"error": "User not found"}), 404


# GET all users
@app.route("/get-users")
def get_all_users():
    response = supabase.table("users").select("*").execute()
    return jsonify(response.data)


# POST — create a new user
@app.route("/create-user", methods=["POST"])
def create_user():
    data = request.get_json()
    
    new_user = {
        "name": data.get("name"),
        "email": data.get("email")
    }
    
    response = supabase.table("users").insert(new_user).execute()
    
    return jsonify({
        "message": "User created",
        "user": response.data[0]
    }), 201


# DELETE a user
@app.route("/delete-user/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    # Check if user exists first
    check = supabase.table("users").select("*").eq("id", user_id).execute()
    if not check.data:
        return jsonify({"error": "User not found"}), 404
    
    supabase.table("users").delete().eq("id", user_id).execute()
    return jsonify({"message": f"User {user_id} deleted"})


# PATCH — update a user
@app.route("/update-user/<user_id>", methods=["PATCH"])
def update_user(user_id):
    data = request.get_json()
    
    response = supabase.table("users").update(data).eq("id", user_id).execute()
    
    if not response.data:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "message": "User updated",
        "user": response.data[0]
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)