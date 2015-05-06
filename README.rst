Django Perimeter
================

Perimeter is a Django app that provides middleware that allows you to 'secure the perimeter' of your django site outside of any existing auth process that you have.

Why?
----

Most django sites have some kind of user registration and security model - a login process, decorators to secure certain URLs, user accounts - everything that comes with django.contrib.auth and associated apps (django-registration).

Sometimes, however, you want to simply secure the entire site to prevent prying eyes - the classic example being before a site goes live. You want to erect a secure perimeter fence around the entire thing. If you have control over your front-end web server (e.g. Apache, Nginx) then this can be used to do this using their in-built access control features. However, if you are running your app on a hosting platform you may not have admin access to these parts. Even if you do have control over your webserver, you may not want to be re-configuring it every time you want to grant someone access.

That's when you need Perimeter.

Perimeter provides simple tokenised access control over your entire Django site (everything, including the admin site and login pages).

How does it work?
-----------------

Once you have installed and enabled Perimeter, everyone requiring access will need an authorisation token (not authentication - there is nothing inherent in Perimeter to prevent people swapping / sharing tokens - that is an accepted use case).

Perimeter runs as middleware that will inspect the user's ``session`` for a
token. If they have a valid token, then they continue to use the site uninterrupted. If they do not have a token, or the token is invalid (expired or set to inactive), then they are redirected to the Perimeter 'Gateway', where they must enter a valid token, along with their name and email (for auditing purposes - this is stored in the database).

To create a new token you need to head to the admin site, and create a new token under the Perimeter app. If you have ``PERIMETER_ENABLED`` set to True already you won't be able to access the admin site (as Perimeter covers everything except for the perimeter 'gateway' form), and so there is a management command (``create_access_token``) that you can use to create your first token. (This is analagous to the Django setup process where it prompts you to create a superuser.)

Setup
-----

1. Add 'perimeter' to your installed apps.
2. Add 'perimeter.middleware.PerimeterAccessMiddleware' to the list of MIDDLEWARE_CLASSES
3. Add the perimeter urls - NB must use the 'perimeter' namespace
4. Add PERIMETER_ENABLED=True to your settings file. This setting can be used to enable or disable Perimeter in different environments.


Settings:

.. code:: python

    PERIMETER_ENABLED = True

    INSTALLED_APPS = (
        ...
        'perimeter',
        ...
    )

    # perimeter must appear after sessions middleware as it relies on there
    # being a valid request.session
    MIDDLEWARE_CLASSES = [
        ...
        'django.contrib.sessions.middleware.SessionMiddleware',
        'perimeter.middleware.PerimeterAccessMiddleware',
        ...
    ]

Site urls:

.. code:: python

    # in site urls
    urlpatterns = patterns(
        '',
        ...
        # NB you must include the namespace, as it is referenced in the app
        url(r'^perimeter/', include('perimeter.urls', namespace='perimeter')),
        ...
    )

Tests
-----

The app has a suite of tests, and a ``tox.ini`` file configured to run them when using ``tox`` (recommended).
