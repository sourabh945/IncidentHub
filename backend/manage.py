#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys

def main():
    """Run administrative tasks."""
    # adding settings based upon the ENVIRONMENT variable
    Environment = os.environ.get("ENV")
    if Environment == "test":
        print("\n[Running in Testing mode]")
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.testing")
    elif Environment == "dev":
        print("\n[Running in development mode]")
        os.environ.setdefault("DJANGO_SETINGS_MODULE", "config.settings.development")
    else:
        print("\n[Running in production mode]")
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
