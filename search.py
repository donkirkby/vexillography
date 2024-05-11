import csv
import re
from collections import Counter
from pathlib import Path
from time import sleep

import requests


# def fetch_flag(name: str, num: int) -> None:
#     url = f'https://upload.wikimedia.org/wikipedia/commons/c/ce/Flag_of_{name}.svg'
#     dest_folder = Path('~/Downloads/iso-flags').expanduser()
#     error_path = dest_folder / f'error{num}.html'
#     dest_path = dest_folder / f'flag{num}.svg'
#     if dest_path.exists() or error_path.exists():
#         return
#     response = requests.get(url, headers={'User-Agent': 'FlagCollectorBot/1.0 donkirkby@gmail.com'})
#     if response.status_code != requests.codes.ok:
#         error_path.write_bytes(response.content)
#     else:
#         dest_path.write_bytes(response.content)
#     sleep(0.1)


def main():
    data_path = Path(__file__).with_name('iso-countries.csv')
    populations = {}
    names = {}
    # fetch_flag('Afghanistan', 1)
    # fetch_flag('Iceland', 110)
    with data_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            iso = row['ISO-3166 Code']
            country_name = row['Country']
            country_num = int(row['Index'])
            # fetch_flag(country_name, country_num)
            names[iso] = country_name
            pop_text = row['Population']
            if pop_text and pop_text != '0':
                populations[iso] = int(pop_text)
    word_path = Path('/usr/share/dict/american-english')
    word_list = [word
                 for word, pair in re.findall(r'^(([a-z][a-z]){2,})$',
                                              word_path.read_text(),
                                              re.MULTILINE)]
    word_scores = Counter()
    for word in word_list:
        letters = iter(word)
        pairs = zip(letters, letters)
        score = 0
        countries = []
        try:
            for pair in pairs:
                iso = ''.join(pair).upper()
                country = names[iso]
                countries.append(country)
                population = populations[iso]
                score += population
            score = round(score / len(word)*2)
            display = ', '.join(countries)
            word_scores[display] = score
            print(score, display)
            break
        except KeyError:
            # Missing country, can't use word.
            pass


main()
