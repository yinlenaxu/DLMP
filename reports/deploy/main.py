from flask import Flask, render_template, redirect, url_for, request, flash, make_response, send_from_directory, abort, jsonify, Response, send_file
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib as matplotlib
import io
import pandas as pd
import os
import sys
sys.path.append('../../src/visualization/')
import visualize as viz

images_folder = os.path.join('static')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = images_folder


proj_refactor = None
proj_fault = None

@app.route('/app/', methods=["GET"])

@app.route('/')
def index():
    global proj_fault, proj_refactor
    refactoring_miner = pd.read_csv("../../data/interim/refactoring_miner.csv", encoding='utf8', engine='python')
    szz_fault_inducing_commits = pd.read_csv("../../data/interim/szz_fault_inducing_commits.csv", encoding='utf8', engine='python')
    fault_commits = pd.read_csv("../../data/processed/fault_commits.csv", encoding='utf8', engine='python')
    fault_commits = fault_commits[fault_commits["FAULT_INDUCING_COMMIT_HASH"].isin(szz_fault_inducing_commits["FAULT_INDUCING_COMMIT_HASH"])]
    proj_refactor = viz.get_project_refactor(refactoring_miner)
    proj_fault = viz.get_project_faults(refactoring_miner, szz_fault_inducing_commits, fault_commits)
    print("Data has been loaded")

    return render_template('index.html')


@app.route('/plot/<project>', methods=['POST'])
def appHandler(project):
    global proj_refactor, proj_fault
    project_id = 'org.apache:' + project
    refact = pd.Series(pd.DataFrame(proj_refactor)[project_id], name="Refactor")
    faults = pd.Series(pd.DataFrame(proj_fault)[project_id], name="Faults")
    matplotlib.use('agg')

    pd.concat([refact, faults], axis=1).plot(kind='bar', figsize=(18,7), rot=75, width=0.65, fontsize=17, color=('cornflowerblue','gold'),edgecolor = 'silver')
    plt.title(project, fontsize=20)

    plt.legend(fontsize=20)
    dir = './static/' + project + '.jpg'

    plt.savefig(dir) #save to the images directory

    return render_template('index.html', image_source=dir)