import os
from datetime import datetime

from django.conf import settings

from apps.schema.services.generator_factory import GeneratorFactory



class CSVDataGenerator:
    generator_factory = GeneratorFactory()
    __line_format = None
    __generators_list = None

    def __init__(self, schema_id, columns_info, rows, column_separator, string_character):
        if isinstance(rows, int) and rows < 1:
            raise ValueError('Dataset should contain at least 1 line')
        self.schema_id = schema_id
        self.rows = rows
        self.columns_info = columns_info
        self.column_separator = column_separator
        self.string_character = string_character
        self.column_names = self.columns_info.keys()
        self.__configure()

    def __configure(self):
        self.__configure_generators()
        self.__configure_line_format()

    def __configure_generators(self):
        self.__generators_list = []
        for column in self.columns_info.values():
            column_range = column.get('range')
            column_type = column.get('type')
            if column_range:
                generator = self.generator_factory.get_generator(column_type, *column_range)
            else:
                generator = self.generator_factory.get_generator(column_type)
            self.__generators_list.append(generator)

    def __configure_line_format(self):
        single_column = self.string_character + "{}" + self.string_character
        self.__line_format = self.column_separator.join([single_column for _ in range(len(self.column_names))])

    def line_generator(self):
        if self.__line_format is None or len(self.__generators_list) == 0:
            raise ValueError("Generator is improperly configured")
        while True:
            yield self.__line_format.format(*[generator.generate() for generator in self.__generators_list])

    def generate(self):
        file_name = self.generate_random_file_name()
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        csv_header = self.column_separator.join(self.column_names)
        generator = self.line_generator()
        with open(file_path, 'w') as file:
            file.write(csv_header + '\n')
            for i in range(self.rows):
                line = next(generator)
                if i != self.rows - 1:
                    line += '\n'
                file.write(line)
        return file_name

    def generate_random_file_name(self):
        return f"{datetime.utcnow().strftime('%Y%m%d-%H%M%S.%f')}.csv"
