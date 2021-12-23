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

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from djangoFCM.models.push_token.manager import Manager


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
    application = models.ForeignKey(
        settings.DJANGOFCM_APPLICATION_MODEL,
        models.CASCADE,
        related_name='push_tokens',
        null=False,
        verbose_name=_('application')
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
    def short_token(self):
        if len(self.push_token) > 12:
            return f'{self.push_token[:6]}...{self.push_token[-6:]}'
        else:
            return self.push_token
