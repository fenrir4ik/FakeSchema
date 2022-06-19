from django.db.models import Prefetch

from FakeSchema.celery import app
from apps.schema.models import DataSet, Schema, Column
from apps.schema.services.data_generator import CSVDataGenerator


@app.task(name='create_dataset')
def generate_dataset(schema_id, dataset_id, rows):
    schema = Schema.objects.select_related('column_separator', 'string_character') \
        .prefetch_related(Prefetch('column_set', queryset=Column.objects.select_related('type').all())) \
        .only('column_separator', 'string_character') \
        .get(pk=schema_id)

    schema_columns = {col.name: {
        'order': col.order,
        'type': col.type.name,
        'range': (col.range_start, col.range_end) if col.type.ranged else None
    } for col in schema.column_set.order_by('order')}

    dataset = DataSet.objects.get(pk=dataset_id)
    try:
        data_generator = CSVDataGenerator(schema_id, schema_columns, rows, schema.column_separator.char,
                                          schema.string_character.char)
        file_name = data_generator.generate()
        dataset.status = DataSet.READY
        dataset.file.name = file_name
        dataset.save()
    except (ValueError, TypeError):
        dataset.status = DataSet.FAILED
        dataset.save()


def create_dataset(schema_id, rows):
    dataset = DataSet(schema_id=schema_id)
    dataset.save()
    generate_dataset.delay(schema_id, dataset.pk, rows)
