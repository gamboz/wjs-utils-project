# WJS utilities

A bunch of django management commands for WJS/Janeway.

Useful during development.


## Install & use

This is a django app that should live inside Janeway. To use it, proceed as follows:

1. Activate your Janeway's virtual environment and install the package
   of this app (please see
   https://gitlab.sissamedialab.it/ml-foss/omlpi/-/packages)

2. Add "wjs\_mgmt\_cmds" to Janeway's INSTALLED\_APPS in `src/core/janeway\_global\_setting.py` like this::
```
INSTALLED_APPS = [
    ...
    'wjs_mgmt_cmds,
]
```

3. You should now see the new management commands as usual:
```
python manage.py help
```
