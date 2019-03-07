Zone Data
=========

Dino tries to mirror as little data as possible from PowerDNS. To enable
permission managment, dino stores a list of zone names within the database.
However, there is no permanent storage of the zone records. The zone list is
refreshed each time a user opens the zone list.

Modifications like creating zones or deleting records are always carried out
live via the PowerDNS API and are not synced later.

Modifcation outside dino
------------------------

Since dino has to store some of the PowerDNS data localy, there are some
currently some caveats when modifying data outside dino. We are working to
resolve most of them in future releaes.

* deleting zones outside of dino is not supported and will result in errors
* zones can be created outside dino and will be synced
* records can be created, changed and deleted outside dino and will be shown
* concurrent editing of the same zone from within inside and outside dino is not
  recommended due to the nature of the PowerDNS API. Assuming a small enough
  time window, some records might get lost.
