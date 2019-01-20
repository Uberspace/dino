from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.views.generic.base import TemplateView


class DeleteConfirmView(TemplateView):
    template_name = "zoneeditor/delete_confirm.html"
    """ name of the URL argument to use as the primary key """
    pk_name = 'pk'
    """ URL to redirect to after deletion or cancellation, see also get_redirect_url() """
    redirect_url = None

    def post(self, *args, **kwargs):
        if self.confirmed:
            self.delete_entity(self.identifier)
            messages.success(self.request, self.get_success_message())

        return HttpResponseRedirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['identifier'] = self.identifier
        return context

    @property
    def identifier(self):
        try:
            return self.kwargs[self.pk_name]
        except LookupError as ex:
            found_args = ','.join(self.kwargs.keys())
            if not found_args:
                found_args = 'none'
            raise Exception(f'expected request to have a kwarg "{self.pk_name}", but found {found_args}.') from ex

    @property
    def confirmed(self):
        return self.request.POST.get('confirm') == 'true'

    def get_success_message(self):
        return f'{self.identifier} has been deleted.'

    def get_redirect_url(self):
        if self.redirect_url:
            return self.redirect_url
        else:
            raise NotImplementedError()

    def delete_entity(self, pk):
        raise NotImplementedError()
