#!/usr/bin/python
import os
import glob
import datetime
import json
import flask
import BeautifulSoup

app = flask.Flask(__name__)
base_dir = os.path.dirname(os.path.abspath( __file__ ))

def file_exists_in_basedir(filename):
    return os.path.exists("%s/%s" % (base_dir, filename))

def read_json_from_basedir(filename):
    if not os.path.exists("%s/%s" % (app.root_path, filename)): return None
    with open("%s/%s" % (app.root_path, filename)) as f:
        return json.load(f)

def read_contents_from_basedir(filename):
    if not os.path.exists("%s/%s" % (app.root_path, filename)): return None
    with open("%s/%s" % (app.root_path, filename)) as f:
        return BeautifulSoup.BeautifulSoup(f.read())

@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/robots.txt')
def robots():
    return flask.send_from_directory(os.path.join(base_dir, 'static'),
                               'robots.txt', mimetype='text/plain')

@app.route('/<page_name>.html')
def page(page_name):
    contents = read_contents_from_basedir("%s.html" % (page_name))
    if contents == None: return "Not found", 404

    data = {}
    site_data = read_json_from_basedir("__site__.json")
    if site_data != None: data.update(site_data)
    page_data = read_json_from_basedir("%s.json" % page_name)
    if page_data != None: data.update(page_data)

    data["page_name"] = page_name
    data["contents"] = contents
    if not "template" in data:
        data["template"] = "page.html"

    return flask.render_template(data["template"],**data)

@app.route('/')
def index():
    return page("index")

def get_pages_and_entries(category_name):
    entries = []
    pages = {}
    files = glob.glob(os.path.join(app.root_path, category_name, "*.json"))
    for file in files:
        basename = os.path.splitext(os.path.basename(file))[0]
        if basename ==  "__category__" or basename == "index": continue
        entry_data = {}
        with open(file) as f:
            entry_data.update(json.load(f))
        entry_data["page_name"] = basename
        pages[basename] = entry_data
        if "pubDate" in entry_data: entries.append(entry_data)
    entries.sort(cmp=lambda x,y:cmp(x['pubDate'],y['pubDate']), reverse=True)
    return pages, entries

@app.route('/<category_name>/<page_name>.html')
def page_with_category(category_name, page_name):
    contents = read_contents_from_basedir("%s/%s.html" % (category_name, page_name))
    if contents == None: return "Not found", 404

    data = {}
    site_data = read_json_from_basedir("__site__.json")
    if site_data != None: data.update(site_data)
    category_data = read_json_from_basedir("%s/__category__.json" % category_name)
    if category_data != None: data.update(category_data)
    page_data = read_json_from_basedir("%s/%s.json" % (category_name, page_name))
    if page_data != None: data.update(page_data)


    if page_name == "index":
        data["pages"], data["entries"] = get_pages_and_entries(category_name)

    data["page_name"] = page_name
    data["category_name"] = category_name
    data["contents"] = contents
    if not "template" in data:
        data["template"] = "page.html"

    return flask.render_template(data["template"],**data)

@app.route('/<category_name>/<img_name>.png')
def image_with_category(category_name, img_name):
    return flask.send_file("%s/%s/%s.png" % (app.root_path, category_name, img_name), "image/png")

@app.route('/<category_name>/<page_name>/<img_name>.png')
def image_with_category2(category_name, page_name, img_name):
    return flask.send_file("%s/%s/%s/%s.png" % (app.root_path, category_name, page_name, img_name), "image/png")

@app.route('/<category_name>/')
def category_index(category_name):
    return page_with_category(category_name, "index")

if __name__ == '__main__':
    start = datetime.datetime.now()
    cnt = 0
    for file in glob.glob("*.json"):
        cnt += 1
        with open(file) as f: json.load(f)
    for file in glob.glob("*/*.json"):
        cnt += 1
        with open(file) as f: json.load(f)
    end = datetime.datetime.now()
    print "%d json files, parse time: %s" % (cnt, end - start)

    app.run(host='0.0.0.0',debug=True)
