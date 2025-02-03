from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL="/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL="/static/masterblog.json" # (2) ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API' # (3) You can change this if you like
    }
)

app = Flask(__name__)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
    {"id": 3, "title": "Travel Adventures", "content": "Exploring the hidden gems of Southeast Asia."},
    {"id": 4, "title": "Cooking Tips", "content": "The secret to perfect pasta is in the sauce preparation."},
    {"id": 5, "title": "Tech News", "content": "Latest developments in artificial intelligence and machine learning."},
    {"id": 6, "title": "Book Review", "content": "A fascinating journey through classic literature."},
    {"id": 7, "title": "Fitness Guide", "content": "Essential workout routines for beginners."},
    {"id": 8, "title": "Garden Tips", "content": "How to grow organic vegetables in your backyard."},
    {"id": 9, "title": "Music Review", "content": "Analysis of contemporary classical compositions."},
    {"id": 10, "title": "Photography Basics", "content": "Understanding composition and lighting techniques."},
]


@app.route('/api/posts/<id>', methods=['DELETE'])
def delete_posts(id):
    global POSTS
    POSTS = [post for post in POSTS if post['id'] != int(id)]
    print(POSTS)
    return jsonify({"message": f"Post with id {id} has been deleted successfully."}), 200

@app.route('/api/posts/<id>', methods=['PUT'])
def update_post(id):
    global POSTS
    update_data = request.json
    if not update_data or 'title' not in update_data or 'content' not in update_data:
        return jsonify({'error': 'Missing required fields: title and content'}), 400
    
    for post in POSTS:
        if post['id'] == int(id):
            post['title'] = update_data['title']
            post['content'] = update_data['content']
            return jsonify(post), 200
    
    return jsonify({'error': f'Post with id {id} not found'}), 404

@app.route('/api/posts', methods=['GET', 'POST'], strict_slashes=False)
def get_posts():
    sort = request.args.get('sort')
    direction = request.args.get('direction')
    if request.method == 'POST':
        new_post = request.json
        if not new_post or 'title' not in new_post or 'content' not in new_post:
            return jsonify({'error': 'Missing required fields: title and content'}), 400
        POSTS.append(new_post)
        
        return jsonify(new_post), 201
    
    if sort and direction:
        print('ccc')
        sorted_posts = sorted(POSTS, key=lambda x: x[sort], reverse=direction == 'desc')
    else:
        print('ddd')
        sorted_posts = POSTS

    return jsonify(sorted_posts)

@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title = request.args.get('title')
    content = request.args.get('content')

    filtered_posts = []
    for post in POSTS:
        if (title and title.lower() in post['title'].lower()) or \
           (content and content.lower() in post['content'].lower()):
            filtered_posts.append(post)
    
    return jsonify(filtered_posts)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
