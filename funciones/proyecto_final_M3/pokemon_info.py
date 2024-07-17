import pickle
from requests_html import HTMLSession
import unidecode

pokemon_stats = {
    'name': '',
    'current_health': 100,
    'base_health': 100,
    'level': 1,
    'type': None,
    'current_exp': 0,
    'attacks': None
}

URL_BASE = 'https://www.pokexperto.net/index2.php?seccion=nds/nationaldex/movimientos_nivel&pk='


# Buscar informacion de un pokemon en la URL
def get_pokemon(index):
    url = f'{URL_BASE}{index}'
    session = HTMLSession()

    # pokemon_stats es una plantilla y usamos un .copy para copiar la plantilla en un pokemon
    new_pokemon = pokemon_stats.copy()
    page = session.get(url)

    # NECESITAMOS INFORMACION DEL NOMBRE, TIPO Y ATAQUES

    # ---Buscar el nombre del pokemon
    new_pokemon['name'] = page.html.find('.mini', first=True).text.split('\n')[0]

    # ---Buscar el tipo de pokemon
    new_pokemon['type'] = []
    for img in page.html.find('.pkmain', first=True).find('.bordeambos', first=True).find('img'):
        new_pokemon['type'].append(img.attrs['alt'])

    # ---Buscar los ataques del pokemon
    new_pokemon['attacks'] = []
    for attack_item in page.html.find('.pkmain')[-1].find('tr .check3'):
        # creamos un diccionario de ataques que ira dentro del diccionario de new_pokemon
        attack = {
            'name_attack': attack_item.find('td', first=True).find('a', first=True).text,
            'type_attack': attack_item.find('td')[1].find('img', first=True).attrs['alt'],
            'min_level': attack_item.find('th', first=True).text,
            'damage': int(attack_item.find('td')[3].text.replace('--', '0'))
        }
        if attack['min_level'] == '':
            attack['min_level'] = attack_item.find('th')[-1].text

        new_pokemon['attacks'].append(attack)

    return new_pokemon


# Guardar en un archivo pkl todos los pokemon
def save_all_pokemons():
    try:  # Abrimos el archivo pkl
        # print('cargando los pokemons del archivo pkl')
        with open('pokefile.pkl', 'rb') as pokefile:
            all_pokemons = pickle.load(pokefile)

    except FileNotFoundError:  # cargamos todos los pokemons y los guardamos en un pkl
        print('accediendo a la pagina web de los pokemons')
        all_pokemons = []
        for num in range(151):
            all_pokemons.append(get_pokemon(num + 1))
            print(f'\r{num + 1}', end='')
        print('\n')
        # creamos el archivo pkl
        with open('pokefile.pkl', 'wb') as pokefile:
            pickle.dump(all_pokemons, pokefile)
    return all_pokemons


def elemental_pokemon_bonus_attack():
    return {
        'acero': {
            'strong': ['hielo', 'roca', 'hada'],
            'weak': ['fuego', 'agua', 'electrico', 'acero']
        },
        'agua': {
            'strong': ['fuego', 'roca', 'tierra'],
            'weak': ['agua', 'dragon', 'planta']
        },
        'bicho': {
            'strong': ['planta', 'psiquico', 'siniestro'],
            'weak': ['acero', 'fantasma', 'fuego', 'hada', 'lucha', 'volador', 'veneno']
        },
        'dragon': {
            'strong': ['dragon'],
            'weak': ['acero', 'hada']
        },
        'electrico': {
            'strong': ['agua', 'volador'],
            'weak': ['dragon', 'electrico', 'planta', 'tierra']
        },
        'fantasma': {
            'strong': ['fantasma', 'volador'],
            'weak': ['normal', 'siniestro']
        },
        'fuego': {
            'strong': ['acero', 'bicho', 'hielo', 'planta'],
            'weak': ['agua', 'dragon', 'fuego', 'roca']
        },
        'hada': {
            'strong': ['dragon', 'lucha', 'siniestro'],
            'weak': ['acero', 'fuego', 'veneno']
        },
        'hielo': {
            'strong': ['dragon', 'planta', 'tierra', 'volador'],
            'weak': ['acero', 'agua', 'fuego', 'hielo']
        },
        'lucha': {
            'strong': ['normal'],
            'weak': ['bicho', 'fantasma', 'hada', 'psiquico', 'veneno', 'volador']
        },
        'normal': {
            'strong': {'normal'},
            'weak': {'acero', 'fantasma', 'roca'}
        },
        'planta': {
            'strong': ['agua', 'roca', 'tierra'],
            'weak': ['acero', 'bicho', 'dragon', 'fuego', 'planta', 'veneno', 'volador']
        },
        'psiquico': {
            'strong': ['lucha', 'veneno'],
            'weak': ['acero', 'psiquico', 'siniestro']
        },
        'roca': {
            'strong': ['bicho', 'fuego', 'hielo', 'volador'],
            'weak': ['acero', 'lucha', 'tierra']
        },
        'siniestro': {
            'strong': ['fantasma', 'psiquico'],
            'weak': ['hada', 'lucha', 'siniestro']
        },
        'tierra': {
            'strong': ['acero', 'electrico', 'fuego', 'roca', 'veneno'],
            'weak': ['bicho', 'planta', 'volador']
        },
        'veneno': {
            'strong': ['hada', 'planta'],
            'weak': ['acero', 'fantasma', 'roca', 'tierra', 'veneno']
        },
        'volador': {
            'strong': ['bicho', 'lucha', 'planta'],
            'weak': ['acero', 'electrico', 'roca']
        }
    }
