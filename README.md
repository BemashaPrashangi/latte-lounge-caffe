# Latte Lounge Caffe Chatbot

A Flask-based chatbot for café ordering with MySQL database integration.

## Setup Instructions

### Prerequisites
- Python 3.6+
- XAMPP (for MySQL database)
- Flask (`pip install flask`)
- PyMySQL (`pip install pymysql`)

### Database Setup
1. Start XAMPP and launch MySQL server
2. Open phpMyAdmin (usually at http://localhost/phpmyadmin)
3. Create a new database named `latte_lounge_caffe`
4. Import the `database/schema.sql` file to create tables
5. Import the `database/sampledata.sql` file to populate sample data

### Running the Application
1. Clone this repository
2. Navigate to the project directory
3. Run the Flask application:
   ```bash
   python app.py


   