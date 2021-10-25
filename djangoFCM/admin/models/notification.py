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

import types
import re

from django.utils import timezone
from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.conf import settings
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType

from ...models import Notification, Parameter, PushToken


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = '__all__'

    body = forms.CharField(widget=forms.Textarea)

    def clean(self):
        if 'send_on' in self.cleaned_data and not self.cleaned_data['send_on'] > timezone.now():
            raise forms.ValidationError({'send_on': 'too late'})


class NotificationAdmin(admin.ModelAdmin):
    form = NotificationForm
    actions = ['compose_recipients']

    class RecipientsComposerForm(forms.Form):

        @staticmethod
        def _get_parameter_choices(ns):
            def get_operators():
                return ('is', 'is'),

            qs = Parameter.objects.all()
            foreign_parameters = qs.filter(type=Parameter.ParameterTypes.FOREIGN_KEY)

            choices = []
            for parameter in foreign_parameters:
                for content_type in parameter.content_types.all():
                    choices.extend(
                        [
                            (f'{parameter.pk}({content_type.pk}).{field.attname}',
                             f'{parameter.name}({content_type.app_labeled_name}).{field.attname}')
                            for field in content_type.model_class()._meta.fields    # noqa: protected-member
                        ]
                    )

            ns['group_state'] = forms.ChoiceField(choices=(('OR', 'OR'), ('AND', 'AND')))
            ns['parameter'] = forms.ChoiceField(choices=choices)
            ns['operator'] = forms.ChoiceField(choices=get_operators())
            ns['value'] = forms.CharField()

        @classmethod
        def construct(cls):
            Form = types.new_class(
                cls.__name__,
                (forms.Form,),
                exec_body=cls._get_parameter_choices
            )
            return Form

    def _get_composer_formset(self, data=None) -> forms.BaseFormSet:
        FormSet = forms.formset_factory(self.RecipientsComposerForm.construct(), extra=0, max_num=1)
        return FormSet(data)

    def _render_composer(self, request, queryset):

        formset = self._get_composer_formset()

        composer = {
            'label': 'test',
            'formset': formset
        }

        extra = '' if settings.DEBUG else '.min'
        js = [
            'admin/js/vendor/jquery/jquery%s.js' % extra,
            'admin/js/jquery.init.js',
            'djangoFCM/generic/js/query-composer.js',
        ]
        css = {
            'all': [
                'djangoFCM/generic/css/query-composer.css',
            ]
        }
        context = {
            'notifications': queryset,
            'parameters': composer,
            'media': forms.Media(js=js, css=css)
        }

        return render(
            request=request,
            template_name='djangoFCM/admin/recipients_composer.html',
            context=context)

    def compose_recipients(self, request, queryset):

        if 'do_action' in request.POST:
            formset = self._get_composer_formset(request.POST)
            notifications = Notification.objects.filter(pk__in=request.POST.getlist('_selected_action'))

            if not formset.is_valid():
                raise Exception(formset.errors)

            data = [
                {
                    _field_name: form[_field_name].data
                    for _field_name in formset.empty_form.fields
                }
                for form in formset
            ]
            _p = re.compile(r'(.*)\((.*)\)\.(.*)')

            if len(data) == 1:
                condition = data[0]
                parameter_pk, contenttype_pk, field_name = re.findall(_p, condition['parameter'])[0]
                # parameter = Parameter.objects.get(pk=parameter_pk)
                contenttype = ContentType.objects.get(pk=contenttype_pk)
                pks = contenttype.model_class().objects\
                    .filter(**{field_name: condition['value']})\
                    .values_list('pk', flat=True)
                push_tokens = PushToken.objects.filter(
                    parameters__parameter__type__in=Parameter.ParameterTypes.FOREIGN_KEY,
                    parameters__value__in=pks,
                    parameters__content_type=contenttype,
                )
            else:
                raise NotImplementedError

            for notification in notifications:
                notification.recipients.set(push_tokens)
                notification.save()
                self.message_user(request, 'OK!', messages.SUCCESS)

            return

        if queryset.filter(sent=True).exists():
            self.message_user(
                request,
                'One of notifications is already sent! Selecct unsent notifications.',
                messages.ERROR)
            return

        return self._render_composer(request, queryset)

    compose_recipients.short_description = _('Compose recipients')

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

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.sent:
            return super().get_readonly_fields(request, obj) + ('title', 'body', 'recipients', 'send_on')

        return super().get_readonly_fields(request, obj)
