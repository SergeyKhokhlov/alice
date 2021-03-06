from flask import Flask, request
import logging
import json
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

cities = {"москва": ["1521359/ee568aacac0a585e160e", "1533899/5f9762aa99b650768a94"],
          "париж": ["1030494/c41a8c36c18dd24a83df", "1030494/d9a02f42c58969d0737e"],
          "нью-йорк": ["213044/3a0d6543f2dbf23bda69", "997614/57180ce8c14b7f6dacac"]}

sessionStorage = {}


@app.route('/post', methods=["POST"])
def main():
    logging.info(f"Request: {request.json!r}")
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info(f"Response: {response!r}")
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = "Привет! Назови своё имя!"
        sessionStorage[user_id] = {
            'first_name': None
        }
        return
    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = "Не расслышала. Повтори, пожалуйста!"
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response']['text'] = "Приятно познакомиться, " + first_name.title() + \
                                      '. Я - Алиса. Какой город ты хочешь увидеть?'
            res['response']['buttons'] = [
                {'title:': city.title(),
                 'hide': True}
                for city in cities
            ]
    else:
        city = get_city(req)
        if city in cities:
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Этот город я знаю'
            res['response']['card']['image_id'] = random.choice(cities[city])
            res['response']['text'] = 'Я угадала!'
        else:
            res['response']['text'] = "Первый раз слышу об этом городе. Попробуй еще разок!"


def get_city(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('city', None)


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == "YANDEX.FIO":
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
