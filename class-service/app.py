import os
from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "classes_db")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

@app.route('/api/v1/classes', methods=['GET'])
def get_classes():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, course_name, instructor, schedule FROM classes;")
        rows = cur.fetchall()
        
        classes_list = []
        for row in rows:
            classes_list.append({
                "id": row[0],
                "course_name": row[1],
                "instructor": row[2],
                "schedule": row[3]
            })
            
        cur.close()
        conn.close()
        return jsonify({"classes": classes_list}), 200
        
    except Exception as e:
        return jsonify({"error": f"Database communication failure: {str(e)}"}), 500

@app.route('/healthz', methods=['GET'])
def health_check():
    """Infrastructure Liveness/Readiness diagnostic hook."""
    return jsonify({"status": "healthy", "service": "classes-service"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
