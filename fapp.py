import os
import os.path

from flask import Flask, jsonify

app = Flask(__name__)

TMPL_DIR = 'templates'


def _get_templates():
    """ List templates in the dir """
    try:
        return os.listdir(TMPL_DIR)
    except OSError:
        if not os.path.exists(TMPL_DIR):
            os.mkdir(TMPL_DIR)
        # it is empty at this point anyway
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
