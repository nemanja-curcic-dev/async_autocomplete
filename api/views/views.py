from aiohttp import web
import json
from ..logic.my_trie_dict import TrieDictWrapper

trie_dict_wrapper = TrieDictWrapper()
trie_dict_wrapper.init_trie()


async def autocomplete(request):
    resp_body = trie_dict_wrapper.get_items(request.query.get('q', ''))

    return web.Response(body=json.dumps(resp_body),
                        headers={'Content-Type': 'application/json',
                                 'Access-Control-Allow-Origin:': '*'},
                        status=200)


async def update_trie(request):
    resp = await request.json()
    print(resp)
    return web.Response(body=json.dumps({'updated': True}),
                        headers={'Content-Type': 'application/json'},
                        status=200)