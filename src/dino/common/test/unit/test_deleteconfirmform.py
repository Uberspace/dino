import pytest

from ...views import DeleteConfirmForm


@pytest.fixture
def form_data(signed_example_com):
    return {
        'identifier': signed_example_com,
    }


@pytest.fixture
def delete_entity(mocker):
    return mocker.MagicMock()


def test_deleteconfirmform_missing_clean(form_data):
    f = DeleteConfirmForm(None, data=form_data)

    with pytest.raises(Exception) as excinfo:
        f.confirmed

    assert 'full_clean' in str(excinfo)


def test_deleteconfirmform_confirm_data_empty(form_data, delete_entity):
    f = DeleteConfirmForm(delete_entity, data=form_data)
    f.full_clean()
    assert not f.confirm_asked
    assert not f.confirmed
    delete_entity.assert_not_called()


def test_deleteconfirmform_confirm_data_no(form_data, delete_entity):
    form_data['confirm'] = 'false'
    f = DeleteConfirmForm(delete_entity, data=form_data)
    f.full_clean()
    assert f.confirm_asked
    assert not f.confirmed
    delete_entity.assert_not_called()


def test_deleteconfirmform_confirm_data_yes(form_data, delete_entity):
    form_data['confirm'] = 'true'
    f = DeleteConfirmForm(delete_entity, data=form_data)
    f.full_clean()
    assert f.confirm_asked
    assert f.confirmed
    delete_entity.assert_called_once_with('example.com.')
