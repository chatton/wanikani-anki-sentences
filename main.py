import os
import sys
from typing import List, Tuple

from wanikani_api.models import Vocabulary, UserInformation
from wanikani_api.client import Client


def extract_context_sentences(v: Vocabulary) -> List[Tuple[str, str]]:
    sentences = v._raw['data']['context_sentences']
    return [(d["en"], d["ja"]) for d in sentences]


def main():
    api_key = os.getenv("WANIKANI_API_KEY")
    if len(sys.argv) > 2:
        api_key = sys.argv[1]

    client = Client(v2_api_key=api_key)
    user_information: UserInformation = client.user_information()

    vocab: List[Vocabulary] = client.subjects(types="vocabulary")

    lines = []

    for v in vocab:
        # we don't care about vocab that is above our level.
        if v.level > user_information.level:
            continue

        sentences = extract_context_sentences(v)
        for sentence in sentences:
            en, jp = sentence
            lines.append(convert_vocab_sentence_to_text_file_import_line(v, en, jp))

    file_contents = '\n'.join(lines)

    with open("/Users/cian.hatton/Desktop/anki-imports/import-test.txt", "w+") as f:
        f.write(file_contents)


def convert_vocab_sentence_to_text_file_import_line(v: Vocabulary, en: str, jp: str) -> str:
    # first entry is japanese text

    size = len(jp) - len(v.characters)
    padding = " " * size
    characters_and_japanese_text = f'''"{padding}{v.characters}

{jp}"'''
    # second entry is the english meaning.
    # third entry contains readings.
    line = [characters_and_japanese_text, en,
            ','.join([m.meaning for m in v.meanings]) + " - " + ','.join([r.reading for r in v.readings])]
    return ';'.join(line)


if __name__ == '__main__':
    main()
