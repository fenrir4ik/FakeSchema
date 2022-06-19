from apps.schema.services.generators import TextGenerator, IntegerGenerator, EmailGenerator, FullNameGenerator, \
    JobGenerator


class GeneratorFactory:
    def __init__(self):
        self.__generators = {
            'Integer': IntegerGenerator,
            'Text': TextGenerator,
            'Email': EmailGenerator,
            'Full name': FullNameGenerator,
            'Job': JobGenerator
        }

    def get_generator(self, typename, *args, **kwargs):
        generator_class = self.__generators.get(typename)
        if not generator_class:
            raise ValueError(f"Generetor for given type ({typename}) not implemented")
        return generator_class(*args, **kwargs)
