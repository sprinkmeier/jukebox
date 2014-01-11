#!/usr/bin/env python

"""
WSGI webapp using Flask
"""

from flask import Flask, redirect, render_template, url_for


from flask.ext.wtf import Form

from wtforms import TextField, validators

import collections
import glob
import os

app = Flask(__name__)


TEMPLATE = 'jukebox.html'

def fileList():
    ret = collections.OrderedDict()
    for pth in sorted(glob.glob('/var/jukebox/*')):
        ret[os.path.split(pth)[1]] = [os.path.split(x)[1] for x in sorted(glob.glob(os.path.join(pth,'*')))]

    return ret



@app.route('/')
def index():
    """Homepage"""

    return "Hello, linux.conf.au"


class RegoForm(Form):
    """A simple rego form"""

    email = TextField('Email')


@app.route('/register', methods=('GET', 'POST'))
def get_register():
    """Handle the registration form"""

    form = RegoForm()

    form.songs = fileList()

    if form.validate_on_submit():
        return "Success"

    return render_template(TEMPLATE, form=form)


@app.route('/a-redirect')
def a_redirect():
    """Redirect the user"""

    return redirect(url_for('a_template'))


@app.route('/a-template')
def a_template():
    """Render a template"""

    return render_template(TEMPLATE)


if __name__ == '__main__':
    app.secret_key = 'THIS IS REALLY SECRET (which should _NOT_ be stored in the code!!)'
    app.run(debug=True)
