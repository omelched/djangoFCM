import pytz
from calendar import Calendar, month_name, day_name

from django.utils import timezone


class DjangoCalendar(Calendar):
    year = None
    month = None
    queryset = None
    date_lookup_name = None

    def get_event_kwargs(self, event):
        return {}

    def __init__(self, year, month, queryset, date_lookup_name) -> None:
        super().__init__()

        self.year = year
        self.month = month
        self.queryset = queryset
        self.date_lookup_name = date_lookup_name

    def monthdays2calendar_with_events(self, _year, _month):
        weeks = self.monthdays2calendar(_year, _month)

        _month_events = []

        for week in weeks:
            _week_events = []
            for day in week:
                _daily_events = [
                    {
                        'time': timezone.localtime(event.send_on, pytz.timezone('Europe/Moscow')).strftime('%H:%M'),
                        'title': event.title or event.name,
                        'body': event.body,
                        'is_sent': event.sent,
                        'kwargs': self.get_event_kwargs(event),
                    }
                    for event in self.queryset.filter(**{f'{self.date_lookup_name}__day': day[0]})
                ]
                _week_events.append((day[0] or None, _daily_events))
            _month_events.append(_week_events)

        return _month_events

    def to_context(self):
        ctx = {
            'month_name': f'{month_name[self.month]} {self.year}',
            'weekdays': [day_name[weekday] for weekday in self.iterweekdays()],
            'weeks': self.monthdays2calendar_with_events(self.year, self.month),
        }

        return ctx
