from django import forms
from django.core.validators import MinValueValidator
from django.db import transaction
from django.forms import modelformset_factory, BaseModelFormSet

from apps.schema.models import Schema, Column, DataType
from apps.schema.validators import type_range_validator


class ColumnForm(forms.ModelForm):
    type = forms.ModelChoiceField(DataType.objects.order_by('id'), required=True)

    class Meta:
        model = Column
        fields = ['name', 'type', 'range_start', 'range_end', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class BaseColumnFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for form in self.forms:
            form.empty_permitted = False

    def clean(self):
        super().clean()
        schema_columns_names = set()
        column_orders = set()
        max_column_order = len(self.forms) - 1
        for form in self.forms:
            column_name = form.cleaned_data.get('name')
            data_type = form.cleaned_data.get('type')
            column_order = form.cleaned_data.get('order')

            if column_name and column_name in schema_columns_names:
                form.add_error('name', 'This column name is already used.')
            else:
                schema_columns_names.add(column_name)

            if data_type and data_type.ranged:
                range_start, range_end = form.cleaned_data.get('range_start'), form.cleaned_data.get('range_end')
                type_range_validator(form, range_start, range_end)

            if column_order is not None:
                if column_order > max_column_order:
                    form.add_error('order', f'Order out of range max is {max_column_order}.')
                elif column_order in column_orders:
                    form.add_error('order', f'Order is already used.')
                else:
                    column_orders.add(column_order)


ColumnFormset = modelformset_factory(Column, form=ColumnForm, formset=BaseColumnFormSet, min_num=1, extra=0,
                                     validate_min=True)


class BaseSchemaForm(forms.ModelForm):
    class Meta:
        model = Schema
        fields = ['name', 'column_separator', 'string_character']

    def __init__(self, data=None, column_formset=None, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)
        self.column_formset = column_formset
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def is_valid(self):
        return super().is_valid() and self.column_formset.is_valid()


class SchemaCreateForm(BaseSchemaForm):
    def __init__(self, data=None, *args, **kwargs):
        self.user = kwargs.pop('user')
        column_formset = ColumnFormset(data=data, queryset=Column.objects.none())
        super().__init__(data=data, column_formset=column_formset, *args, **kwargs)

    def save(self, commit=True):
        with transaction.atomic():
            schema_instance = super().save(commit=False)
            schema_instance.user = self.user
            schema_instance.save()
            schema_columns = self.column_formset.save(commit=False)
            for column in schema_columns:
                column.schema = schema_instance
            Column.objects.bulk_create(schema_columns)
        return schema_instance


class SchemaUpdateForm(BaseSchemaForm):
    def __init__(self, data=None, *args, **kwargs):
        self.schema_pk = kwargs.pop('schema_pk')
        column_formset = ColumnFormset(data=data, queryset=Column.objects.filter(schema_id=self.schema_pk))
        super().__init__(data=data, column_formset=column_formset, *args, **kwargs)

    def save(self, commit=True):
        with transaction.atomic():
            schema_instance = super().save()
            Column.objects.filter(schema=schema_instance).delete()
            schema_columns = []
            for form in self.column_formset:
                form.instance.pk = None
                form.instance.schema = schema_instance
                schema_columns.append(form.instance)
            Column.objects.bulk_create(schema_columns)
        return schema_instance


class DataSetGenerateForm(forms.Form):
    rows = forms.IntegerField(validators=[MinValueValidator(1)],
                              widget=forms.NumberInput(attrs={'class': 'form-control'}))
