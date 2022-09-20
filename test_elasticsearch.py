from elasticsearch import Elasticsearch
from datetime import datetime

es = Elasticsearch('http://localhost:9200')
res = es.get(index='posts', id='xTMKRYMBmYhgqVP5siay')
print(res['_source'])

body = {
    'from': 0,
    'size': 0,
    'query': {
        'match': {
            'message': 'Buna'
        }
    }
}
res2 = es.search(index='posts', )