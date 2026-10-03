# Latte Lounge Café & Digital Barista Chatbot

A production-ready Flask web application featuring a coffee shop landing page, an artisan Bakery storefront, an interactive shopping basket, and an intelligent digital barista dialog bot.

---

## 🚀 Live Cloud Deployment Guide (Free 24/7 Hosting)

The application is pre-configured with **zero-setup dual database support**.
- When run locally with XAMPP, it automatically connects to your local MySQL database.
- When deployed to any cloud provider (Render, Railway, PythonAnywhere), it automatically falls back to an embedded database populated with all 24 menu items, categories, and full checkout persistence—**no paid or complex cloud database needed!**

---

### Option 1: Deploy to Render.com (Recommended - 100% Free & Fast)

Render hosts Flask web applications for free with an automated HTTPS URL (e.g., `https://latte-lounge.onrender.com`).

#### Step 1: Push your code to GitHub
1. Create a new repository on [GitHub](https://github.com/new) named `latte-lounge-caffe`.
2. In your terminal / command prompt, run:
   ```bash
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/latte-lounge-caffe.git
   git branch -M main
   git push -u origin main
   ```

#### Step 2: Create a Free Web Service on Render
1. Go to [Render.com](https://render.com/) and Sign Up / Log In with GitHub.
2. Click **New +** &rarr; **Web Service**.
3. Select **Build and deploy from a Git repository** and connect your `latte-lounge-caffe` repository.
4. Render will auto-detect the configuration:
   - **Name**: `latte-lounge-caffe` (or your preferred name)
   - **Region**: Oregon or Frankfurt
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`
5. Click **Deploy Web Service**.
6. In 1–2 minutes, Render will build your application and give you a permanent live public URL:
   `https://latte-lounge-caffe.onrender.com`

---

### Option 2: Deploy to PythonAnywhere.com (Free Native Python Hosting)

PythonAnywhere is specifically built for Python/Flask applications.

1. Sign up for a free beginner account at [PythonAnywhere.com](https://www.pythonanywhere.com/).
2. Open the **Bash Console** in your dashboard and clone your repository:
   ```bash
   git clone https://github.com/<YOUR_GITHUB_USERNAME>/latte-lounge-caffe.git
   cd latte-lounge-caffe
   pip install -r requirements.txt
   ```
3. Go to the **Web** tab in PythonAnywhere:
   - Click **Add a new web app** &rarr; select **Manual configuration** &rarr; **Python 3.10+**.
   - Set the **Source code** directory to: `/home/<your-username>/latte-lounge-caffe`
   - Click the **WSGI configuration file** link to edit it, replace its contents with:
     ```python
     import sys
     import os

     path = '/home/<your-username>/latte-lounge-caffe'
     if path not in sys.path:
         sys.path.insert(0, path)

     from app import app as application
     ```
   - Click **Save** and then click the green **Reload** button at the top of the Web tab.
4. Your website is instantly live at:
   `https://<your-username>.pythonanywhere.com`

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