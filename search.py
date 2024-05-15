import csv
import html
import re
import shutil
from collections import Counter
from itertools import count
from pathlib import Path
from textwrap import dedent

from PIL import Image, ImageDraw


class FlagFetcher:
    def __init__(self):
        self.has_printed = False
        self.dest_folder = Path(__file__).with_name('iso-flags')

    def fetch(self, name: str, num: int) -> Path:
        dest_path = self.dest_folder / f'flag{num}.png'
        if dest_path.exists():
            return dest_path
        self.scrape()
        if dest_path.exists():
            return dest_path
        if not self.has_printed:
            message = dedent('''\
                To fetch missing flags:
                * Edit your Wikipedia user page.
                * Copy the list below, and paste it in the editor.
                * Wait for the preview to update.
                * Then save the complete web page in the iso-flags folder.
                * Run this script again to generate puzzles.
                
                Here's the list to paste in the editor:''')
            print(message)
            self.has_printed = True
        print(f'* flag{num} {{{{flagicon|{name}|size=300px}}}}')
        return dest_path

    def scrape(self) -> None:
        for source_page in self.dest_folder.glob('*.html'):
            page_text = source_page.read_text()
            for label, img_path in re.findall(
                    r'(flag\d+).*<img .*src="(.*?)"',
                    page_text):
                clean_img_path = html.unescape(img_path)
                source_path = self.dest_folder.joinpath(clean_img_path)
                dest_path = self.dest_folder / f'{label}.png'
                shutil.copy(source_path, dest_path)
            archive_folder = self.dest_folder / 'archive'
            for i in count(1):
                archive_path = archive_folder / f'version{i}'
                if archive_path.exists():
                    continue

                source_files_stem = source_page.stem
                source_files = source_page.with_name(
                    source_files_stem + '_files')
                archive_path.mkdir(parents=True)
                shutil.move(source_page, archive_path)
                shutil.move(source_files, archive_path)
                break


def paste_images(dest_image: Path, *source_images: Path) -> None:
    sources = [Image.open(source_image) for source_image in source_images]
    width = max(source.width for source in sources)
    height = sum(source.height for source in sources)
    output = Image.new('RGBA', (width, height))
    drawing = ImageDraw.Draw(output)
    y = 0
    for source in sources:
        output.paste(source, (0, y))
        drawing.rectangle((0, y, source.width, y+source.height-1),
                          outline='black')
        y += source.height
    # output.show()
    output.save(dest_image)
    print(f'Saved as {dest_image}')


def main():
    data_path = Path(__file__).with_name('iso-countries.csv')
    populations = {}
    names = {}
    country_numbers = {}
    fetcher = FlagFetcher()
    # uk_path = fetcher.fetch('United Kingdom', 244)
    # canada_path = fetcher.fetch('Canada', 42)
    # paste_images(data_path.with_name('pasted.png'),
    #              uk_path,
    #              canada_path)
    # return
    with data_path.open() as f:
        reader = csv.DictReader(f)
        row: dict[str, str]
        for row in reader:
            iso = row['ISO-3166 Code']
            country_name = row['Country']
            country_num = int(row['Index'])
            fetcher.fetch(country_name, country_num)
            names[iso] = country_name
            country_numbers[iso] = country_num
            pop_text = row['Population']
            if pop_text and pop_text != '0':
                populations[iso] = int(pop_text)
    word_path = Path('/usr/share/dict/american-english')
    word_list = [word
                 for word, pair in re.findall(r'^(([a-z][a-z]){2,})$',
                                              word_path.read_text(),
                                              re.MULTILINE)]
    if fetcher.has_printed:
        # Missing some flags, so give up.
        return

    # TODO: Eliminate duplicate flags.

    word_scores = Counter()
    for word in word_list:
        letters = iter(word)
        pairs = zip(letters, letters)
        scores = []
        countries = []
        image_paths = []
        try:
            for pair in pairs:
                iso = ''.join(pair).upper()
                country = names[iso]
                country_num = country_numbers[iso]
                img_path = fetcher.fetch(country, country_num)
                image_paths.append(img_path)
                countries.append(country)
                population = populations[iso]
                scores.append(population)
            score = min(scores) * len(word)
            word_scores[tuple(image_paths)] = score
        except KeyError:
            # Missing country, can't use word.
            pass

    for puzzle_num, (image_paths, score) in enumerate(word_scores.most_common(10),
                                                      1):
        output_path = data_path.with_name(f'puzzle{puzzle_num}.png')
        paste_images(output_path, *image_paths)


main()
