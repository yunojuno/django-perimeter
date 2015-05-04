Django Perimeter
================

Perimeter is an app that provides middleware that allows you to 'secure the perimeter' of your django site outside of any existing auth process that you have.

Why?
----

Most django sites have some kind of user registration and security model - a login process, decorators to secure certain URLs, user accounts - everything that comes with django.contrib.auth and associated apps (django-registration).

Sometimes, however, you want to simply secure the entire site to prevent prying eyes - the classic example being before a site goes live. You want to erect a secure perimeter fence around the entire thing. If you have control over your front-end web server (e.g. Apache, Nginx) then this can be used to do this using their in-built access control features. However, if you are running your app on a hosting platform you may not have admin access to these parts. Even if you do have control over your webserver, you may not want to be re-configuring it every time you want to grant someone access.

That's when you need Perimeter.

Perimeter provides simple tokenised access control over your entire Django site. It consists of two parts: admin site functionality to create new access tokens, and middleware to control the access based on said token.

How does it work?
-----------------

Once you have installed and enabled Perimeter, everyone requiring access will need an authorisation token (not authentication - there is nothing inherent in Perimeter to prevent people swapping / sharing tokens - that is an accepted use case).

To create a new token you need to head to the admin site, and create a new token under the Perimeter app. If you have ``PERIMETER_ENABLED`` set to True already you won't be able to access the admin site (it covers everything except for the perimeter 'gateway' form), and so there is a management command (``create_access_token``) that you can use to create your first token. (This is analagous to the Django setup process where it prompts you to create a superuser.)

If someone visits any page on the site they will be redirected to the 'Gateway' page where they need to input the token, and their details (for auditing purposes). Once set the token is stored in their session and they can then access the site as normal.

Setup
-----

1. Add 'perimeter' to your installed apps.
2. Add 'perimeter.middleware.PerimeterAccessMiddleware' to the list of MIDDLEWARE_CLASSES
3. Add PERIMETER_ENABLED=True to your settings file. This setting can be used to enable or disable Perimeter in different environments.
