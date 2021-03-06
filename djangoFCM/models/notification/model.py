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

import json

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import PeriodicTask, ClockedSchedule
from django.utils import timezone
from django.db.models.signals import m2m_changed, post_delete
from django.dispatch import receiver
from picklefield import PickledObjectField
from django.contrib.auth import get_user_model

from djangoFCM.models.notification.manager import Manager
from djangoFCM.models.push_token import PushToken
from djangoFCM.src import fcm_app, hms_app


class Notification(models.Model):
    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        constraints = []

    name = models.CharField(
        max_length=63,
        null=False,
        blank=False,
        unique=True,
        editable=True,
        verbose_name=_('name'),
    )
    title = models.CharField(
        max_length=63,
        null=False,
        blank=True,
        editable=True,
        verbose_name=_('title'),
    )
    body = models.CharField(
        max_length=255,
        null=False,
        blank=True,
        editable=True,
        verbose_name=_('body'),
    )
    recipients = models.ManyToManyField(
        PushToken,
        related_name='notifications',
        verbose_name=_('recipients'),
        blank=True,
    )
    recipients_composer_conditions = PickledObjectField(
        null=True,
        verbose_name=_('recipients composer conditions'),
    )
    __original_send_on = None
    send_on = models.DateTimeField(
        null=False,
        blank=True,
        editable=True,
        verbose_name=_('send on date'),
    )
    sent = models.BooleanField(
        null=False,
        blank=False,
        verbose_name=_('is sent'),
        default=False,
    )
    creation_date = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False,
        verbose_name=_('creation date'),
    )
    task = models.OneToOneField(
        PeriodicTask,
        models.SET_NULL,
        related_name='notification',
        null=True,
        verbose_name=_('task')
    )
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        related_name='notifications',
        null=True,
        blank=True,
        editable=False,
        verbose_name=_('author'),
    )

    objects = Manager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_send_on = self.send_on

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        if self.task and self.send_on != self.__original_send_on:
            # 'send_on' was changed, therefore task is obsolete
            self.task.delete()
            self.task = None

        super().save(force_insert, force_update, using, update_fields)
        self.__original_send_on = self.send_on

    def compile_recipients(self):
        if not self.recipients_composer_conditions:
            self.recipients.clear()
            return

        if len(self.recipients_composer_conditions) == 1:
            condition = self.recipients_composer_conditions[0]
            self.recipients.set(
                PushToken.objects.filter(
                    **{
                        condition['attribute']: condition['value']
                    }
                )
            )
        else:
            raise NotImplementedError

    def send(self):

        (FCM_tokens, HMS_tokens) = (
            list(self.recipients.filter(application__messaging_service='F').values_list('push_token', flat=True)),
            list(self.recipients.filter(application__messaging_service='H').values_list('push_token', flat=True)),
        )
        kwargs = {k: v for k, v in self.arguments.all().values_list('key', 'value')}

        if FCM_tokens:
            fcm_app.notify_multiple_devices(
                registration_ids=FCM_tokens,
                message_title=self.title,
                message_body=self.body,
                extra_notification_kwargs=kwargs,
            )
        if HMS_tokens:
            hms_app.notify_multiple_devices(
                registration_ids=FCM_tokens,
                message_title=self.title,
                message_body=self.body,
                data=kwargs,
            )

        self.send_on = timezone.now()
        self.sent = True
        self.save()


@receiver(post_delete, sender=Notification)
def notification_deleted_handler(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()


@receiver(m2m_changed, sender=Notification.recipients.through)
def recipients_changed_handler(sender, instance, action, reverse, pk_set, **kwargs):
    def _add_task(_instance: Notification):
        clock, _ = ClockedSchedule.objects.get_or_create(
            clocked_time=_instance.send_on
        )

        task = PeriodicTask.objects.create(
            name=f'Send {_instance.name}(pk={_instance.pk})',
            task=f'djangoFCM.tasks.send_push_notification',
            clocked=clock,
            one_off=True,
            kwargs=json.dumps({
                'notification_pk': _instance.pk
            })
        )
        _instance.task = task

        _instance.save()
        # save to set 'task' value

    def _delete_task(_instance: Notification):
        if _instance.task:
            _instance.task.delete()
            _instance.task = None
            _instance.save()

    if not reverse:
        if action == 'post_add':
            if not instance.sent and not instance.task:
                _add_task(instance)

        elif action == 'post_remove':
            if not instance.recipients.exists():
                _delete_task(instance)

        elif action == 'post_clear':
            _delete_task(instance)
    else:
        if action == 'post_add':
            notifications = instance.notifications.filter(
                sent=False,
                task__isnull=True,
            )
            for notification in notifications:
                _add_task(notification)

        if action == 'post_remove':
            # if some m2m were removed (reverse relation)
            no_push_notifications = Notification.objects.filter(
                pk=pk_set,  # select notifications relations to which were removed
                recipients=None,  # if no recipients left
                sent=False,  # and they are not already sent
                task__isnull=False,  # and task still exists
            )

            for notification in no_push_notifications:
                _delete_task(notification)

        if action == 'pre_clear':
            # if all m2m are being cleared (reverse relation)
            no_push_notifications = instance.notifications.annotate(rec_count=models.Count('recipients')).filter(
                rec_count__lte=1,  # notifications, relations to which to-be-cleared, if that will be last push
                sent=False,  # and they are not already sent
                task__isnull=False,  # and task still exists
            )

            for notification in no_push_notifications:
                _delete_task(notification)


class NotificationArgument(models.Model):
    class Meta:
        verbose_name = _('notification argument')
        verbose_name_plural = _('notifications\' arguments')
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'notification',
                    'key',
                ),
                name='unique notification and key',
            ),
        )

    notification = models.ForeignKey(
        Notification,
        models.CASCADE,
        related_name='arguments',
        null=False,
        verbose_name=_('notification'),
    )
    key = models.CharField(
        max_length=255,
        null=False,
        blank=True,
        editable=True,
        verbose_name=_('key'),
    )
    value = models.CharField(
        max_length=255,
        null=False,
        blank=True,
        editable=True,
        verbose_name=_('value'),
    )
