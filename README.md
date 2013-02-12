# Django-Perimeter

Perimeter is an app that provides middleware that allows you to 'secure the perimeter' of your django site outside of any existing auth process that you have.

## Why?

Most django sites have some kind of user registration and security model - a login process, decorators to secure certain URLs, user accounts - everything that comes with django.contrib.auth and associated apps (django-registration).

Sometimes, however, you want to simply secure the entire site to prevent prying eyes - the classic example being before a site goes live. You want to erect a secure perimeter fence around the entire thing. If you have control over your front-end web server (e.g. Apache, Nginx) then this can be used to do this using their in-built access control features. However, if you are running your app on a hosting platform you may not have admin access to these parts. Even if you do have control over your webserver, you may not want to be re-configuring it every time you want to grant someone access.

That's when you need Perimeter.

Perimeter provides simple tokenised access control over your entire Django site. It consists of two parts: admin site functionality to create new access tokens, and middleware to control the access based on said token.

## How does it work?

Once you have installed and enabled Perimeter, everyone requiring access will need an authorisation token (not authentication - there is nothing inherent in Perimeter to prevent people swapping / sharing tokens - that is an accepted use case).

To create a new token you need to head to the admin site, and create a new token under the Perimeter app. The token has a number of properties:

* Recipient email - tokens are bound to a single email address. This is never validated, however it allows us to log usage, just in case things get hairy down the line. (CYA)
* Expiry - tokens automatically expire after a certain period - set this to a date / time in the future.
* Token - this is the token that the user must append to the URL that they get. It is not auto-generated, but must be unique.

Once the user has the token (you'll need to give it to them yourself), they can visit the site. The Perimeter middleware, if enabled, will check a user's session for a token (and check that it's valid). If they do not have a valid token in the session, then Perimeter will check the querystring for a token argument. If it's found on the querystring, then it's validated (from db) and added to the user's session.

The first time that it's used in a session the usage is recorded, along with client IP and user agent (for reference purposes).

## Setup

1. Add 'django_perimeter' to your installed apps.
2. Add 'django_perimeter.middleware.PerimeterAccessMiddleware' to the list of MIDDLEWARE_CLASSES
3. Add PERIMETER_ENABLED=True to your settings file. This setting can be used to enable or disable Perimeter in different environments.
4. (optional) Add PERIMETER_SESSION_KEY setting to your settings file to override the default value of 'pt'.
