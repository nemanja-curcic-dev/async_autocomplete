# routes.py
from api.views.views import autocomplete, update_trie


def setup_routes(app):
    app.router.add_get('/hotel_cosmos/autocomplete',
                       autocomplete)
    app.router.add_post('/hotel_cosmos/update_trie',
                       update_trie)