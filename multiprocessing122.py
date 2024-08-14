import requests
import time
import multiprocessing

def fetch_pokemon(id):
    url = f'https://pokeapi.co/api/v2/pokemon/{id}'
    resp = requests.get(url)
    pokemon = resp.json()
    return pokemon['name']

def main():
    start_time = time.time()

    with multiprocessing.Pool() as pool:
        pokemon_names = pool.map(fetch_pokemon, range(1, 151))

    for name in pokemon_names:
        print(name)

    end_time = time.time()
    print(end_time - start_time)

if __name__ == '__main__':
    main()