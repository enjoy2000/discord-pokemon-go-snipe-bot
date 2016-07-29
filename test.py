# Test script to get pokemon names regex

import json

with open('data/pokemons.json') as data:
    pokemons = json.load(data)

regex = ''
for index, pokemon in enumerate(pokemons):
    regex += pokemon.get('Name', 'NA')
    regex += '|'
    regex += pokemon.get('Name', 'NA').lower()
    if index + 1 != len(pokemons):
        regex += '|'

print(regex) 
