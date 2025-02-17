from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import json
import os

class PostManager:
    def __init__(self):
        self.posts = []
        self.next_id = 1
        # Load posts from seedData.json
        with open(os.path.join(os.path.dirname(__file__), 'static/seedData.json')) as f:
            data = json.load(f)
            self.posts = data['posts']
            # Initialize next_id based on existing posts
            if self.posts:
                self.next_id = max(post['id'] for post in self.posts) + 1
    
    def delete_post(self, post_id):
        self.posts = [post for post in self.posts if post['id'] != post_id]
    
    def add_post(self, post):
        post['id'] = self.next_id
        self.next_id += 1
        self.posts.append(post)
        return post
    
    def get_posts(self, sort=None, direction=None):
        if sort and direction:
            return sorted(self.posts, key=lambda x: x[sort], reverse=direction == 'desc')
        return self.posts

# Initialize the post manager
post_manager = PostManager()

SWAGGER_URL="/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL="/static/masterblog.json" 

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API' 
    }
)

app = Flask(__name__)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
CORS(app)  # enable CORS for all routes


@app.route('/api/posts/<id>', methods=['DELETE'])
def delete_posts(id):
    post_manager.delete_post(int(id))
    return jsonify({"message": f"Post with id {id} has been deleted successfully."}), 200

@app.route('/api/posts/<id>', methods=['PUT'])
def update_post(id):
    update_data = request.json
    if not update_data or 'title' not in update_data or 'content' not in update_data:
        return jsonify({'error': 'Missing required fields: title and content'}), 400
    
    for post in post_manager.get_posts():
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
        new_post = post_manager.add_post(new_post)
        return jsonify(new_post), 201
    
    return jsonify(post_manager.get_posts(sort, direction))

@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title = request.args.get('title')
    content = request.args.get('content')

    filtered_posts = []
    for post in post_manager.get_posts():
        if (title and title.lower() in post['title'].lower()) or \
           (content and content.lower() in post['content'].lower()):
            filtered_posts.append(post)
    
    return jsonify(filtered_posts)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)

# http://localhost:5002/api/posts?sort=title&direction=asc