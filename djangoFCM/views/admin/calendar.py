from datetime import datetime, timedelta
import calendar

from django.http import HttpRequest
from django.views import generic
from django.conf import settings
from django.forms import Media
from django.core.exceptions import PermissionDenied

from djangoFCM.models import Notification
from djangoFCM.src.calendar import DjangoCalendar


class CalendarView(generic.ListView):
    template_name = 'djangoFCM/admin/calendar.html'
    queryset = Notification.objects.all()

    def get(self, request, *args, **kwargs):
        if not self.has_perm(request):
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def has_perm(self, request: HttpRequest):
        """Check if user has permission to access the related model."""
        # return request.user and request.user.is_staff
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # use today's date for the calendar
        d = get_date(self.request.GET.get('month', None))

        # Instantiate our calendar class with today's year and date
        cal = DjangoCalendar(d.year,
                             d.month,
                             self.queryset.filter(send_on__month=d.month, send_on__year=d.year),
                             'send_on')
        context['calendar'] = cal.to_context()

        extra = '' if settings.DEBUG else '.min'
        js = [
            'admin/js/vendor/jquery/jquery%s.js' % extra,
            'admin/js/jquery.init.js',
        ]
        css = {
            'all': [
                'djangoFCM/admin/css/calendar.css',
            ]
        }
        context['media'] = Media(js=js, css=css)

        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context

        return context


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return datetime(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month
