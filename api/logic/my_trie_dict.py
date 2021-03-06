import pytrie
import rethinkdb
from .my_translate import translate
import re
import os


class TrieDictWrapper:
    def __init__(self):
        self.trie = None
        self.d = {}

    def init_trie(self):
        """Initialize trie with current data in geodata table"""
        rethink_conn = rethinkdb.connect(db='hotel_cosmos', host=os.environ['RETHINK_IP'], port=28015, user="admin",
                                         password=os.environ['RETHINK_PASS'])
        geodata = list(rethinkdb.table('geodata').run(rethink_conn))

        for row in geodata:
            reverse_hotel_key = ''
            if row['type'] == 'hotel':
                name = re.sub(r'hotel','', row['name'].lower(), re.IGNORECASE)
                key = translate(name + ' ' + row['city'].lower())
                reverse_hotel_key = translate(row['city'].lower() + ' ' + name)
            elif row['type'] == 'zip':
                key = translate(row['name'].lower() + ' ' + row['city'].lower())
            elif row['type'] == 'city':
                key = translate(row['name'].lower() + ' ' + row['country'].lower())
            elif row['type'] == 'street':
                key = translate(row['name'].lower())

            if key not in self.d:
                # remove unneeded data
                key = re.sub('\s+', '', key)
                row.pop('id', None)
                row.pop('timeStampAdded', None)

                if row['type'] != 'zip':
                    row.pop('country', None)

                row.pop('index_country', None)
                self.d[key] = row

            if reverse_hotel_key != '':
                if reverse_hotel_key not in self.d:
                    reverse_hotel_key = re.sub('\s+', '', reverse_hotel_key)
                    # remove unneeded data
                    row.pop('id', None)
                    row.pop('timeStampAdded', None)
                    row.pop('country', None)
                    row.pop('index_country', None)
                    self.d[reverse_hotel_key] = row

        self.trie = pytrie.StringTrie(self.d)

        # delete dictionary
        self.d.clear()
        del self.d

        # close connection to rethinkdb
        rethink_conn.close()

    def _hotel_city_key(self, city, hotel):
        hotel = re.sub(city, '', hotel)
        return city + hotel

    def add_to_trie(self, d):
        """Add new item to trie"""

        for key, val in d.items():
            self.trie.__setitem__(key, val)
            print(key, val)

    def get_items(self, search):
        if len(search) < 3:
            return []

        if search == '':
            return []

        search = re.sub('\s+', '', search).lower()

        items = self.trie.items(prefix=search)

        # sort results
        cities = list(filter(lambda x: True if x[1]['type'] == 'city' else False, items))
        others = list(filter(lambda x: True if x[1]['type'] != 'city' else False, items))
        cities.sort(key=lambda x: len(x[1]['name']))
        print(cities)

        cities_filtered = {}

        for city in cities:
            if city[0] not in cities_filtered:
                cities_filtered[city[0]] = city

        print(cities_filtered.values())

        return [item[1] for item in cities_filtered.values()] + [item[1] for item in others][:15]
