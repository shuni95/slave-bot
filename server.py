from flask import Flask, request

app = Flask(__name__)

@app.route('/messenger/webhook', methods=['GET'])
def handle_verification():
    return request.args['hub.challenge']

@app.route('/messenger/webhook', methods=['POST'])
def handle_incoming_requests():
    data = request.json
    messaging = data['entry'][0]['messaging'][0]
    chat_id = messaging['sender']['id']
    handler = BotHandler(chat_id)

    return handler.handle_bot(messaging)

if __name__ == '__main__':
    app.run(debug=True)
