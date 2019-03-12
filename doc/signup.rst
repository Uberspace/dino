User Signup
===========

By default dino doesn't allow new users to sign up themselves. This means that
users have to be created manually, using a username and password. The login data
can then be passed to the user. Depending on your organisation, allowing the
right users to create accounts themselves might be required.

Enabling Signup
---------------

To enable users to create accounts themselves, add the ``DINO_ENABLE_EMAIL_SIGNUP`` setting
to your dino configuration (``/etc/dino.cfg``, or another location):

.. code-block:: ini

  # enable signup via email/password
  DINO_ENABLE_EMAIL_SIGNUP=True
  # and/or enable social signup, see below
  #DINO_ENABLE_SOCIAL_SIGNUP=True

.. warning::

  Please be aware that this enables anyone with access to dino to create new,
  permissionless accounts. This is probably not what you want. Continue to the
  next section to restrict signups.

Restricting Domains
-------------------

To combat the "everything can sign up"-siguration, you can restrict the mail
domains, which can be used to create new accounts. This applies to both
email/password accounts and social accounts. This can be used to only allow
signups from your company domain.

In ``/etc/dino.cfg`` (or wherever you configure your dino), add the following
and restart dino:

.. code-block:: ini

  DINO_VALID_SIGNUP_DOMAINS=example.com

The above configuration allows anyone with a ``...@example.com`` mail address to
create accounts.

Social Accounts
---------------

Dino utilizes `django-allauth <https://www.intenct.nl/projects/django-allauth/>`_
to enable login and signup using various providers. Most of them will not be of much
use in typical dino deployments; you might find Google, GitLab or OpenID useful,
if your organisation uses one of them for authentication interally.

We'll run through adding Google login to dino. The process is almost identical
for most other providers; take a look at the `allauth documentation <providers>`_
for your provider for details.

.. _`providers`: https://django-allauth.readthedocs.io/en/latest/providers.html

First, we need to load the `google provider`_. In ``/etc/dino.cfg``
(or wherever you configure your dino), add the following and restart dino:

.. code-block:: ini

  DINO_LOGIN_PROVIDERS=google
  # and optionally
  #DINO_ENABLE_SOCIAL_SIGNUP=True

.. _`google provider`: https://django-allauth.readthedocs.io/en/latest/providers.html#google

Now, continue with the django-allauth docs about `app registration`_, to create
a config at google and add it to dino. After those setps, the provider setup is
finished. 

.. _`app registration`: https://django-allauth.readthedocs.io/en/latest/providers.html#app-registration
