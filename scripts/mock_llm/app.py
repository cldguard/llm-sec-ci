from flask import Flask, request, jsonify
app = Flask(__name__)
@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    body = request.json or {}
    messages = body.get("messages", [])
    prompt = messages[-1].get("content") if messages else ""
    return jsonify({"id":"chatcmpl-mock","object":"chat.completion",
        "choices":[{"index":0,"message":{"role":"assistant","content":"MOCK-LLM: safe deterministic reply. (Prompt length: %d)" % len(str(prompt))},"finish_reason":"stop"}],
        "model": body.get("model","mock-llm")})
@app.route('/health', methods=['GET'])
def health(): return jsonify({"status":"ok"}), 200
if __name__ == '__main__': app.run(host='0.0.0.0', port=8000)