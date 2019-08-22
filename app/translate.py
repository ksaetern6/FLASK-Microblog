import json
import requests
from flask_babel import _
from flask import current_app


##
# @name: translate
# @desc: takes in text to be translated with the source and destination language then
#   returns the translated string
##
def translate(text, source_language, dest_language):
    # check if theres a key for the translation api
    if 'MS_TRANSLATOR_KEY' not in current_app.config or \
            not current_app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')

    # authenticate with translator api service with key
    auth = {'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY']}

    # GET request to endpoint of translation api that returns a JSON paylaod
    r = requests.get('https://api.microsofttranslator.com/v2/Ajax.svc'
                     '/Translate?text={}&from={}&to={}'.format(
        text, source_language, dest_language),
        headers=auth)

    if r.status_code != 200:
        return _('Error: the translation service failed.')

    # decode JSON's content body into string.
    return json.loads(r.content.decode('utf-8-sig'))
