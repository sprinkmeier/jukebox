#!/usr/bin/env python

"""
WSGI webapp using Flask
"""

from flask import Flask, redirect, render_template, url_for


from flask.ext.wtf import Form

from wtforms import TextField, validators

import collections

app = Flask(__name__)


TEMPLATE = 'jukebox.html'


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

    form.letters = "ABCD"
    form.songs = {'A': ["ABC","DEF","GHJ","JKL",],
                  'B': [],
                  'C': [],
                  'D': ["xyz","stu"],
                  'E': ["lmn","opq"],
                  }
#    form.songs = ["ABC","DEF","GHJ","JKL",]

    form.songs = collections.OrderedDict()

    form.songs['A'] = ["ABC","DEF","GHJ","JKL",]
    form.songs['B'] = []
    form.songs['C'] = []
    form.songs['D'] = ["xyz","stu"]
    form.songs['E'] = ["lmn","opq"]


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
