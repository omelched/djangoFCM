from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import JsonResponse, HttpRequest
from django.views.generic.list import BaseListView


class MetadataJsonView(BaseListView):
    """Handle DataComposer's requests for metadata."""
    paginate_by = None
    admin_site = None

    def get(self, request, *args, **kwargs):

        if not self.has_perm(request):
            raise PermissionDenied

        result = self.get_data()
        return JsonResponse(
            {
                'results': result
            },
            json_dumps_params={'indent': 2}
        )

    def get_data(self):
        _models = apps.get_models()
        result = [
            {
                'key': i,
                'name': _models[i].__name__,
                'fields': [
                    {
                        'key': ii,
                        'name': field.name,
                        'type': self.guess_type(field),
                        'attributes':
                            {
                                'to': field.related_model.__name__
                            } if self.guess_type(field) == 'foreign-key' else
                            {}
                    }
                    for ii, field in enumerate(_models[i]._meta._get_fields())
                ],
            }
            for i, model in enumerate(_models)
        ]

        return result

    @staticmethod
    def guess_type(field):
        if isinstance(field, models.ForeignKey):
            return 'foreign-key'
        return 'regular'

    def has_perm(self, request: HttpRequest):
        """Check if user has permission to access the related model."""
        return request.user and request.user.is_staff
