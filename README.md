# Latte Lounge Café & Digital Barista Chatbot

A production-ready Flask web application featuring a coffee shop landing page, an artisan Bakery storefront, an interactive shopping basket, and an intelligent digital barista dialog bot.

---

## 💻 Local Development Setup (XAMPP & MySQL)

### Prerequisites
- Python 3.8+
- XAMPP (for Apache & MySQL)

### Local Steps
1. Start the MySQL module in the XAMPP Control Panel.
2. Open phpMyAdmin (`http://localhost/phpmyadmin`), create a database named `latte_lounge_caffe`.
3. Import `database/schema.sql`, then import `database/sampledata.sql`.
4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Launch the application:
   ```bash
   python app.py
   ```
6. Open your browser at `http://localhost:5000`.

---

## ☕ Key Features
- **Artisan Coffee & Bakery Menu**: Over 24 items with real-time pricing in Sri Lankan Rupees (LKR).
- **Interactive Shopping Cart**: Add, view, update, and order items.
- **Natural Language Dialog Barista**: Intelligent order processing, recommendation engine, location maps with embedded Google Maps, and checkout state machine.
- **Zero-Failure Architecture**: Automatic fallback between MySQL and embedded SQLite.
