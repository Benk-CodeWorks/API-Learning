"""
Simple REST API - Books Collection
Demonstrates the 4 core HTTP methods: GET, POST, PUT, DELETE
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory data store (acts like a database for learning purposes)
books = [
    {"id": 1, "title": "The Pragmatic Programmer", "author": "David Thomas", "year": 1999},
    {"id": 2, "title": "Clean Code", "author": "Robert C. Martin", "year": 2008},
    {"id": 3, "title": "You Don't Know JS", "author": "Kyle Simpson", "year": 2015},
]
next_id = 4


def find_book(book_id):
    return next((b for b in books if b["id"] == book_id), None)


# GET /books — retrieve all books
@app.route("/books", methods=["GET"])
def get_books():
    return jsonify({"books": books, "count": len(books)})


# GET /books/<id> — retrieve a single book by ID
@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = find_book(book_id)
    if book is None:
        return jsonify({"error": f"Book {book_id} not found"}), 404
    return jsonify(book)


# POST /books — create a new book
@app.route("/books", methods=["POST"])
def create_book():
    global next_id
    data = request.get_json()

    if not data or not data.get("title") or not data.get("author"):
        return jsonify({"error": "title and author are required"}), 400

    new_book = {
        "id": next_id,
        "title": data["title"],
        "author": data["author"],
        "year": data.get("year"),
    }
    books.append(new_book)
    next_id += 1

    return jsonify(new_book), 201


# PUT /books/<id> — update an existing book
@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = find_book(book_id)
    if book is None:
        return jsonify({"error": f"Book {book_id} not found"}), 404

    data = request.get_json()
    if not data or not data.get("title") or not data.get("author"):
        return jsonify({"error": "title and author are required"}), 400

    book["title"] = data["title"]
    book["author"] = data["author"]
    book["year"] = data.get("year")

    return jsonify(book)


# DELETE /books/<id> — delete a book
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = find_book(book_id)
    if book is None:
        return jsonify({"error": f"Book {book_id} not found"}), 404

    books.remove(book)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5000)