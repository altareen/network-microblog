#!/usr/bin/env python

###
#-------------------------------------------------------------------------------
# manage.py
#-------------------------------------------------------------------------------
#
# Author:       Alwin Tareen
# Created:      May 28, 2021
#
# Venv setup:       python3 -m venv venv
# Venv activation:  source venv/bin/activate
#
# Check if Django is installed: python -m django --version
# Install Django:               pip install Django
#
# Run Django:   python manage.py runserver
# Conclusion:   deactivate
#
# If you make any changes to auctions/models.py run the following:
# python manage.py makemigrations
# python manage.py migrate
#
# This program implements a Twitter-like social network website.
#
# Submission instructions:
# Create a .gitignore file with the folliwng contents: venv/
# Move inside the folder that contains your project code and execute:
#
# git init
# git remote add origin https://github.com/me50/altareen.git
# git add -A
# git commit -m "Submit my project 4"
# git push origin main:web50/projects/2020/x/network
#
##

"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project4.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
