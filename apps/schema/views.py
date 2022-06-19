import glob
import os

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import FileResponse, HttpResponseNotFound
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DeleteView
from django.views.generic.edit import FormMixin, UpdateView

from FakeSchema import settings
from apps.schema.forms import SchemaCreateForm, DataSetGenerateForm, SchemaUpdateForm
from apps.schema.models import Schema, DataSet
from apps.schema.tasks import create_dataset


class SchemaList(LoginRequiredMixin, ListView):
    template_name = 'schema/schema_list.html'
    context_object_name = 'schema_list'

    def get_queryset(self):
        return Schema.objects.only('name', 'modified').filter(user=self.request.user).order_by('-pk')


class SchemaCreateView(LoginRequiredMixin, CreateView):
    success_url = reverse_lazy('schema-list')
    form_class = SchemaCreateForm
    template_name = 'schema/schema_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class SchemaUpdateView(LoginRequiredMixin, UpdateView):
    form_class = SchemaUpdateForm
    template_name = 'schema/schema_update.html'
    model = Schema

    def get_success_url(self):
        return reverse('schema-update', args=(self.object.pk,))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'schema_pk': self.object.pk})
        return kwargs


class SchemaDeleteView(LoginRequiredMixin, DeleteView):
    model = Schema
    success_url = reverse_lazy('schema-list')


class SchemaGenerateView(LoginRequiredMixin, UserPassesTestMixin, FormMixin, ListView):
    template_name = 'schema/schema_generate.html'
    context_object_name = 'data_sets'
    form_class = DataSetGenerateForm

    def test_func(self):
        schema_pk = self.kwargs.get('pk')
        return Schema.objects.filter(pk=schema_pk, user=self.request.user).exists()

    def get_queryset(self):
        schema_pk = self.kwargs.get('pk')
        return DataSet.objects.only('created', 'status').filter(schema=schema_pk).order_by('-pk')

    def post(self, request, *args, **kwargs):
        self.form = self.get_form()
        if self.form.is_valid():
            create_dataset(kwargs.get('pk'), self.form.cleaned_data.get('rows'))
            return redirect(request.path_info)
        else:
            return self.get(request, *args, **kwargs)


def download_file(request, pk):
    dataset = get_object_or_404(DataSet, pk=pk)
    file_path = os.path.join(settings.MEDIA_ROOT, dataset.file.name)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'))
    else:
        return HttpResponseNotFound()
