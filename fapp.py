import os
import os.path
import subprocess

from flask import Flask, jsonify, request

app = Flask(__name__)

TMPL_DIR = 'templates'
RASTER = 'rasterize.js'


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


def _compose(img, template):
    # update jinja template, insert img to a tag
    return template


def _generate_img(template):
    output_img = None
    pipe = subprocess.Popen(
        ['phantomjs', '/dev/stdin', template, output_img],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    stdout, stderr = pipe.communicate(input=RASTER)
    if pipe.returncode != 0:
        raise RuntimeError(
            "PhantomJS didn't execute successfully - STDOUT: %s STDERR: %s" % (
                stdout, stderr))
    return output_img


@app.route('/compose', methods=['POST'])
def compose():
    """ Compose image with template """
    img = request.json['img']
    template = request.json['template']
    # make a template
    new_template = _compose(img, template)
    return jsonify({'image': _generate_img(new_template)})


if __name__ == '__main__':
    app.run()
