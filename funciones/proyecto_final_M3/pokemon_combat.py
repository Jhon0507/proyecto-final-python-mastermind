import random
from time import sleep
from pokemon_info import save_all_pokemons, elemental_pokemon_bonus_attack
import os

list_level_attacks = []


def welcome():
    text = 'Bienvenido a este combate pokemon'.upper()
    print(text + '\n' + len(text) * '-')
    sleep(3)
    os.system('cls')
    print('Te enfrentaras a todos los pokemons y durante este\n'
          'tiempo podras utilizar pokeballs para capturar\n'
          'y pociones para curar a tu pokemon')
    sleep(5)
    os.system('cls')
    input('ANOTACIONES\n'
          '- Si tu pokemon pierde se eliminara de tu lista\n'
          '- Si capturas un pokemon se te añadira a tu inventario y podras usarlo\n'
          '- Tienes que escribir el nombre de los ataques con sus mayusculas y acentos\n'
          '- Tus ataques pueden infligir el doble de daño o solo la mitad, elige bien tu siguiente movimiento\n'
          '- Hay probabilidad de no capturar al pokemon o no recibir ninguna recompensa al ganar un combate\n'
          '- A medida que tu pokemon sube de nivel, este ira desbloqueando nuevos ataques\n'
          'press [ENTER]')
    os.system('cls')


# definir el perfil del jugador
def get_player_profile(list_pokemon):
    perfil_player = {'player_name': input('Escribe tu nombre: '),
                     'pokemon_inventory': [],
                     'combats': 0,
                     'pokeballs': {
                         'pokeball': 1,
                         'superball': 0,
                         'ultraball': 0,
                         'masterball': 0
                     },
                     'health_potion': 1}

    # me permite añadir 3 pokemons sin que estos no se repitan en la lista
    for a in range(1):
        pokemon_character = random.choice(list_pokemon)
        if pokemon_character not in perfil_player['pokemon_inventory']:
            perfil_player['pokemon_inventory'].append(pokemon_character)

    return perfil_player


# es una condicion de True y False que se cumple mientras toda la vida los pokemons sea mayor a 0
def any_player_pokemon_lives(player_profile):
    # Se suman todas las vidas de nuestros pokemons
    return sum([health_pokemon['current_health'] for health_pokemon in player_profile['pokemon_inventory']]) > 0


# te muestra las opciones que puedes realizar, es un bucle que no acaba hasta que uno de los 2 gane
def fight(player_profile, enemy_pokemon):
    print('--- NUEVO COMBATE ---')

    attack_history = []

    player_pokemon = choose_pokemon(player_profile)
    os.system('cls')

    print(f'\nNOMBRE | NIVEL | VIDA | TIPO                NOMBRE | NIVEL | VIDA | TIPO\n'
          f'{get_pokemon_info(player_pokemon)}     VS     {get_pokemon_info(enemy_pokemon)}')

    print(show_inventory_items(player_profile))
    sleep(1)

    # bucle que seguira mientras la vida de los 2 pokemons sea mayor que 0
    while any_player_pokemon_lives(player_profile) and enemy_pokemon['current_health'] > 0:
        action = None
        # bucle para elegir una de las 4 opciones de accion
        while action not in ['a', 'b', 'c', 'd']:
            action = input('Elige una opcion:\na. Atacar\nb. Pokeball\nc. Pocion de vida\nd. cambiar\n-->')
            print('\n')

            if action == 'a':
                enemy_pokemon['current_health'] = player_attack(player_pokemon, enemy_pokemon)
                attack_history.append(player_pokemon)
                life_bar(player_pokemon, enemy_pokemon)
            elif action == 'b':
                capture_with_pokeball(enemy_pokemon, player_profile)
            elif action == 'c':
                cure_pokemon(player_profile, player_pokemon)
            elif action == 'd':
                player_pokemon = choose_pokemon(player_profile)

        sleep(1)
        # si la vida del enemigo es 0, mi pokemon gana experiencia
        if int(enemy_pokemon["current_health"]) == 0:
            print("has ganado")
            assign_experience(attack_history)

        # si capturas al pokemon y esta en tu inventario, se rompe el bucle
        if enemy_pokemon in player_profile['pokemon_inventory']:
            break

        # si uno de los 2 tiene 0 de vida se cierra el bucle, sino el pokemon enemigo realiza su ataque
        if player_pokemon['current_health'] == 0 or enemy_pokemon['current_health'] == 0:
            break
        else:
            player_pokemon['current_health'] = enemy_attack(enemy_pokemon, player_pokemon)
            life_bar(player_pokemon, enemy_pokemon)
            print('\n')
            if player_pokemon['current_health'] == 0:
                break

    print('--- FIN DE COMBATE ---')
    input('[Enter]')


def choose_pokemon(player_profile):
    chosen = None

    # si mi pokemon tiene 0 de vida, se eliminara de mi inventario
    for index in range(len(player_profile['pokemon_inventory'])):
        if player_profile['pokemon_inventory'][index]['current_health'] == 0:
            player_profile['pokemon_inventory'].pop(index)
            break

    # Elige un pokemon de tu lista
    while not chosen:
        print('           Elige un pokemon\n'
              '    NOMBRE | NIVEL | VIDA | TIPO')
        # devuelve informacion nuestros 3 pokemons y la id que usan
        for index in range(len(player_profile['pokemon_inventory'])):
            print(f'{index} - {get_pokemon_info(player_profile['pokemon_inventory'][index])}')

        try:
            return player_profile['pokemon_inventory'][int(input('--> '))]
        except (ValueError, IndexError):
            print('opcion invalida')


# es un print que me muestra las caracteristicas del pokemon
def get_pokemon_info(pokemon):
    return (f'{pokemon['name']} | '
            f'{pokemon['level']} | '
            f'{pokemon['current_health']}/{pokemon['base_health']} | '
            f'{', '.join(pokemon['type'])}')


# es un condicion que te permite ver tus pokeballs y pociones de vida que tengo
def show_inventory_items(player_profile):
    if input('\n¿Quieres ver tu inventario?: ') in ['S', 'Si', 'si', 'SI', 's']:
        return (f'pokeball: {player_profile['pokeballs']['pokeball']}\n'
                f'superball: {player_profile['pokeballs']['superball']}\n'
                f'ultraball: {player_profile['pokeballs']['ultraball']}\n'
                f'masterball: {player_profile['pokeballs']['masterball']}\n'
                f'pocion de vida: {player_profile['health_potion']}\n')
    else:
        return 'vale, pues seguimos\n'


def player_attack(player_pokemon, enemy_pokemon):
    global list_level_attacks
    list_name_attacks = []
    name_attack = None

    for num in range(len(player_pokemon['attacks'])):
        # guardar en una lista todos los nombres de los ataques
        list_name_attacks.append(player_pokemon['attacks'][num]['name_attack'])
        # guardo en una lista externa el nivel los pokemons y que la lista no se resertee cada vez que entra la funcion
        if player_pokemon['level'] == int(player_pokemon['attacks'][num]['min_level']):
            if int(player_pokemon['attacks'][num]['min_level']) not in list_level_attacks:
                list_level_attacks.append(int(player_pokemon['attacks'][num]['min_level']))

    print(f'Turno de {player_pokemon['name']}\n'
          f'NOMBRE | NIVEL | DAÑO | TIPO')

    # imprimo los ataques disponibles en funcion al nivel de mi pokemon
    for a in player_pokemon['attacks']:

        if int(a['min_level']) in list_level_attacks:
            print(f'{a['name_attack']} | '
                  f'{a['min_level']} | '
                  f'{a['damage']} | '
                  f'{a['type_attack']}')

    print(f'\nTu nivel actual es {player_pokemon['level']}')

    while name_attack not in list_name_attacks:
        name_attack = input('elige un ataque: ')

    bonus_multiplication = multiplication_attack(player_pokemon, enemy_pokemon, name_attack)
    print(f'\n{player_pokemon['name']} utiliza {name_attack}, inflige {bonus_multiplication} de daño')
    return enemy_pokemon['current_health'] - bonus_multiplication


def multiplication_attack(player_pokemon, enemy_pokemon, name_attack):
    multiplication_list = elemental_pokemon_bonus_attack()
    for num in range(len(player_pokemon['attacks'])):  # accedemos a todos los ataques
        if name_attack == player_pokemon['attacks'][num]['name_attack']:  # buscamos el ataque que hemos seleccionado

            for element in multiplication_list:  # filtramos todos los elementos/tipos
                if element == player_pokemon['attacks'][num]['type_attack']:  # comparar con el tipo de nuestro ataque
                    # el multiplicador se aplica solo al primer tipo que se encuentre del pokemon
                    if enemy_pokemon['type'][0] in multiplication_list[element]['strong']:
                        return player_pokemon['attacks'][num]['damage'] * 2
                    elif enemy_pokemon['type'][0] in multiplication_list[element]['weak']:
                        return int(player_pokemon['attacks'][num]['damage'] / 2)
                    else:
                        return player_pokemon['attacks'][num]['damage']


# se selecciona una ataque aleatorio sin tener en cuenta el nivel del pokemon enemigo
def enemy_attack(enemy_pokemon, player_pokemon):
    choose_attack = random.choice(range(len(enemy_pokemon['attacks'])))
    damage_attack = enemy_pokemon['attacks'][choose_attack]['damage']
    name_attack = enemy_pokemon['attacks'][choose_attack]['name_attack']
    print(f'\nturno de {enemy_pokemon['name']}')
    print(f'{enemy_pokemon['name']} utiliza {name_attack}, inflige {damage_attack} de daño')
    return player_pokemon['current_health'] - damage_attack


# interfaz que muestra la vida de los 2 pokemons
def life_bar(player_pokemon, enemy_pokemon):
    my_pokemon_health = int(player_pokemon['current_health'] / 5)
    enemy_pokemon_health = int(enemy_pokemon['current_health'] / 5)

    if player_pokemon['current_health'] < 0:
        player_pokemon['current_health'] = 0
        my_pokemon_health = 0
    elif enemy_pokemon['current_health'] < 0:
        enemy_pokemon['current_health'] = 0
        enemy_pokemon_health = 0

    return print(f'{player_pokemon['name']} '
                 f'[{my_pokemon_health * '♡'}{' ' * (20 - my_pokemon_health)}]'
                 f'[{player_pokemon['current_health']}/{player_pokemon['base_health']}]\n'
                 f'{enemy_pokemon['name']} '
                 f'[{enemy_pokemon_health * '♡'}{' ' * (20 - enemy_pokemon_health)}]'
                 f'[{enemy_pokemon['current_health']}/{enemy_pokemon['base_health']}]')


def capture_with_pokeball(enemy_pokemon, player_profile):
    print(f'\n{enemy_pokemon['name']} tiene {enemy_pokemon['current_health']} de vida\n'
          f'1. {player_profile['pokeballs']['pokeball']} pokeball(s)\n'
          f'2. {player_profile['pokeballs']['superball']} superball(s)\n'
          f'3. {player_profile['pokeballs']['ultraball']} ultraball(s)\n'
          f'4. {player_profile['pokeballs']['masterball']} masterball(s)')
    opcion = int(input('elige una pokeball[1-4]: '))
    print('*tiras la pokeball...')
    sleep(2)
    probability = random.choice(range(1, 10))
    # en funcion de la vida, tienes una probalilidad de capturar al pokemon
    # hay pokeballs que aumentan la probabilidad de capturarlo debido a su rareza
    if opcion == 1:

        if player_profile['pokeballs']['pokeball'] == 0:
            print('No te quedan estas pokeballs')
        else:
            if enemy_pokemon['current_health'] in range(70, 100+1):
                if probability == 1:
                    add_pokemon(enemy_pokemon, player_profile)
                else:
                    print('Vaya, has utilizado la pokeball cuando el enemigo todavia tiene mucha vida')
            if enemy_pokemon['current_health'] in range(35, 69+1):
                if probability in range(1, 5):
                    add_pokemon(enemy_pokemon, player_profile)
                else:
                    print('Mmmmm.... intentalo otra vez si quieres')
            if enemy_pokemon['current_health'] in range(1, 34+1):
                if probability in range(1, 8):
                    add_pokemon(enemy_pokemon, player_profile)
                else:
                    print('Haz tenido mala suerte intentalo otra vez')

        player_profile['pokeballs']['pokeball'] -= 1
        if player_profile['pokeballs']['pokeball'] <= 0:
            player_profile['pokeballs']['pokeball'] = 0

    elif opcion == 2:

        if player_profile['pokeballs']['superball'] == 0:
            print('No te quedan estas pokeballs')
        else:
            if enemy_pokemon['current_health'] in range(75, 100+1):
                if probability in range(1, 8):
                    add_pokemon(enemy_pokemon, player_profile)
                else:
                    print('Esto si que es tener mala suerte')
            if enemy_pokemon['current_health'] in range(1, 74+1):
                if probability in range(1, 9):
                    add_pokemon(enemy_pokemon, player_profile)
                else:
                    print('Vaya...has tenido mala suerte')

        player_profile['pokeballs']['superball'] -= 1
        if player_profile['pokeballs']['superball'] <= 0:
            player_profile['pokeballs']['superball'] = 0

    elif opcion == 3:

        if player_profile['pokeballs']['ultraball'] == 0:
            print('No te quedan estas pokeballs')
        else:
            if probability in range(1, 8):
                add_pokemon(enemy_pokemon, player_profile)
            else:
                print('Tienes muy mala suerte como pàra que se te haya librado el pokemon')

        player_profile['pokeballs']['ultraball'] -= 1
        if player_profile['pokeballs']['ultraball'] <= 0:
            player_profile['pokeballs']['ultraball'] = 0

    elif opcion == 4:

        if player_profile['pokeballs']['masterball'] == 0:
            print('No te quedan estas pokeballs')
        else:
            add_pokemon(enemy_pokemon, player_profile)
        player_profile['pokeballs']['masterball'] -= 1
        if player_profile['pokeballs']['masterball'] <= 0:
            player_profile['pokeballs']['masterball'] = 0


# si se da el caso de haber capturado el pokemon, se te añadira al inventario
def add_pokemon(enemy_pokemon, player_profile):
    enemy_pokemon['current_health'] = 100
    print('Un pokemon mas a la lista')
    return player_profile['pokemon_inventory'].append(enemy_pokemon)


# si tienes pociones de vida podras curar a tu pokemon, estas pociones no sobrepasaran de 100
def cure_pokemon(player_profile, player_pokemon):
    if player_profile['health_potion'] == 0:
        print(f'Tienes {player_profile['health_potion']} pociones de vida\n'
              f'por lo tanto no puedes curar a tus pokemons')
    else:
        print(f'Tienes {player_profile['health_potion']} pociones de vida'
              f' y tu {player_pokemon['name']} tiene {player_pokemon['current_health']} de vida')
        if input(f'Quieres curar a tu {player_pokemon['name']}?\n---> ') in ['S', 'Si', 'si', 'SI', 's']:
            player_profile['health_potion'] -= 1
            player_pokemon['current_health'] += 50
            if player_pokemon['current_health'] > 100:
                player_pokemon['current_health'] = 100
            return player_pokemon['current_health']


# cada vez que gane tu pokemon habra una seleccion de numeros aleatorios y que cuando estos sean mayor que 20
# el pokemon subira de nivel
def assign_experience(attack_history):
    for pokemon in attack_history:
        points = random.randint(1, 10)
        pokemon['current_exp'] += points
        while pokemon['current_exp'] > 20:
            pokemon['current_exp'] -= 20
            pokemon['level'] += 1
            pokemon['current_health'] = pokemon['base_health']
            print(f'tu pokemon sube de nivel\n{get_pokemon_info(pokemon)}')


# cada vez que ganes, recibiras un objetos aleatorio que se te añadira al inventario
def item_lottery(player_profile, enemy_pokemon):
    probability = random.choice(range(1, 100+1))

    if enemy_pokemon['current_health'] == 0:
        print('Veamos si se te añadira un objeto al inventario o no...')
        sleep(2)
        if probability in range(1, 10+1):
            print('Vaya... no has conseguido nada')

        elif probability in range(11, 40+1):
            print('una pokeball')
            player_profile['pokeballs']['pokeball'] += 1
            return player_profile['pokeballs']['pokeball']

        elif probability in range(41, 70+1):
            print('una pocion de vida')
            player_profile['health_potion'] += 1
            return player_profile['health_potion']

        elif probability in range(71, 85+1):
            print('!una superball!')
            player_profile['pokeballs']['superball'] += 1
            return player_profile['pokeballs']['superball']

        elif probability in range(86, 95+1):
            print('¡¡¡Una ultraball!!!')
            player_profile['pokeballs']['ultraball'] += 1
            return player_profile['pokeballs']['ultraball']

        elif probability in range(96, 100+1):
            print('¡¡¡UNA MASTERBALL!!!')
            player_profile['pokeballs']['masterball'] += 1
            return player_profile['pokeballs']['masterball']


def main():
    list_pokemon = save_all_pokemons()  # guardamos todos los pokemons en una variable
    # guardamos los pokemons enemigos en otra lista porque en caso de tener una pelea donde sean los mismos pokemons
    # la vida se restará a ambos
    enemy_list_pokemon = save_all_pokemons()
    welcome()
    player_profile = get_player_profile(list_pokemon)  # creamos el perfil del jugador
    count_combats = 0

    while any_player_pokemon_lives(player_profile):  # es un True pero cuando la vida <= 0 sera un False y se finalizara
        enemy_pokemon = random.choice(enemy_list_pokemon)  # seleccionara un pokemon aleatorio
        fight(player_profile, enemy_pokemon)
        count_combats += 1
        item_lottery(player_profile, enemy_pokemon)
        os.system('cls')
        sleep(1)

    if len(player_profile['pokemon_inventory']) == 1:
        print(f'has perdido en el combate numero {count_combats}\n'
              f'intenta una nueva partida ')
    else:
        print('¡¡¡FELICIDADES!!!\n'
              'te has convertido en el mejor entrenador pokemon')


if __name__ == "__main__":
    main()
