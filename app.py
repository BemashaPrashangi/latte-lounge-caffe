from flask import Flask, render_template, request, session, jsonify
from datetime import datetime
import pymysql
import re
import random
import difflib
import os
import sqlite3
from urllib.parse import urlparse

# ==============================================================================
# EXTERNAL KNOWLEDGE ENGINE CONFIGURATION
# ==============================================================================
# Set your API key here or in your environment variables (GEMINI_API_KEY)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

try:
    # pyrefly: ignore [missing-import]
    import google.generativeai as genai
    if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY":
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="Act as a helpful barista at Latte Lounge Cafe in Sri Lanka."
        )
    else:
        gemini_model = None
except Exception as e:
    genai = None
    gemini_model = None

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this for production

# In serverless cloud environments (like Vercel), use /tmp for writeable SQLite database
if os.environ.get("VERCEL"):
    SQLITE_DB_PATH = "/tmp/latte_lounge_caffe.db"
else:
    SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'latte_lounge_caffe.db')

def seed_sqlite_database():
    """Seeds SQLite database automatically if tables do not exist, ensuring zero-configuration cloud deployment."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            time_range TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category_id INTEGER NOT NULL,
            is_vegetarian INTEGER DEFAULT 0,
            is_drink INTEGER DEFAULT 0,
            is_dessert INTEGER DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            order_type TEXT NOT NULL,
            delivery_address TEXT,
            payment_method TEXT NOT NULL,
            total_amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            menu_item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
        );
        CREATE TABLE IF NOT EXISTS unknown_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    # Check if categories already seeded
    c.execute("SELECT COUNT(*) FROM categories")
    if c.fetchone()[0] == 0:
        categories = [
            (1, 'Breakfast', '6-11'),
            (2, 'Lunch', '11-16'),
            (3, 'Dinner', '16-22'),
            (4, 'All Day', '6-22'),
            (5, 'Bakery', '6-22')
        ]
        c.executemany("INSERT INTO categories (id, name, time_range) VALUES (?, ?, ?)", categories)

        menu_items = [
            ('Avocado Toast', 'Sourdough bread with smashed avocado, cherry tomatoes, and feta', 850.00, 1, 1, 0, 0),
            ('Pancake Stack', 'Fluffy pancakes with maple syrup and fresh berries', 750.00, 1, 1, 0, 0),
            ('Eggs Benedict', 'English muffin with poached eggs, ham, and hollandaise', 950.00, 1, 0, 0, 0),
            ('Breakfast Burrito', 'Scrambled eggs, black beans, cheese, and salsa in a tortilla', 800.00, 1, 0, 0, 0),
            ('Caesar Salad', 'Romaine lettuce, croutons, parmesan, and Caesar dressing', 900.00, 2, 0, 0, 0),
            ('Veggie Burger', 'House-made patty with lettuce, tomato, and special sauce', 1050.00, 2, 1, 0, 0),
            ('Chicken Panini', 'Grilled chicken, mozzarella, and pesto on ciabatta', 1100.00, 2, 0, 0, 0),
            ('Margherita Pizza', 'Tomato sauce, fresh mozzarella, and basil', 1250.00, 2, 1, 0, 0),
            ('Pasta Carbonara', 'Spaghetti with creamy egg sauce, pancetta, and parmesan', 1400.00, 3, 0, 0, 0),
            ('Mushroom Risotto', 'Creamy arborio rice with wild mushrooms and herbs', 1350.00, 3, 1, 0, 0),
            ('Grilled Salmon', 'With roasted vegetables and lemon butter sauce', 1650.00, 3, 0, 0, 0),
            ('Beef Tenderloin', '8oz beef with mashed potatoes and red wine reduction', 1900.00, 3, 0, 0, 0),
            ('House Coffee', 'Freshly brewed coffee', 350.00, 4, 1, 1, 0),
            ('Iced Latte', 'Espresso with milk and ice', 450.00, 4, 1, 1, 0),
            ('Fresh Orange Juice', 'Cold-pressed orange juice', 400.00, 4, 1, 1, 0),
            ('Chocolate Cake', 'Rich chocolate cake with ganache', 650.00, 4, 1, 0, 1),
            ('Tiramisu', 'Classic Italian dessert with coffee flavor', 700.00, 4, 1, 0, 1),
            ('Topan Virtles', 'Traditional golden bundt cake ring sprinkled with powdered sugar and vanilla aroma', 650.00, 5, 1, 0, 1),
            ('Spâtues', 'Soft artisan brioche ring baked with sweet cherries and caramelized glaze', 750.00, 5, 1, 0, 1),
            ('Artisan Choux Ring', 'Fluted choux pastry ring filled with light vanilla bean cream and powdered sugar', 680.00, 5, 1, 0, 1),
            ('Gueke Tmes', 'Twisted cinnamon brioche wreath with delicate sugar glaze', 590.00, 5, 1, 0, 1),
            ('Saper Cluter', 'Almond-crusted fluted cake dusted with confectioners sugar', 720.00, 5, 1, 0, 1),
            ('Saper Coldes', 'Golden sponge ring with rich mascarpone filling and toasted crumb', 820.00, 5, 1, 0, 1),
            ('Signature Raspberry Cake Slice', 'Layers of moist vanilla sponge, wild raspberry compote, and light cream', 850.00, 5, 1, 0, 1)
        ]
        c.executemany("INSERT INTO menu_items (name, description, price, category_id, is_vegetarian, is_drink, is_dessert) VALUES (?, ?, ?, ?, ?, ?, ?)", menu_items)
        conn.commit()
    conn.close()

class UnifiedCursor:
    def __init__(self, raw_cursor, is_sqlite=False):
        self.raw_cursor = raw_cursor
        self.is_sqlite = is_sqlite

    def execute(self, sql, params=None):
        if self.is_sqlite and params:
            sql = sql.replace('%s', '?')
        if params is not None:
            return self.raw_cursor.execute(sql, params)
        return self.raw_cursor.execute(sql)

    def fetchall(self):
        rows = self.raw_cursor.fetchall()
        if self.is_sqlite:
            return [dict(row) for row in rows]
        return rows

    def fetchone(self):
        row = self.raw_cursor.fetchone()
        if self.is_sqlite and row:
            return dict(row)
        return row

    @property
    def lastrowid(self):
        return self.raw_cursor.lastrowid

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self.raw_cursor, 'close'):
            self.raw_cursor.close()

class UnifiedConnection:
    def __init__(self, raw_conn, is_sqlite=False):
        self.raw_conn = raw_conn
        self.is_sqlite = is_sqlite

    def cursor(self):
        return UnifiedCursor(self.raw_conn.cursor(), is_sqlite=self.is_sqlite)

    def commit(self):
        self.raw_conn.commit()

    def close(self):
        self.raw_conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def get_db_connection():
    # If explicitly configured to use SQLite
    if os.environ.get("USE_SQLITE", "").lower() in ["true", "1"]:
        seed_sqlite_database()
        s_conn = sqlite3.connect(SQLITE_DB_PATH)
        s_conn.row_factory = sqlite3.Row
        return UnifiedConnection(s_conn, is_sqlite=True)

    # Database configuration for Remote or Local MySQL
    db_url = os.environ.get("DATABASE_URL")
    if db_url and (db_url.startswith("mysql://") or db_url.startswith("mysql+pymysql://")):
        url = urlparse(db_url)
        mysql_conf = {
            'host': url.hostname or 'localhost',
            'user': url.username or 'root',
            'password': url.password or '',
            'database': url.path.lstrip('/') or 'latte_lounge_caffe',
            'port': int(url.port or 3306),
            'cursorclass': pymysql.cursors.DictCursor,
            'connect_timeout': 3
        }
    else:
        mysql_conf = {
            'host': os.environ.get('DB_HOST', 'localhost'),
            'user': os.environ.get('DB_USER', 'root'),
            'password': os.environ.get('DB_PASSWORD', ''),
            'database': os.environ.get('DB_NAME', 'latte_lounge_caffe'),
            'port': int(os.environ.get('DB_PORT', 3306)),
            'cursorclass': pymysql.cursors.DictCursor,
            'connect_timeout': 3
        }

    try:
        raw_conn = pymysql.connect(**mysql_conf)
        return UnifiedConnection(raw_conn, is_sqlite=False)
    except Exception:
        # Fall back to automated SQLite if MySQL server is offline or in cloud container
        seed_sqlite_database()
        s_conn = sqlite3.connect(SQLITE_DB_PATH)
        s_conn.row_factory = sqlite3.Row
        return UnifiedConnection(s_conn, is_sqlite=True)

# Initialize session variables
def init_session():
    session['order_in_progress'] = True
    session['checkout_step'] = None  # Tracks checkout stage: None, 'order_type', 'address', 'payment'
    session['current_items'] = []
    session['order_type'] = None
    session['delivery_address'] = None
    session['payment_method'] = None
    session['customer_name'] = 'Guest'

# Get current menu based on time
def get_current_menu():
    current_hour = datetime.now().hour
    conn = get_db_connection()   
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT c.name as category, m.id, m.name, m.description, m.price,
                       m.is_vegetarian, m.is_drink, m.is_dessert
                FROM menu_items m
                JOIN categories c ON m.category_id = c.id
                WHERE 
                    (c.time_range = '6-22') OR
                    (c.time_range = '6-11' AND 6 <= %s AND %s < 11) OR
                    (c.time_range = '11-16' AND 11 <= %s AND %s < 16) OR
                    (c.time_range = '16-22' AND 16 <= %s AND %s < 22)
                ORDER BY c.id, m.name
            """, (current_hour, current_hour, current_hour, current_hour, current_hour, current_hour))
            return cursor.fetchall()
    finally:
        conn.close()

# Customer query analytics and logging function
def log_unknown_query(user_input):
    """
    Connects to the database and logs unrecognized customer inquiries into the 'unknown_queries'
    table for ongoing service optimization.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO unknown_queries (`query`)
                VALUES (%s)
            """, (user_input,))
            conn.commit()
    except Exception as e:
        print(f"[Query Analytics] Failed to log query: {e}")
    finally:
        if conn:
            conn.close()

# Helper function: Tokenization, Sanitization, and Fuzzy String Matching using difflib.get_close_matches
def extract_menu_items(user_text, menu_items):
    """
    NLP Tokenization, Sanitization, and Fuzzy Matching:
    - Strips punctuation and extraneous whitespace.
    - Tokenizes sanitized input into discrete word tokens.
    - Employs difflib.get_close_matches to catch misspellings and typos (e.g., 'late' -> 'latte', 'expresso' -> 'espresso').
    - Resolves both multi-word exact matches and single-token typo variants.
    """
    # 1. Sanitization: Strip punctuation and collapse redundant whitespace
    clean_text = re.sub(r'[^\w\s]', ' ', user_text.lower())
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # 2. Tokenization: Extract word tokens
    tokens = clean_text.split()
    
    # Stop words to exclude from fuzzy token matching
    stop_words = {'the', 'and', 'for', 'with', 'all', 'day', 'house', 'stack', 'fresh', 'slice',
                  'order', 'please', 'like', 'want', 'some', 'get', 'give', 'have', 'an', 'a',
                  'would', 'see', 'whats', 'what', 'on', 'menu', 'is', 'can', 'could', 'id'}

    # Build vocabulary mapping (keys -> menu item dict)
    vocab_map = {}
    for item in menu_items:
        name_clean = item['name'].lower()
        vocab_map[name_clean] = item
        
        # Index key descriptive words in the item name
        keywords = re.findall(r'\b[a-z0-9]+\b', name_clean)
        for kw in keywords:
            if kw not in stop_words and len(kw) >= 3:
                vocab_map[kw] = item

    # Register common customer synonyms / aliases
    for item in menu_items:
        lower_name = item['name'].lower()
        if 'latte' in lower_name:
            vocab_map['latte'] = item
            vocab_map['espresso'] = item  # maps typo 'expresso' via fuzzy match
        elif 'coffee' in lower_name:
            vocab_map['coffee'] = item
        elif 'pancake' in lower_name:
            vocab_map['pancake'] = item
            vocab_map['pancakes'] = item
        elif 'burger' in lower_name:
            vocab_map['burger'] = item
            vocab_map['veggie'] = item
        elif 'virtles' in lower_name or 'topan' in lower_name:
            vocab_map['virtles'] = item
            vocab_map['topan'] = item
        elif 'spatues' in lower_name or 'spâtues' in lower_name:
            vocab_map['spatues'] = item
            vocab_map['spâtues'] = item
        elif 'choux' in lower_name:
            vocab_map['choux'] = item
        elif 'gueke' in lower_name:
            vocab_map['gueke'] = item
        elif 'cluter' in lower_name:
            vocab_map['cluter'] = item
        elif 'coldes' in lower_name:
            vocab_map['coldes'] = item
        elif 'raspberry' in lower_name:
            vocab_map['raspberry'] = item
            vocab_map['raspberry cake'] = item

    matched = []

    # A. Check exact phrase containment first (multi-word item names)
    for phrase, item in vocab_map.items():
        if f" {phrase} " in f" {clean_text} ":
            if item not in matched:
                matched.append(item)

    # B. Token-level fuzzy string matching with difflib.get_close_matches (Typo tolerance)
    vocabulary_keys = list(vocab_map.keys())
    for token in tokens:
        if token in stop_words or len(token) < 3:
            continue
        
        # Use difflib.get_close_matches to handle typos (e.g., 'late' -> 'latte', 'expresso' -> 'espresso')
        close_matches = difflib.get_close_matches(token, vocabulary_keys, n=1, cutoff=0.75)
        if close_matches:
            matched_item = vocab_map[close_matches[0]]
            if matched_item not in matched:
                matched.append(matched_item)

    return matched

# Process natural language input (NLP & Dialog Flow Engine)
def process_natural_input(user_input, menu_items):
    """
    Natural Language Dialog Management Engine:
    - Step 1: Sanitization & Tokenization: Strips punctuation and normalizes spacing.
    - Step 2: Complex Sentence Item Extraction: Uses fuzzy matching (difflib.get_close_matches)
              to capture items within complex sentences (e.g., "I'd like to place an order for a latte").
    - Step 3: Regex-based Intent Recognition: Classifies user intents across complex sentence
              structures (e.g., "I would like to see what's on the menu please").
    - Step 4: Fallback & Knowledge Logging: Logs unknown queries for menu optimization.
    """
    # 1. Sanitization & Tokenization
    sanitized_input = re.sub(r'[^\w\s]', ' ', user_input.lower())
    clean_input = re.sub(r'\s+', ' ', sanitized_input).strip()
    
    # Priority 1: Complex sentences ordering specific items (with typo tolerance via difflib.get_close_matches)
    selected_items = extract_menu_items(user_input, menu_items)
    if selected_items:
        return process_item_selection(selected_items)
    
    # Priority 2: Viewing Menu Intent (handles complex phrasing like "I would like to see what's on the menu please")
    if re.search(r'\b(menu|what(?:\'s|\s+is)\s+on\s+the\s+menu|catalog|food\s+list|options|what\s+do\s+you\s+have|show\s+(?:me\s+)?(?:the\s+)?menu|available\s+items)\b', clean_input):
        return suggest_menu(menu_items)

    # Priority 3: Greetings Intent (handling typos like 'helo' and friendly greetings)
    if re.search(r'\b(hello|helo|hi|hey|howdy|greetings|good\s*(morning|afternoon|evening))\b', clean_input):
        return {'response': random.choice([
            "Hello! Welcome to Latte Lounge Caffe. How can I help you today?",
            "Hi there! Ready to explore our delicious menu or order some fresh treats?"
        ])}

    # Priority 4: General Order Intent (when no specific item was named)
    if re.search(r'\b(place\s+an\s+order|order\s+food|want\s+to\s+order|how\s+to\s+order)\b', clean_input):
        return suggest_menu(menu_items, "We'd love to take your order! Here is what's fresh on our menu right now:")
        
    # Priority 5: Table Reservation Intent
    if re.search(r'\b(reserv(e|ation|ing)?|book(ing)?(\s+a)?\s+table|table\s+for)\b', clean_input):
        return {'response': "We'd love to host you! To reserve a table, please let us know your date, time, and party size (e.g., 'Table for 2 tonight at 7 PM'), or call us directly at (555) 019-2834."}

    # Priority 6: Loyalty Points / Rewards Intent
    if re.search(r'\b(loyalty|points?|rewards?|membership|balance)\b', clean_input):
        return {'response': "Latte Lounge Rewards: You earn 10 points for every LKR 100 spent! Every 100 points unlocks a free specialty drink or bakery item. Provide your phone number at checkout to accumulate points."}

    # Priority 7: Dietary Preference Intent - Vegetarian
    if re.search(r'\b(vegetar(ian)?|veggie|plant[- ]based|vegan)\b', clean_input):
        veg_items = [item for item in menu_items if item.get('is_vegetarian')]
        return suggest_menu(veg_items, "Here are our delicious vegetarian options:")
        
    # Priority 8: Category Intent - Drinks / Coffee
    if re.search(r'\b(drinks?|beverage(s)?|coffee|tea|juice)\b', clean_input):
        drink_items = [item for item in menu_items if item.get('is_drink')]
        return suggest_menu(drink_items, "Here are our handcrafted drinks and coffees:")
        
    # Priority 9: Category Intent - Bakery, Pastries & Desserts
    if re.search(r'\b(baker(y|ies)?|pastr(y|ies)|cakes?|dessert(s)?|sweet(s)?|croissant|donut|doughnut|brioche|bundt|bun|tiramisu|bakes?)\b', clean_input):
        bakery_items = [item for item in menu_items if (item.get('category') == 'Bakery' or item.get('is_dessert'))]
        return suggest_menu(bakery_items, "Here are our freshly baked artisan pastries and sweet bakery treats:")

    # Priority 10: Location / Map Feature
    location_keywords = ['location', 'address', 'where', 'map', 'place']
    if any(kw in clean_input for kw in location_keywords) and 'order' not in clean_input:
        map_iframe = (
            '<div style="margin-top: 8px; border-radius: 12px; overflow: hidden; border: 1px solid #ebdcd0; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">'
            '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d15843.076865231264!2d79.8407425!3d6.9344444!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3ae2592477f1e7d3%3A0x6b5a3eb17c6031f0!2sColombo%20Fort%2C%20Colombo!5e0!3m2!1sen!2slk!4v1700000000000!5m2!1sen!2slk" '
            'width="100%" height="200" style="border:0; display:block;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
            '</div>'
        )
        return {
            'response': f"Latte Lounge Café is located in <strong>Colombo Fort, Sri Lanka</strong>! 📍 Pop in for freshly brewed artisan coffee, cozy vibes, and delicious treats.<br>{map_iframe}"
        }

    # Priority 11: Polite Gratitude / Closing Intent
    if re.search(r'\b(thank(s|\s+you)?|appreciate|cheers|bye|goodbye)\b', clean_input):
        return {'response': "You're most welcome! Let me know if you would like anything else from Latte Lounge."}

    # Final Fallback: Query logging & smart barista concierge fallback
    log_unknown_query(user_input)

    try:
        if gemini_model:
            external_res = gemini_model.generate_content(user_input)
            if external_res and external_res.text:
                return {'response': external_res.text.strip()}
        elif genai and GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY":
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction="Act as a helpful barista at Latte Lounge Cafe in Sri Lanka."
            )
            external_res = model.generate_content(user_input)
            if external_res and external_res.text:
                return {'response': external_res.text.strip()}
    except Exception as e:
        print(f"[Service Fallback Notice] {e}")

    return {'response': "Sorry, I didn't catch that. Would you like to see our menu?"}

# Suggest menu items to user
def suggest_menu(items, message="Here's what we have available:"):
    if not items:
        return {'response': "Sorry, we don't have any items matching your request."}
    
    response = message + "\n"
    for item in items:
        response += f"- {item['name']} (LKR {float(item['price']):.2f}): {item['description']}\n"
    
    response += "\nYou can say the name of any item to add it to your order."
    return {'response': response}

# Process item selection
def process_item_selection(items):
    """
    Processes recognized menu items, updates the session order cart,
    and returns a structured receipt summary with running total.
    """
    if not session.get('current_items'):
        session['current_items'] = []
    
    for item in items:
        session['current_items'].append(item)
    
    # Calculate running order total
    running_total = sum(float(i['price']) for i in session['current_items'])
    
    # Format newly added items
    added_names = ", ".join([f"{item['name']} (LKR {float(item['price']):.2f})" for item in items])
    
    response_msg = (
        f"I've added {added_names} to your order!\n"
        f"Current Order Total: LKR {running_total:.2f}\n"
        f"Would you like to add anything else, or type 'checkout' (or choose 'delivery'/'pickup') to complete your order?"
    )
    
    return {
        'response': response_msg,
        'items': session['current_items']
    }

# Process order type (delivery/pickup)
def process_order_type(user_input):
    clean_input = user_input.lower().strip()
    
    if 'delivery' in clean_input:
        session['order_type'] = 'delivery'
        session['checkout_step'] = 'address'
        return {'response': "Great! We'll deliver your order. What's your delivery address?"}
    elif 'pickup' in clean_input or 'collect' in clean_input:
        session['order_type'] = 'pickup'
        session['checkout_step'] = 'payment'
        return {'response': "Got it! Your order will be ready for pickup. How would you like to pay - cash or card?"}
    elif re.search(r'\b(check\s*out|my\s+order|order\s+checkout|place\s+order)\b', clean_input):
        return {'response': "I've got your order ready to go! To finalize your checkout, please let me know: will you be picking this up, or do you need delivery?"}
    else:
        return {'response': "Sorry, I didn't catch that. Would you like delivery or pickup?"}

# Process delivery address
def process_delivery_address(user_input):
    session['delivery_address'] = user_input
    session['checkout_step'] = 'payment'
    return {'response': "Thanks! We'll deliver to that address. How would you like to pay - cash or card?"}

# Process payment method
def process_payment_method(user_input):
    user_input = user_input.lower()
    
    if 'cash' in user_input:
        session['payment_method'] = 'cash'
    elif 'card' in user_input or 'credit' in user_input or 'debit' in user_input:
        session['payment_method'] = 'card'
    else:
        return {'response': "Sorry, I didn't catch that. Would you like to pay with cash or card?"}
    
    session['checkout_step'] = None
    return confirm_order()

# Confirm order and save to database
def confirm_order():
    if not session.get('current_items'):
        return {'response': "Your order is empty. Please add some items before confirming."}
    
    # Consolidate items to calculate accurate quantities and line item totals
    item_map = {}
    for item in session['current_items']:
        name = item.get('name', 'Artisan Coffee')
        qty = item.get('quantity', 1)
        price = float(item.get('price', 0.0))
        if name in item_map:
            item_map[name]['quantity'] += qty
        else:
            item_map[name] = {
                'id': item.get('id'),
                'name': name,
                'price': price,
                'quantity': qty
            }
    
    # Calculate order total
    total = sum(item['price'] * item['quantity'] for item in item_map.values())
    
    # Extract and format customer & checkout details
    customer_name = session.get('customer_name') or 'Guest'
    order_type_raw = session.get('order_type') or 'pickup'
    order_type = order_type_raw.capitalize()
    payment_method_raw = session.get('payment_method') or 'cash'
    payment_method = payment_method_raw.capitalize()
    delivery_address = session.get('delivery_address')
    
    # Save to database
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Insert order record
            cursor.execute("""
                INSERT INTO orders (customer_name, order_type, delivery_address, payment_method, total_amount)
                VALUES (%s, %s, %s, %s, %s)
            """, (customer_name, order_type_raw.lower(), delivery_address, payment_method_raw.lower(), total))
            order_id = cursor.lastrowid
            
            # Insert consolidated order items
            for item in item_map.values():
                cursor.execute("""
                    INSERT INTO order_items (order_id, menu_item_id, quantity)
                    VALUES (%s, %s, %s)
                """, (order_id, item.get('id') if isinstance(item.get('id'), int) else 1, item['quantity']))
            
            conn.commit()
    except Exception as e:
        print(f"[Order DB Error] Failed to persist order: {e}")
    finally:
        if conn:
            conn.close()
            
    # Format items list: - {name} x {quantity} (LKR {price:.2f})
    items_list = "\n".join([
        f"- {item['name']} x {item['quantity']} (LKR {item['price']:.2f})"
        for item in item_map.values()
    ])
    
    # Conditional delivery/pickup status message and address line
    if order_type_raw.lower() == 'delivery':
        address_line = f"Delivery address: {delivery_address}\n" if delivery_address else ""
        status_msg = "Your order is being prepared and will be delivered soon!"
    else:
        address_line = ""
        status_msg = "Your order will be ready for pickup in 10–15 minutes!"
        
    # Structured receipt confirmation
    confirmation = (
        f"Thank you for your order, {customer_name}! Here's your confirmation:\n\n"
        f"Items:\n"
        f"{items_list}\n\n"
        f"Total: LKR {total:.2f}\n"
        f"Order type: {order_type}\n"
        f"{address_line}"
        f"Payment method: {payment_method}\n\n"
        f"{status_msg}"
    )
    
    # Clear session after completing order
    init_session()
    
    return {'response': confirmation, 'order_complete': True}

# Flask routes
@app.route('/')
def home():
    init_session()
    return render_template('index.html')

@app.route('/bakery')
def bakery():
    if 'current_items' not in session:
        init_session()
    return render_template('bakery.html')

@app.route('/api/cart', methods=['GET', 'POST', 'DELETE'])
def manage_cart():
    if 'current_items' not in session:
        init_session()
        
    if request.method == 'GET':
        items = session.get('current_items', [])
        total = round(sum(item['price'] for item in items), 2)
        return jsonify({'items': items, 'total': total, 'count': len(items)})
        
    elif request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        item_name = data.get('name')
        price = data.get('price')
        item_id = data.get('id')
        
        # If item_name given, lookup in database if price not provided
        if item_name and not price:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, name, price FROM menu_items WHERE name LIKE %s LIMIT 1", (f"%{item_name}%",))
                    row = cursor.fetchone()
                    if row:
                        item_id = row['id']
                        item_name = row['name']
                        price = float(row['price'])
                    else:
                        price = 450.00
            finally:
                conn.close()
        elif price:
            price = float(price)
            
        new_item = {
            'id': int(item_id) if item_id else random.randint(100, 999),
            'name': item_name or 'Artisan Coffee',
            'price': float(price) if price else 450.00
        }
        items = session.get('current_items', [])
        items.append(new_item)
        session['current_items'] = items
        session.modified = True
        total = round(sum(it['price'] for it in items), 2)
        return jsonify({'success': True, 'item': new_item, 'items': items, 'total': total, 'count': len(items)})
        
    elif request.method == 'DELETE':
        session['current_items'] = []
        session.modified = True
        return jsonify({'success': True, 'items': [], 'total': 0.0, 'count': 0})


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form.get('user_input', '').strip()
    if not user_input:
        return jsonify({'response': "Please type a message or select a suggestion chip."})
    
    menu_items = get_current_menu()
    
    # 1. Active checkout state machine flow
    checkout_step = session.get('checkout_step')
    if checkout_step == 'order_type':
        return jsonify(process_order_type(user_input))
    elif checkout_step == 'address':
        return jsonify(process_delivery_address(user_input))
    elif checkout_step == 'payment':
        return jsonify(process_payment_method(user_input))
        
    # 2. Checkout trigger if order items already exist
    clean_lower = user_input.lower()
    if session.get('current_items') and any(w in clean_lower for w in ['checkout', 'confirm order', 'finish order', 'done']):
        session['checkout_step'] = 'order_type'
        return jsonify({'response': "Ready to checkout! Would you like your order for delivery or pickup?"})
        
    if session.get('current_items') and ('delivery' in clean_lower or 'pickup' in clean_lower):
        return jsonify(process_order_type(user_input))

    # 3. Conversational Natural Language Processing & Inference
    return jsonify(process_natural_input(user_input, menu_items))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)