import abc
import os.path
import random
from string import ascii_letters

from django.conf import settings


class DataTypeGenerator(abc.ABC):
    @abc.abstractmethod
    def generate(self):
        pass


class DataTypeWithSourceGenerator(DataTypeGenerator):
    data_source = []

    def __init__(self, data_source):
        self.data_source = self.load_source(data_source)

    @classmethod
    def load_source(cls, data_source):
        try:
            with open(data_source, 'r') as file:
                file_data = file.read()
                result_list = file_data.split('\n')
        except FileNotFoundError:
            raise ValueError(f"{cls.__name__} is improperly configured, file {data_source} not found.")
        return result_list


class IntegerGenerator(DataTypeGenerator):
    """Range included [from_, to_]"""

    def __init__(self, start, end):
        if start > end:
            raise ValueError(f'Start value({start}) is greater then end value({end})')
        self.start, self.end = start, end

    def generate(self):
        return random.randint(self.start, self.end)


class TextGenerator(DataTypeWithSourceGenerator):
    def __init__(self, min_sentences, max_sentences,
                 data_source=os.path.join(settings.STATICFILES_DIRS[0], 'data_sources', 'text.txt'),
                 min_words_size=3, max_words_size=10):
        super().__init__(data_source)
        if min_words_size is None or min_words_size < 1:
            raise ValueError("Sentence should contain at least 1 word")
        if max_words_size is None or max_words_size < min_words_size:
            raise ValueError(f"Invalid max_words_size given {max_words_size}")
        if min_sentences is None or min_sentences < 1:
            raise ValueError("String should contain at least 1 sentence")
        if max_sentences is None or max_sentences < min_sentences:
            raise ValueError(f"Invalid max_sentences given {max_sentences}")

        self.min_sentences = min_sentences
        self.max_sentences = max_sentences
        self.min_words_size = min_words_size
        self.max_words_size = max_words_size

    def generate(self):
        sentences = []
        sentences_number = random.randint(self.min_sentences, self.max_sentences)
        for i in range(sentences_number):
            sentence_length = random.randint(self.min_words_size, self.max_words_size)
            words = [random.choice(self.data_source) for _ in range(sentence_length)]
            words[0] = words[0].capitalize()
            sentence = ' '.join(words) + '.'
            sentences.append(sentence)
        return ' '.join(sentences)


class EmailGenerator(DataTypeGenerator):
    def __init__(self, email_domain='gmail.com', email_min_size=3, email_max_size=30):
        self.email_domain = email_domain
        self.email_min_size = email_min_size
        self.email_max_size = email_max_size

    def generate(self):
        address_size = random.randint(self.email_min_size, self.email_max_size)
        return f"{''.join(random.choice(ascii_letters) for _ in range(address_size))}@{self.email_domain}"


class FullNameGenerator(DataTypeWithSourceGenerator):
    def __init__(self, data_source=os.path.join(settings.STATICFILES_DIRS[0], 'data_sources', 'full_name.txt')):
        super().__init__(data_source)

    def generate(self):
        return random.choice(self.data_source)


class JobGenerator(DataTypeWithSourceGenerator):
    def __init__(self, data_source=os.path.join(settings.STATICFILES_DIRS[0], 'data_sources', 'job.txt')):
        super().__init__(data_source)

    def generate(self):
        return random.choice(self.data_source)
