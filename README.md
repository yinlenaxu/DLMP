DLMP
==============================

TAED2Predicting faults from refactorings

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               
    │
    ├── models             
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to generate data and turn raw data into features for modeling
    │   │   └── make_dataset.py
    │   │
    │   ├── features       
    │   │   └── build_features.py
    │   │
    │   ├── models         
    │   │   │                 
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>

To run this project, there are three different steps you have to follow, all of them are make calls that will set up the repository and make it usable.

- First of all, to get all the libraries our project uses, call make requirements:

```sh
>> make requirements
```

- To set up the data and make it ready for its use, now call make data:

```shell
>> make data
```

- And now, to execute our deployment of the project, call make deploy:

```shell
>> make deploy
```

You will see now an interactive UI that will allow you to visualize a chart relating refactors and faults for each project.

To take a deeper look at the project and find all the work done, head to the notebooks directory and read them with your preferred notebook reader, we suggest Jupyter Notebook, but you can use any other one.
You will find 6 different notebooks, one for each step of the project.

1. Data Exploration, here you will find our first approach to the dataset and a bunch of different visualizations and prints to help the user to better understand the scope of the dataset.
2. Data Preparation, this is a way shorter notebook that preprocesses the data to make it more usable.
3. Text Analysis is the notebook used to analyse the commit messages of each project. Here we look for keywords and other common strategies for this kind of problem.
4. Statistical Tests is the notebook where we have done most of the mathematic and statistical work. Here you will find different tests we used to find the correlation between the refactors and the appearnce of faults. Also, you will find many different visualizations of the data and many other resources.
5. Modeling, in this short notebook we train and test the models explained in the memory of this project. We have used GLM, SVM and RF trying to predict if a refactor is going to induce a fault or not.
6. Visualization, in this last notebook you will find some scripts we used during the project and the generation of plots for the deployment of the app.

Besides all the content of this notebooks, we are also providing all the scripts used for the project at the directory "source". There you will find all the code classified on its kind and application.

To peak at the deployment code, head to "reports/deploy". We can differentiate between two different deploys in this area:

1. The first one is the one we actually are using. Check at "templates" and run the file index.html to open our application. It works with a local connection to the image database at "static/images".
2. However, we expect to have updates on the data since this Technical Debt Dataset is being improved all the time. To cover these updates, we also implemented a small Flask application that connects to the index.html and is capable of generating the new plots when the data changes. We have found that reading all the data and generating the new plots takes a lot of time (because there is a lot of data) and it's not worth it for the scope of this project, so notice that this Flask code is provided but not completely implemented into the index.html. If you're interested and want to make it work, contact the team members and we will explain you how to do it.