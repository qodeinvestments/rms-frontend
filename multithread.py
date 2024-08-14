import requests
import time
import concurrent.futures

def fetch_pokemon(id):
    url = f'https://pokeapi.co/api/v2/pokemon/{id}'
    resp = requests.get(url)
    pokemon = resp.json()
    return pokemon['name']

def main():
    start_time = time.time()

    # Number of threads to use
    max_threads = 100

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Create a list of futures
        futures = [executor.submit(fetch_pokemon, i) for i in range(1, 151)]

        # As each future completes, print the result
        for future in concurrent.futures.as_completed(futures):
            print(future.result())

    end_time = time.time()
    print(f"Total time: {end_time - start_time}")

if __name__ == "__main__":
    main()