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

from djangoFCM.models.push_token.manager import Manager


class Application(models.Model):
    name = models.CharField(
        max_length=63,
        blank=False,
        verbose_name=_('name'),
        unique=True,
    )

    objects = Manager()

    class Meta:
        verbose_name = _('application')
        verbose_name_plural = _('applications')
        swappable = 'DJANGOFCM_APPLICATION_MODEL'

    def __str__(self):
        return self.name
