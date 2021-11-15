import flask
from flask import request
import json
import os
import pandas as pd
import re
from pathlib import Path

app = flask.Flask(__name__)
app.config["DEBUG"] = True

path = Path(os.getcwd())
parent = path.parent.absolute()

db_path = "/wis-advanced-python-2021-2022/students/"

json_list = os.listdir(str(parent)+db_path)
list_students = []
for file in json_list:
    json_file = str(parent)+db_path+file
    with open(json_file) as f: # go over json files and append them to list of dictionaries
        json_dict = json.load(f)
        list_students.append(json_dict)
df = pd.DataFrame(list_students)   # convert to dataframe

@app.route("/")
def index():
    return '<a href="/engine">Search Engine</a>'

@app.route("/engine", methods=['GET'] ) # create first page
def engine():
    return '''<form method="POST" action="/engine">
        <input name="gmail">
        <input type="submit" value="Go">
        </form>'''

@app.route("/engine", methods=['POST'] )
def engine_post():
    search = request.form.get('gmail') # get the input
    search = str(search) # convert to str
    dfstr = df.astype(str, copy=True, errors='raise') # create a parallar dataframe where everything is a string (searchable)
    r = re.compile(r'.*('+search+').*',re.IGNORECASE) # the regex to look for. case insensitive
    dfs = df[dfstr.applymap(lambda x: bool(r.match(x))).any(axis=1)] # This will return a dataframe with only the relevant rows
    names = list(dfs['name']) # get only names from the relevant rows
    names.sort()
    # iterate through items and format the result as an html site
    result = ['<a href="http://127.0.0.1:5000/engine/{}">{}</a>'.format(a,a) for a in names]
    return("<p>" + "</p><p>".join(result)) # format as a list

@app.route('/engine/<path:name>') # the name of the site is as the studnt's name
def sum_route(name):
    new_df = df[df['name']==name].T.dropna().reset_index() # create a dataframe from the student's info
    new_df['joined'] = new_df.apply(lambda x: ':'.join(x.dropna().values.tolist()), axis=1)
    result = new_df['joined'].tolist() # create a list of info saparated by ':'
    return("<p>" + "</p><p>".join(result)) # return as a list
    