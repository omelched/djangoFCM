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

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.forms import ValidationError

from .manager import Manager
from ..parameter import Parameter


class PushToken(models.Model):
    push_token = models.CharField(
        primary_key=True,
        max_length=255,
        blank=False,
        verbose_name=_('push token'),
    )
    user = models.ForeignKey(
        get_user_model(),
        models.CASCADE,
        related_name='push_tokens',
        null=False,
        verbose_name=_('user'),
    )
    creation_date = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False,
        verbose_name=_('creation date'),
    )
    update_date = models.DateTimeField(
        auto_now=True,
        blank=False,
        null=False,
        verbose_name=_('update date'),
    )

    objects = Manager()

    class Meta:
        verbose_name = _('push token')
        verbose_name_plural = _('push tokens')

    @property
    def shorty(self):
        if len(self.push_token) > 12:
            return f'{self.push_token[:6]}...{self.push_token[-6:]}'
        else:
            return self.push_token

    def set_parameters(self, data: dict):
        self.parameters.all().delete()

        for parameter in data:
            self.parameters.create(
                parameter=parameter,
                value=data[parameter]
            )


class PushTokenParameters(models.Model):
    push_token = models.ForeignKey(
        PushToken,
        models.CASCADE,
        related_name='parameters',
        null=False,
        verbose_name=_('push token')
    )
    parameter = models.ForeignKey(
        Parameter,
        models.CASCADE,
        related_name='push_tokens',
        null=False,
        verbose_name=_('parameter')
    )
    value = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        verbose_name=_('value'),
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('content type'),
    )
    ref = GenericForeignKey(
        'content_type',
        'value'
    )

    objects = models.Manager()

    class Meta:
        verbose_name = _('push token parameter')
        verbose_name_plural = _('push token parameters')
        constraints = [
            models.UniqueConstraint(
                fields=['push_token', 'parameter', 'value'],
                name='unique parameter value at token',
            )
        ]

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.parameter.type == Parameter.ParameterTypes.FOREIGN_KEY and not self.content_type:
            try:
                self.content_type = self.parameter.guess_content_type(self.value)
            except ValueError:
                raise ValidationError

        super().save(force_insert, force_update, using, update_fields)
