import os
import os.path
import shutil
import subprocess
import tempfile

from flask import Flask, jsonify, request
from jinja2 import Template

app = Flask(__name__)

TMPL_DIR = 'templates'
RASTER = 'output.js'
TMPL_INDEX = 'index.html'
CURRENT_PATH = os.path.abspath('.')
IMG_TAG_SRC = 'data:image/png;base64,{image}'


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


def _compose(img, template_name):
    tmpl_path = os.path.join(CURRENT_PATH, TMPL_DIR, template_name)
    # create temp files in template dir
    html = tempfile.NamedTemporaryFile(dir=tmpl_path)
    js = tempfile.NamedTemporaryFile(dir=tmpl_path)

    # copy contents of real files into temp files
    html.file.write(open(os.path.join(tmpl_path, TMPL_INDEX)).read())
    js.file.write(open(os.path.join(CURRENT_PATH, RASTER)).read())

    # update index.html.tmp, {{ dick_pic }}
    template_html = Template(html.read())
    img_tag = IMG_TAG_SRC.format(image=img)
    html.write(template_html.render(dick_pic=img_tag))

    # update output.js.tmp, {{ template_name }}
    template_js = Template(js.read())
    js.write(template_js.render(template_name=os.path.join(tmpl_path,
                                                           TMPL_INDEX)))

    # return temp files
    return html.name, js.name


def _generate_img(template, img):
    # make a template
    tmp_html, tmp_js = _compose(img, template)
    subprocess.Popen(['phantomjs', tmp_js],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT)
    # close tmp files
    tmp_html.close()
    tmp_js.close()


@app.route('/compose', methods=['POST'])
def compose():
    """ Compose image with template """
    img = request.form['img']
    template = request.form['template']
    return jsonify({'image': _generate_img(template, img)})


if __name__ == '__main__':
    app.run()
