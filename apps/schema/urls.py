from django.urls import path

from apps.schema.views import SchemaList, SchemaCreateView, SchemaDeleteView, SchemaGenerateView, download_file, \
    SchemaUpdateView

urlpatterns = [
    path('', SchemaList.as_view(), name='schema-list'),
    path('schema_create/', SchemaCreateView.as_view(), name='schema-create'),
    path('schema_delete/<int:pk>/', SchemaDeleteView.as_view(), name='schema-delete'),
    path('schema_generate/<int:pk>/', SchemaGenerateView.as_view(), name='schema-generate'),
    path('schema_update/<int:pk>/', SchemaUpdateView.as_view(), name='schema-update'),
    path('download/<int:pk>/', download_file, name='download-csv')
]
