# Cadet: Asset Management for spaCy Language Models

![](https://i.imgur.com/yhTiX7G.jpeg)<!-- .element: style="width:70%; background: #222222; border:0; box-shadow:none;" -->

## What is Cadet?

Cadet is a web app for creating custom language objects for spaCy.

- **Goal**: To provide an easy-to-use tool that enables non-technical users to start leveraging the power of natural language processing (NLP) in their research projects.
- **Context**: CLS Infra + DARIAH-Princeton Workshop Series "NLP 4 New Languages" (funded by the NEH)

## New Languages for spaCy?

- before you can train your model on annotated data, you need some data to begin with
- spaCy language object contains multiple linguistic assets, not just an annotated corpus
- spaCy offers models for many languages, but starting from scratch is not easy

![Скриншот 2019-11-20 19.48.27](https://i.imgur.com/7e7B8Pc.png)

## Why Cadet?

- **Accessibility:** Makes the collection and processing of langauge assets accessible to humanists without a background in programming or data science.
- **Customization:** Allows users to tailor language data to their specific needs and research domains.
- **Efficiency:** Streamlines the process of creating amd processing language assets for new spaCy language models

## Two flavors of Cadet

- **Stand-alone web app**: User-friendly GUI with an intuitive design that simplifies model creation and customization.
- **Jupyter Notebook**: More flexible than the stand-alone web app but requires a knowledge of Python

## How does it work?

- it takes the user through seven individual steps

![](https://i.imgur.com/QeBW6GO.png) <!-- .element: style="width:70%; border:none; background: none" -->

### 1. Create a New Language Object

Building from spaCy's defaults, this will create a new language object for your language

### 2. Provide example sentences

![](https://i.imgur.com/ak948Ha.png)<!-- .element: style="width:90%; border:none; background: none" -->

### 3. Tokenization Check

![](https://i.imgur.com/GRmRT1X.png)<!-- .element: style="width:90%; border:none; background: none" -->

### 4. Lookup Tables

![](https://i.imgur.com/qu7X9k6.png)<!-- .element: style="width:90%; border:none; background: none" -->

### 5. Load texts for annotation

![](https://i.imgur.com/SgeCIfI.png)<!-- .element: style="width:90%; border:none; background: none" -->

### 6. Frequent Tokens

#### Overview

![](https://i.imgur.com/im3FwqF.png)<!-- .element: style="width:70%; border:none; background: none" -->

#### Bulk Editing

![](https://i.imgur.com/nUBSOwS.png)<!-- .element: style="width:80%; border:none; background: none" -->

#### 7. Generate CONLL-U Files for Export to Inception

![](https://i.imgur.com/dEye0Io.jpeg) <!-- .element: style="width:70%; border:none; background: #222222;  box-shadow:none;" -->

### 8. Export model for training

![](https://i.imgur.com/kQxhPtZ.png)<!-- .element: style="width:70%; border:none; background: #222222; box-shadow:none;" -->

## Install and run with Docker

1. Make sure you have docker installed on your machine (including the `docker` command).
2. After cloning this repository, navigate to the root of the repository
For example:
```
git clone git@github.com:BCDH/cadet.git
cd cadet
```
3. Build the Docker image
```
docker build -t cadet .
```

4. Run the Docker Container
```
docker run -p 8000:8000 cadet
```
 

## Repo template

![](https://i.imgur.com/ttcnsAr.png)<!-- .element: style="width:70%; border:none; background: #222222; box-shadow:none;" -->

## How to use this template

1. [Click on the green button "Use this template"](https://docs.github.com/en/free-pro-team@latest/github/creating-cloning-and-archiving-repositories/creating-a-repository-from-a-template)
  ![](https://i.imgur.com/Rh2y7ZK.png)

2. Create a new repository for your app.  The name is entirely up to you.

3. When you application is working and ready to deploy, type the following in your browser:

    `https://heroku.com/deploy?template=https://github.com/<your git account>/<your repo>/tree/master`  

Please note that you will be prompted to create a Hiroku user account if you do not have one.

<a href="https://heroku.com/deploy">
  <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy">
</a>

## Acknowledgements

<img src="https://i.imgur.com/z7WiXJU.jpeg" width=20% height=20%>

This project has received funding from the European Union’s Horizon 2020 Research and Innovation Programme under Grant Agreement No 101004984: [CLS INFRA](https://clsinfra.io) as well as the National Endownment for the Humanities via [New Languages for NLP](https://newnlp.princeton.edu)
