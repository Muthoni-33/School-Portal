import os
from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# DevOps Injection Hooks (Reads from runtime environment variables)
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "auth_db")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")

def get_db_connection():
    """Helper method executing the backend-to-database connection hook."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Secure query executing parameters separation
        cur.execute("SELECT id, role FROM users WHERE username = %s AND password = %s;", (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user:
            return jsonify({
                "status": "authenticated",
                "user_id": user[0],
                "role": user[1],
                "token": "mock-jwt-token-xyz" # Token logic layer placeholder
            }), 200
        return jsonify({"error": "Invalid username or password"}), 401
        
    except Exception as e:
        return jsonify({"error": f"Database communication failure: {str(e)}"}), 500

@app.route('/healthz', methods=['GET'])
def health_check():
    """Infrastructure Liveness/Readiness diagnostic hook."""
    return jsonify({"status": "healthy", "service": "auth-service"}), 200

if __name__ == '__main__':
    # Local fallback execution thread (Production will pass via Gunicorn)
    app.run(host='0.0.0.0', port=5001)
