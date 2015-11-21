import os
import os.path
import shutil
import subprocess
import argparse

from flask import Flask, jsonify, request, send_file
from jinja2 import Template

app = Flask(__name__)

TMPL_DIR = 'templates'
RASTER = 'output.js'
TMPL_INDEX = 'index.html'
CURRENT_PATH = os.path.abspath('.')


def _get_templates():
    """
    List templates in the dir

    Each template in dir:
    - should be in a separate directory which name will be used as a template
      name.
    - should have index.html file within the root of it's dir.
    - should provide all the assets needed
    - within index.html there should be a template tag {{ dick_pic }}

    """
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


def _make_jinja_template(path):
    with open(path) as file_path:
        return Template(file_path.read())


def _create_JS_for_phantom(template_name, img_url):
    tmpl_path = os.path.join(CURRENT_PATH, TMPL_DIR, template_name)

    # copy contents of real files into temp files
    js_path = os.path.join(CURRENT_PATH, 'output.js.copy')
    shutil.copy(os.path.join(CURRENT_PATH, RASTER), js_path)
    template_js = _make_jinja_template(js_path)

    # update output.js.tmp, {{ template_path }}
    with open(js_path, 'w') as js_file:
        js_file.write(template_js.render(
            template_path=os.path.join(tmpl_path, TMPL_INDEX)))

    return js_path


def _prepare_template(template_name, img_url):
    tmpl_path = os.path.join(CURRENT_PATH, TMPL_DIR, template_name)

    html_path = os.path.join(tmpl_path, 'index.html.copy')
    shutil.copy(os.path.join(tmpl_path, TMPL_INDEX), html_path)

    template_html = _make_jinja_template(html_path)

    # update index.html.tmp, {{ dick_pic }}
    with open(html_path, 'w') as html_file:
        html_file.write(template_html.render(dick_pic=img_url))


def _generate_img(template, img_url):
    _prepare_template(template, img_url)
    js = _create_JS_for_phantom(template, img_url)
    subprocess.call(['phantomjs', js],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
    return open(os.path.join(CURRENT_PATH, 'output.jpg'))


@app.route('/compose', methods=['POST'])
def compose():
    """ Compose image with template """
    img_url = request.form['img']
    template = request.form['template']
    return send_file(_generate_img(template, img_url))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("--debug", action="store_true", default=False)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", default=5000, type=int)
    args = p.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)
