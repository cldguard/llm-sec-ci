from flask import Flask, request, jsonify, abort
import os

app = Flask(__name__)

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    if not request.is_json:
        abort(400, description="Expected application/json")
    body = request.get_json(silent=True) or {}
    messages = body.get("messages", [])
    prompt = messages[-1].get("content") if messages else ""
    # Keep the same deterministic mock behavior
    return jsonify({
        "id": "chatcmpl-mock",
        "object": "chat.completion",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant",
                        "content": "MOCK-LLM: safe deterministic reply. (Prompt length: %d)" % len(str(prompt))},
            "finish_reason": "stop"
        }],
        "model": body.get("model", "mock-llm")
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    # Bind to localhost by default to avoid exposing the service unintentionally.
    # Allow override via env var for controlled environments.
    host = os.environ.get('FLASK_BIND_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_BIND_PORT', '8000'))
    app.run(host=host, port=port)
