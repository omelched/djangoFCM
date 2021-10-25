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

from ...models import Parameter, ParameterChoices


class ParameterChoicesInline(admin.TabularInline):
    model = ParameterChoices
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'choice',
                )
            }
        ),
    )
    extra = 0


class ParameterAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'name',
                    'type',
                )
            }
        ),
    )

    list_display = ('name', 'type',)
    list_filter = ('type',)
    search_fields = ('name',)
    ordering = ('name', 'type',)
    filter_vertical = ('content_types',)
    inlines = ()

    def get_fieldsets(self, request, obj=None):

        if obj and obj.type == Parameter.ParameterTypes.FOREIGN_KEY:
            return super().get_fieldsets(request, obj) + (
                (
                    _('content types'),
                    {
                        'fields': (
                            'content_types',
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_inlines(self, request, obj):

        if obj and obj.type == Parameter.ParameterTypes.CHOICE:
            return super().get_inlines(request, obj) + (ParameterChoicesInline,)

        return super().get_inlines(request, obj)
