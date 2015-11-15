import os

from flask import Flask, jsonify

app = Flask(__name__)

TMPL_DIR = 'templates'


def _get_templates():
    """ List templates in the dir """
    try:
        return os.listdir(TMPL_DIR)
    except OSError:
        return []


@app.route('/templates')
def template_list():
    """ Return list of templates """
    return jsonify({'templates': _get_templates()})


@app.route('/compose', methods=['POST'])
def compose():
    """ Compose image with template """
    return jsonify({'image': ''})


if __name__ == '__main__':
    app.run()
