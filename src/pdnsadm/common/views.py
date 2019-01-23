from django.contrib import messages
from django.http import Http404, HttpResponseNotAllowed, HttpResponseRedirect
from django.views.generic.base import TemplateView

from pdnsadm.pdns_api import PDNSError


class DeleteConfirmView(TemplateView):
    template_name = "common/delete_confirm.html"
    """ URL to redirect to after deletion or cancellation, see also get_redirect_url() """
    redirect_url = None

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(permitted_methods=['POST'])

    def post(self, request, *args, **kwargs):
        self.request = request

        if self.confirmed:
            success = self._run_delete()

            if success:
                return HttpResponseRedirect(self.get_redirect_url())
            else:
                return self._show_template()  # show error message
        elif self.confirmed is False:
            return HttpResponseRedirect(self.get_redirect_url())
        else:
            return self._show_template()  # no answer given yet, show yes/no

    def _run_delete(self):
        try:
            self.delete_entity(self.identifier)
        except PDNSError as e:
            messages.error(self.request, f'PowerDNS error: {e.message}')
            return False
        else:
            messages.success(self.request, self.get_success_message())
            return True

    def _show_template(self):
        return super().get(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['identifier'] = self.identifier
        return context

    @property
    def identifier(self):
        try:
            return self.request.POST['identifier']
        except LookupError as ex:
            found_args = ','.join(self.request.POST.keys())
            if not found_args:
                found_args = 'none'
            raise Exception(f'expected request to have POST field "identifier", but found {found_args}.') from ex

    @property
    def confirmed(self):
        try:
            return self.request.POST['confirm'] == 'true'
        except LookupError:
            return None

    def get_success_message(self):
        return f'{self.identifier} has been deleted.'

    def get_redirect_url(self):
        if self.redirect_url:
            return self.redirect_url
        else:
            raise NotImplementedError()

    def delete_entity(self, pk):
        raise NotImplementedError()
