# ******************************************************************************
#  djangoFCM — Django app which stores, manages FCM push tokens                *
#  and interacts with them.                                                    *
#  Copyright (C) 2021-2021 omelched                                            *
#                                                                              *
#  This file is part of djangoFCM.                                             *
#                                                                              *
#  djangoFCM is free software: you can redistribute it and/or modify           *
#  it under the terms of the GNU Affero General Public License as published    *
#  by the Free Software Foundation, either version 3 of the License, or        *
#  (at your option) any later version.                                         *
#                                                                              *
#  djangoFCM is distributed in the hope that it will be useful,                *
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              *
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               *
#  GNU Affero General Public License for more details.                         *
#                                                                              *
#  You should have received a copy of the GNU Affero General Public License    *
#  along with djangoFCM.  If not, see <https://www.gnu.org/licenses/>.         *
# ******************************************************************************

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.db import models

from djangoFCM import get_application_model


class PushTokenAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'push_token',
                    ('user', 'application',)
                )
            }
        ),
        (
            _('important dates'),
            {
                'fields': (
                    'creation_date',
                    'update_date',
                )
            }
        ),
    )

    list_display = ('short_token', 'user', 'application',)
    list_filter = ('application',)
    search_fields = ('push_token', 'user__username',)
    ordering = ('user', 'creation_date',)
    readonly_fields = ('creation_date', 'update_date',)
    autocomplete_fields = ('user',)

    def get_search_fields(self, request):
        application_fields = get_application_model()._meta.fields
        searchable_fields_lookups = []
        for field in application_fields:
            if isinstance(field, models.CharField) or isinstance(field, models.TextField):
                searchable_fields_lookups.append(f'application__{field.name}')

        return super(PushTokenAdmin, self).get_search_fields(request) + tuple(searchable_fields_lookups)
