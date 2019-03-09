import django.forms as forms
from django.contrib import messages
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormView

from dino.pdns_api import PDNSError

from .fields import SignedHiddenField


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
            self.add_error(None, _('PowerDNS error: {}').format(e.message))


class DeleteConfirmView(FormView):
    """
    Delete something, but ask the user for confirmation first. It has able to
    pass arbitrary data from the "delete"-button, through confirmation to the
    actual delete function. The data is protected by djangos signing feature.

    Flow:
      1. User clicks delete <button> on unrelated page
      2. <form> sends to request to your DeleteConfirmForm derivative
         passes along a signed primary key in POST[identifier].
      3. DeleteConfirmForm check for the presence of POST[confirm]
        3a. DeleteConfirmForm asks user for confirmation
        3b. user confirms
      4. DeleteConfirmForm calls your `delete_entity()`
      5. DeleteConfirmForm redirects to `redirect_url`

    To use this class, first create a view inheriting from this one:

        class RecordDeleteView(DeleteConfirmView):
            redirect_url = None  # see get_redirect_url()

            def delete_entity(self, identifier):
                # actually delete the object identified by `identifier`
                # at this point the View has made sure that this deletion has
                # been requested using POST and that the user as confirmed the
                # deletion.
                #
                # This method can also be used for last-minute permission
                # checks. Raise a django.core.exceptions.PermissionDenied().
                #
                # required.

            def get_redirect_url(self, rr):
                # URL to redirect to after successful deletion or cancelation.
                # if the deletion failed, the confirmation form is shown again,
                # along with an error message.
                # Alternatively a static URL can be provided in redirect_url.
                #
                # required.

            def get_display_identifier(self, identifier):
                # return a human-readable representation of `identifier`
                # used to ask the user for confirmation.
                #
                # optional, default: the identifier itself.

            def get_success_message(self, identifier):
                # message to show when the
                #
                # optional, default: '... has been deleted.'
                #           using get_display_identifier()

    Register your view under some URL (e.g. `/resource/delete`). Then, place a
    delete button somewhere like so:

        {% load deleteconfirm %}
        <form action="/resource/delete" method="POST">
            {% csrf_token %}
            <input type="hidden" name="identifier" value="{{ obj.pk|sign }}">
            <button type="submit" class="button tiny alert">{% trans 'delete' %}</button>
        </form>
    """

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
        context['identifier'] = self.get_display_identifier(form.cleaned_data['identifier'])
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
        identifier = self.get_display_identifier(identifier)
        return _('{} has been deleted.').format(identifier)

    def get_redirect_url(self, identifier):
        if self.redirect_url:
            return self.redirect_url
        else:
            raise NotImplementedError()

    def get_display_identifier(self, identifier):
        return identifier

    def delete_entity(self, pk):
        raise NotImplementedError()
