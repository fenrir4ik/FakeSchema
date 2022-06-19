from django.contrib import admin

from apps.schema.models import ColumnSeparator, StringCharacter, DataType

admin.site.register(ColumnSeparator)
admin.site.register(StringCharacter)


@admin.register(DataType)
class ItemAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('ranged', 'name')
        return self.readonly_fields

