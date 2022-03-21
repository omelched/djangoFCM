from django.apps import apps
from django.core.exceptions import PermissionDenied, FieldDoesNotExist
from django.http import JsonResponse, HttpRequest
from django.views.generic.list import BaseListView


class DataFetcherJsonView(BaseListView):
    """Handle DataComposer's requests for data."""
    paginate_by = None

    def get(self, request, *args, **kwargs):

        if not self.has_perm(request):
            raise PermissionDenied

        self.model = self.process_request(request)
        return JsonResponse(
            {
                'results': [
                    {
                        'key': i.pk,
                        'name': str(i)
                    } for i in self.get_queryset()
                ]
            },
            json_dumps_params={'indent': 2}
        )
    @staticmethod
    def process_request(request: HttpRequest):
        try:
            model_name = request.GET['model_name']
            field_name = request.GET['field_name']
        except KeyError as e:
            raise PermissionDenied from e

        source_model = None
        all_models = apps.get_models()
        for _model in all_models:
            if _model.__name__ == model_name:
                source_model = _model
                break

        if not source_model:
            raise PermissionDenied

        try:
            source_field = source_model._meta.get_field(field_name)
        except FieldDoesNotExist as e:
            raise PermissionDenied from e
        try:
            remote_model = source_field.remote_field.model
        except AttributeError as e:
            raise PermissionDenied from e

        return remote_model

    def has_perm(self, request: HttpRequest):
        """Check if user has permission to access the related model."""
        return request.user and request.user.is_staff
