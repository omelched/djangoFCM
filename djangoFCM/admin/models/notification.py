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

from django.contrib import admin, messages
from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import render
from django.db.models import QuerySet
from django.utils.translation import ugettext_lazy as _
from django.forms import formset_factory, Media, BaseFormSet

from djangoFCM.forms import DataComposerForm
from djangoFCM.models import PushToken


class NotificationAdmin(admin.ModelAdmin):
    class RecipientsComposerForm(DataComposerForm):
        model = PushToken

    fieldsets = (
        (
            None,
            {
                'fields': (
                    ('name', 'sent'),
                )
            }
        ),
        (
            _('payload'),
            {
                'fields': (
                    ('title', 'body'),
                )
            }
        ),
        (
            _('sending info'),
            {
                'fields': (
                    ('recipients', 'send_on'),
                )
            }
        ),
        (
            _('important dates'),
            {
                'fields': (
                    'creation_date',
                )
            }
        )
    )

    list_display = ('name', 'title', 'send_on', 'sent')
    list_filter = ('sent',)
    search_fields = ('name', 'title', 'body', 'send_on', 'recipients')
    ordering = ('send_on', 'title')
    readonly_fields = ('sent', 'creation_date')
    filter_horizontal = ('recipients',)
    actions = ['compose_recipients']

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.sent:
            return super().get_readonly_fields(request, obj) + ('title', 'body', 'recipients', 'send_on')

        return super().get_readonly_fields(request, obj)

    def get_formset(self, data):
        FormSet = formset_factory(
            self.RecipientsComposerForm,
            extra=0,
            max_num=1,
        )
        return FormSet(data)

    def compose_recipients(self, request: HttpRequest, queryset: QuerySet):
        if 'do_action' in request.POST:
            formset: BaseFormSet = self.get_formset(request.POST)
            if not formset.is_valid():
                raise Exception(formset.errors)

            for notification in queryset:
                notification.recipients_composer_conditions = formset.cleaned_data
                notification.save()
                notification.compile_recipients()

        if queryset.filter(sent=True).exists():
            self.message_user(
                request,
                'One of notifications is already sent! Select unsent notifications.',
                messages.ERROR)
            return

        formset = self.get_formset(None)

        extra = '' if settings.DEBUG else '.min'
        js = [
            'admin/js/vendor/jquery/jquery%s.js' % extra,
            'admin/js/jquery.init.js',
            'djangoFCM/generic/js/data-composer.js',
        ]
        css = {
            'all': [
                'djangoFCM/generic/css/data-composer.css',
            ]
        }
        context = {
            'notifications': queryset,
            'formset': formset,
            'media': Media(js=js, css=css)
        }

        return render(
            request=request,
            template_name='djangoFCM/admin/recipients_composer.html',
            context=context
        )