Users & Tenants
===============

Dino has a basic multi-tenancy feature, which allows you to create users and
give them access to a subset of the available domains. You can also use admin
accounts instead, if this functionality is not needed.

Users
-----

Dino knows a couple kinds of users:

* admin users, has full access to all zones
* tenant users, has access to associated zones only

During the setup guide a single administrator user was created. You can use this
account to log into dino. Further users should be created using the web
interface. Visit ``/admin/auth/user`` and use the "Add User" button to create
new users. They can later be associated with a tenant.

Tenants
-------

By default, there are no tenants created. Visit ``/admin/tenants/tenant`` in the
web interface to create your first one. During creation process you can add
users and zones to the new tenant.

Users may have one of the following permission levels:

* tenant users:

  * cannot delete or create zones
  * can create/edit/delete records in associated zones

* tenant admins:

  * can create or delete zones
  * can create/edit/delete records in associated zones

Tenants admins can currently not add new users themselves.
