import django.forms as forms
from django.contrib import messages
from django.core import signing
from django.http import Http404, HttpResponseNotAllowed, HttpResponseRedirect
from django.views.generic.edit import FormView

from pdnsadm.pdns_api import PDNSError


class SignedHiddenField(forms.CharField):
    widget = forms.HiddenInput

    def to_python(self, value):
        return signing.loads(value)


class DeleteConfirmForm(forms.Form):
    identifier = SignedHiddenField()
    confirm = forms.BooleanField(required=False)

    def __init__(self, delete_entity_func, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delete_entity = delete_entity_func

    @property
    def confirm_asked(self):
        return 'confirm' in self.data

    @property
    def confirmed(self):
        if not hasattr(self, 'cleaned_data'):
            raise Exception('call form.full_clean() before using DeleteConfirmForm.confirmed')

        return self.confirm_asked and self.cleaned_data['confirm']

    def _post_clean(self):
        if not self.errors and self.cleaned_data['confirm']:
            self.run_delete_entity(self.cleaned_data['identifier'])

    def run_delete_entity(self, identifier):
        try:
            self.delete_entity(identifier)
        except PDNSError as e:
            self.add_error(None, f'PowerDNS error: {e.message}')


class DeleteConfirmView(FormView):
    template_name = "common/delete_confirm.html"
    form_class = DeleteConfirmForm
    """ URL to redirect to after deletion or cancellation, see also get_redirect_url() """
    redirect_url = None

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(permitted_methods=['POST'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['delete_entity_func'] = self.delete_entity
        return kwargs

    def get_context_data(self, form):
        context = super().get_context_data()
        context['identifier'] = form.cleaned_data['identifier']
        return context

    def form_valid(self, form):
        if form.confirm_asked:
            identifier = form.cleaned_data['identifier']
            if form.confirmed:
                messages.success(self.request, self.get_success_message(identifier))
            return HttpResponseRedirect(self.get_redirect_url(identifier))
        else:
            return self.form_invalid(form)

    def get_success_message(self, identifier):
        return f'{identifier} has been deleted.'

    def get_redirect_url(self, identifier):
        if self.redirect_url:
            return self.redirect_url
        else:
            raise NotImplementedError()

    def delete_entity(self, pk):
        raise NotImplementedError()
