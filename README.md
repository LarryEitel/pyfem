pyfem
##############

python flask elasticsearch mongoengine web/api sandbox

Key Services and Tools
============

    python
    mongodb
    flask
    elasticsearch
    mongoengine

Make it run!
============

To make it run, you just have to do something like::

    cd into a python projects directory 
    git clone git@github.com:LarryEitel/pyfem.git
    cd pyfem
    virtualenv venv

Create a local_settings to override for your environment

    cp settings.py local_settings.py

This is a windows hack to set some paths, etc. You may need to adjust for your Windows environment.

    activate.cmd

Non-Windows users:

    source venv/bin/activate
    cd pyfem

    pip install -r requirements.txt

Run tests:
    python -m unittest discover

Run the application:

    python run.py

Developer Notes
===============

If you use WingWare IDE (Highly recommended), here are some useful settings for debugging:

Project/Project Settings

    Environment
        Python Path (Added):
            c:\Users\Larry\__prjs\pyfem\venv\Lib\site-packages
            c:\Users\Larry\__prjs\pyfem
    Debug
        Main Debug File:
            c:\Users\Larry\__prjs\pyfem\pyfem\run.py
        Initial Directory:
            c:\Users\Larry\__prjs\pyfem\pyfem
        Python Options (set testing ON, see pyfem.run.main)
            -t