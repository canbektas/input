import json

import requests
import xmltodict
from requests.auth import HTTPBasicAuth

from src.utils.errors import BlupointError


def parse_iha_response(string):
    o = xmltodict.parse(string)
    o = o['rss']['channel']['item'][0]
    return json.dumps(o)


def parse_aa_response(string):
    o = json.loads(json.dumps(xmltodict.parse(string)))
    o = o['newsMessage']['itemSet']['newsItem']['contentSet']['inlineXML']['nitf']['body']
    r = {
        'headline': o['body.head']['headline']['hl1'],
        'byline': o['body.head']['byline']['byttl'],
        'abstract': o['body.head']['abstract'],
        'content': o['body.content']
    }

    return json.dumps(r)


def prepare_iha_url(agency, body):
    url = body['input_url'] + '&{}={}&{}={}'.format(
        agency['auth_credential_parameters']['username'],
        body['username'],
        agency['auth_credential_parameters']['password'],
        body['password']
    )

    response = requests.get(url)
    if response.status_code != 200:
        raise BlupointError(
            err_msg="Agency Rss did not return 200",
            err_code="errors.InvalidUsage",
            status_code=response.status_code
        )

    response_json = parse_iha_response(response.text)

    return response_json


def prepare_aa_url(agency, body):
    url = body['input_url'] + '/abone/search'

    data = {
        'end_data': 'NOW',
        'filter_language': 1
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
    }

    response = requests.post(url, data=data, headers=headers, auth=HTTPBasicAuth(body['username'], body['password']))

    if response.status_code != 200:
        raise BlupointError(
            err_msg="Agency rss did not return 200",
            err_code="errors.InvalidUsage",
            status_code=response.status_code
        )

    feeds_json = json.loads(response.text)
    items = feeds_json['data']['result']

    text_news = []

    for item in items:
        if item['type'] == 'text':
            text_news.append(item)

    detail_url = body['input_url'] + '/abone/document/' + text_news[0]['id'] + '/newsml29'
    response = requests.get(detail_url, headers=headers, auth=HTTPBasicAuth(body['username'], body['password']))

    if response.status_code != 200:
        raise BlupointError(
            err_code="errors.InvalidUsage",
            err_msg="Agency news response is not 200",
            status_code=response.status_code
        )

    response_json = parse_aa_response(response.text)

    return response_json


def prepare_dha_url(agency, body):
    pass


def prepare_reuters_url(agency, body):
    pass
