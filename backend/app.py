from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)


# Database setup
def init_db():
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()

    # Products table
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY, name TEXT, category TEXT, 
                  price REAL, rating REAL, tags TEXT)''')

    # User interactions table
    c.execute('''CREATE TABLE IF NOT EXISTS user_interactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, 
                  product_id INTEGER, action TEXT, timestamp TEXT)''')

    # Seed initial products
    products = [
        (1, "Wireless Headphones", "Electronics", 79.99, 4.5, "audio,wireless,music"),
        (2, "Running Shoes", "Sports", 89.99, 4.7, "fitness,running,outdoor"),
        (3, "Coffee Maker", "Home", 49.99, 4.3, "kitchen,coffee,appliance"),
        (4, "Yoga Mat", "Sports", 29.99, 4.6, "fitness,yoga,exercise"),
        (5, "Laptop Stand", "Electronics", 39.99, 4.4, "workspace,ergonomic,desk"),
        (6, "Smart Watch", "Electronics", 199.99, 4.8, "fitness,tech,wearable"),
        (7, "Protein Powder", "Health", 34.99, 4.5, "fitness,nutrition,supplement"),
        (8, "Desk Lamp", "Home", 44.99, 4.2, "workspace,lighting,desk"),
        (9, "Bluetooth Speaker", "Electronics", 59.99, 4.6, "audio,wireless,portable"),
        (10, "Water Bottle", "Sports", 24.99, 4.4, "fitness,hydration,outdoor")
    ]

    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO products VALUES (?,?,?,?,?,?)", products)
        print("✅ Database initialized with 10 products")

    conn.commit()
    conn.close()


# Get user behavior
def get_user_behavior(user_id):
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()

    c.execute('''SELECT product_id, action FROM user_interactions 
                 WHERE user_id=? ORDER BY timestamp DESC''', (user_id,))
    interactions = c.fetchall()

    viewed = [i[0] for i in interactions if i[1] == 'view']
    purchased = [i[0] for i in interactions if i[1] == 'purchase']

    conn.close()
    return {'viewed': viewed, 'purchased': purchased}


# Recommendation algorithm
def generate_recommendations(user_id, limit=3):
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()

    # Get user behavior
    behavior = get_user_behavior(user_id)
    viewed_ids = set(behavior['viewed'])
    purchased_ids = set(behavior['purchased'])

    # Get all products
    c.execute("SELECT * FROM products")
    products = c.fetchall()

    scored_products = []

    for product in products:
        prod_id, name, category, price, rating, tags = product
        tags_list = tags.split(',')

        # Skip purchased products
        if prod_id in purchased_ids:
            continue

        score = 0

        # Get viewed products for comparison
        if viewed_ids:
            c.execute("SELECT category, tags FROM products WHERE id IN ({})".format(
                ','.join('?' * len(viewed_ids))), list(viewed_ids))
            viewed_products = c.fetchall()

            # Category match
            viewed_categories = [vp[0] for vp in viewed_products]
            if category in viewed_categories:
                score += 30

            # Tag overlap
            for vp in viewed_products:
                vp_tags = vp[1].split(',')
                tag_overlap = len(set(tags_list) & set(vp_tags))
                score += tag_overlap * 10

        # Rating boost
        score += rating * 5

        # Penalize already viewed
        if prod_id in viewed_ids:
            score *= 0.5

        scored_products.append({
            'id': prod_id,
            'name': name,
            'category': category,
            'price': price,
            'rating': rating,
            'tags': tags_list,
            'score': score
        })

    conn.close()

    # Sort and return top recommendations
    scored_products.sort(key=lambda x: x['score'], reverse=True)
    return scored_products[:limit]


# LLM-powered explanation generator
def generate_explanation(product, user_id):
    behavior = get_user_behavior(user_id)

    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()

    explanation = f"We recommend the {product['name']} for you because "
    reasons = []

    # Analyze viewed products
    if behavior['viewed']:
        c.execute("SELECT category, tags FROM products WHERE id IN ({})".format(
            ','.join('?' * len(behavior['viewed']))), behavior['viewed'])
        viewed = c.fetchall()

        viewed_categories = [v[0] for v in viewed]
        if product['category'] in viewed_categories:
            reasons.append(f"you've shown interest in {product['category']} products")

        # Tag analysis
        all_viewed_tags = []
        for v in viewed:
            all_viewed_tags.extend(v[1].split(','))
        common_tags = [tag for tag in product['tags'] if tag in all_viewed_tags]
        if common_tags:
            reasons.append(f"it matches your interests in {', '.join(common_tags)}")

    # Purchase history
    if behavior['purchased']:
        c.execute("SELECT category FROM products WHERE id IN ({})".format(
            ','.join('?' * len(behavior['purchased']))), behavior['purchased'])
        purchased = c.fetchall()
        purchased_categories = [p[0] for p in purchased]

        if product['category'] in purchased_categories:
            reasons.append(f"it complements your recent {product['category']} purchases")

    # Rating
    if product['rating'] >= 4.5:
        reasons.append(f"it has excellent customer reviews ({product['rating']}★)")

    if not reasons:
        reasons.append("it's a popular choice among customers with similar preferences")

    explanation += ', '.join(reasons) + '. '

    # Price point
    if product['price'] < 50:
        explanation += f"At ${product['price']}, it offers great value for money."
    else:
        explanation += f"This premium product is priced at ${product['price']}."

    conn.close()
    return explanation


# API Routes
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()

    result = []
    for p in products:
        result.append({
            'id': p[0], 'name': p[1], 'category': p[2],
            'price': p[3], 'rating': p[4], 'tags': p[5].split(',')
        })

    return jsonify(result)


@app.route('/api/recommendations/<user_id>', methods=['GET'])
def get_recommendations(user_id):
    limit = request.args.get('limit', 3, type=int)
    recommendations = generate_recommendations(user_id, limit)

    # Add explanations
    for rec in recommendations:
        rec['explanation'] = generate_explanation(rec, user_id)

    return jsonify(recommendations)


@app.route('/api/interaction', methods=['POST'])
def log_interaction():
    data = request.json
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    action = data.get('action')  # 'view' or 'purchase'

    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('''INSERT INTO user_interactions (user_id, product_id, action, timestamp)
                 VALUES (?, ?, ?, ?)''',
              (user_id, product_id, action, datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})


@app.route('/api/user/<user_id>/behavior', methods=['GET'])
def get_behavior(user_id):
    behavior = get_user_behavior(user_id)
    return jsonify(behavior)


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'E-commerce Recommender API',
        'endpoints': {
            'GET /api/products': 'Get all products',
            'GET /api/recommendations/<user_id>': 'Get recommendations',
            'POST /api/interaction': 'Log user interaction',
            'GET /api/user/<user_id>/behavior': 'Get user behavior'
        }
    })


if __name__ == '__main__':
    print("🚀 Starting E-commerce Recommender API...")
    init_db()
    print("✅ Server running on http://localhost:5000")
    app.run(debug=True, port=5000)
    from flask_cors import CORS
    CORS(app)
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
