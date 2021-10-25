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
from django.contrib.contenttypes.models import ContentType


class Parameter(models.Model):
    class ParameterTypes(models.TextChoices):
        NUMBER = 'N', _('number')
        STRING = 'S', _('string')
        FOREIGN_KEY = 'F', _('foreign key')
        CHOICE = 'C', _('choice')

    name = models.CharField(
        primary_key=True,
        max_length=63,
        blank=False,
        verbose_name=_('name')
    )
    type = models.CharField(
        null=False,
        blank=False,
        max_length=1,
        choices=ParameterTypes.choices,
        editable=True,
        verbose_name=_('type'),
    )
    content_types = models.ManyToManyField(
        ContentType,
        related_name='used_in_parameters',
        verbose_name=_('content types'),
        blank=True,
    )

    objects = models.Manager()

    class Meta:
        verbose_name = _('parameter')
        verbose_name_plural = _('parameters')
        constraints = []

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)

    def guess_content_type(self, fk: str):
        assert self.type == Parameter.ParameterTypes.FOREIGN_KEY, ValueError
        assert fk, ValueError

        queryset = self.content_types.all()

        assert queryset.exists(), ValueError
        if queryset.count() == 1:
            return queryset.first()

        assert all([
            issubclass(content_type.model_class().pk, models.UUIDField) for content_type in queryset
        ]), ValueError

        for content_type in queryset:
            try:
                content_type.get_object_for_this_type(pk=fk)
                return content_type
            except content_type.model_class().DoesNotExist:
                continue

        raise ValueError


class ParameterChoices(models.Model):
    parameter = models.ForeignKey(
        Parameter,
        models.CASCADE,
        related_name='choices',
        null=False,
        verbose_name=_('parameter')
    )
    choice = models.CharField(
        max_length=63,
        blank=False,
        null=False,
        verbose_name=_('choice'),
    )

    objects = models.Manager()

    class Meta:
        verbose_name = _('parameter and choice')
        verbose_name_plural = _('parameters and choices')
        constraints = [
            models.UniqueConstraint(
                fields=['parameter', 'choice'],
                name='unique parameter and choice',
            )
        ]
