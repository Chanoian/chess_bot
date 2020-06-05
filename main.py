import berserk
from flask import Flask, request, make_response, json


with open('./lichess.token') as f:
    token = f.read()

session = berserk.TokenSession(token)
client = berserk.Client(session)
app = Flask(__name__)


@app.route('/')
def helloWorld():
    return 'Hello, World'


@app.route('/api/v1/assistant', methods=['POST'])
def mainAssistant():
    req = request.get_json()
    if req["queryResult"]["action"] == "CreateGame":
        return createChallengeAI()
    # elif req["queryResult"]["action"] == "MakeMove":
    #     return movePiece()


def createChallengeAI():
    response = client.challenges.create_ai()
    game_id = response['id']
    return_to_dialogflow = {
        "fulfillmentMessages": [
            {
            "text": {
                "text": ["Text response from webhook"]
                }
            }
        ]
    }
    res = json.dumps(return_to_dialogflow, indent=4)
    r = make_response(res)
    return r


# def movePiece():
#     client.board.make_move(game_id=GAME_ID, move='e2e4')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)