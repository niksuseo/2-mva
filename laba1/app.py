
import os
import time
from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "default")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8080"))


def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def init_db():
    for attempt in range(10):
        try:
            with connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS requests (
                            id SERIAL PRIMARY KEY,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
            return
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("Cannot connect to PostgreSQL")


@app.route("/api/v1/get", methods=["GET"])
def get_requests():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO requests DEFAULT VALUES")
            cur.execute(
                "SELECT id, created_at FROM requests ORDER BY id"
            )
            rows = cur.fetchall()

    return jsonify([
        {"id": row[0], "created_at": row[1].isoformat()}
        for row in rows
    ])


@app.route("/", methods=["GET"])
def home():
    return "Docker Lab 1: Application is running!"


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=SERVER_PORT)
