import flask
from flask import request
from ruamel.yaml import YAML
import git
import json
import os.path

app = flask.Flask(__name__)
app.config["DEBUG"] = True
yaml=YAML()
with open('./config.json') as f:
    config=json.load(f)
    
path = config['default_home_path']

def gitpull(path):
    repo=git.Repo(path)
    repo.remotes.origin.pull()
    
def gitclone(path,repo):
    git.Git(path).clone(repo)
    
def readyaml(path):
   
    fp=open(path).read()
    yamlcontent=yaml.load(fp)
    return yamlcontent

def writeyaml(obj,str):
    fp=open(str,"w")
    yaml.dump(obj,fp)
    return True

def selectpipeline(input):
    print ("Inside selectpipeline ---")
    if input['BuildType'] == 'dotnet':
        pipelinescript ='dotnet.groovy'
        print ("go to dotnet.groovy") # printing
        return pipelinescript
    elif input['BuildType'] == 'React_Build_With_Test':
        pipelinescript = 'react_build_with_test.groovy'
        return pipelinescript
    elif input['BuildType'] == 'React_Build_With_Test_Gzip':
        pipelinescript = 'react_build_with_test_gzip.groovy'
        return pipelinescript
    else:
       return False
        
def modifyyamlforspring(yamlcontent,input,apprepo):
    for elem in yamlcontent:
        elem['job']['name']=input['ApplicationName']
        elem['job']['display-name']=input['BuildName']
        elem['job']['builders'][0]['maven-target']['maven-version']=input['Maven_Version']
        elem['job']['builders'][0]['maven-target']['pom']=input['pom_path']
        elem['job']['publishers'][0]['archive']['artifacts']=input['build_artifact_path']
        elem['job']['scm'][0]['git']['url']=apprepo    
        break
    return yamlcontent

def modifyyamlfordotnet(yamlcontent,input,apprepo,pipelinescript):
    print ("Inside modify for dotnet")
    for elem in yamlcontent:
        elem['job']['name']=input['ApplicationName']
        elem['job']['parameters'][0]['string']['default']=input['BuildName']
        elem['job']['parameters'][1]['string']['default']=apprepo
        elem['job']['parameters'][2]['string']['default']=config['credentials_id']
        elem['job']['parameters'][3]['string']['default']=input['FileName']
        elem['job']['parameters'][4]['string']['default']=input['Branch']
        elem['job']['pipeline-scm']['scm'][0]['git']['url']=config['job_git_url']
        elem['job']['pipeline-scm']['scm'][0]['git']['credentials-id']=config['credentials_id']
        elem['job']['pipeline-scm']['script-path']='pipeline/'+ pipelinescript
        elem['job']['builders'][0]['msbuild']['solution-file']=input['FileName']
        break
    return yamlcontent

def inputfunc(str):
    with open(os.path.join(path,str)+'/pipeline_config.json') as f:
        input=json.load(f)
        return input

def createdotnetjob(input,apprepo):
    print ("Inside create job for dotnet")
    pipeline_repo_path=os.path.join(path,config['repo_name'])
    if os.path.isdir(pipeline_repo_path):
        gitpull(pipeline_repo_path)
        yamlpath=os.path.join(pipeline_repo_path,"jobs/dotnetjob.yaml")
        yamlcontent=readyaml(yamlpath)
        pipelinescript=selectpipeline(input)
        if pipelinescript!= False :
            modifiedyaml=modifyyamlfordotnet(yamlcontent,input,apprepo,pipelinescript)
            if(writeyaml(modifiedyaml,'./dotnetjob.yaml')):
                os.system('jenkins-jobs --conf ./jenkins_jobs.ini update ./dotnetjob.yaml')
                print ("96 - dotnet job is created") # printing
                return ('dotnet job created')
            else:
                return ('error writing yaml file')
                print ("100 - error in writing to yaml file") # printing
               
        else:
            print ("107 - No valid pipeline template") # printing
            return ('Invalid Pipeline Type')
            
    else:
        gitclone(path,config['job_git_url'])
        print ("Inside cloning dotnet job for dotnet")
        yamlpath=os.path.join(pipeline_repo_path,"jobs/dotnetjob.yaml")
        yamlcontent=readyaml(yamlpath)
        pipelinescript=selectpipeline(input)
        if pipelinescript!= False :
            modifiedyaml=modifyyamlfordotnet(yamlcontent,input,apprepo,pipelinescript)
            if(writeyaml(modifiedyaml,'./dotnetjob.yaml')):
                os.system('jenkins-jobs --conf ./jenkins_jobs.ini update ./dotnetjob.yaml')
                return ('dotnet job created')
            else:
                return ('error writing yaml file')
                print ("122 - error writing to yaml file") # printing
        else:
            print ("125 - invalid pipeline type") # printing
            return ('Invalid Pipeline Type')

def createspringjob(input,apprepo):
    pipeline_repo_path=os.path.join(path,config['repo_name'])
    if os.path.isdir(pipeline_repo_path):
        gitpull(pipeline_repo_path)
        yamlpath=os.path.join(pipeline_repo_path,"jobs/springmavenjob.yaml")
        yamlcontent=readyaml(yamlpath)
        modifiedyaml=modifyyamlforspring(yamlcontent,input,apprepo)
        if(writeyaml(modifiedyaml,'./springmavenjob.yaml')):
            os.system('jenkins-jobs --conf ./jenkins_jobs.ini update ./springmavenjob.yaml')
            return ('spring job created')
        else:
            return ('error writing yaml file')
    else:
        gitclone(path,config['job_git_url'])
        yamlpath=os.path.join(pipeline_repo_path,"jobs/springmavenjob.yaml")
        yamlcontent=readyaml(yamlpath)
        modifiedyaml=modifyyamlforspring(yamlcontent,input,apprepo)
        if(writeyaml(modifiedyaml,'./springmavenjob.yaml')):
            os.system('jenkins-jobs --conf ./jenkins_jobs.ini update ./springmavenjob.yaml')
            return ('spring job created')
        else:
            return ('error writing yaml file')

    
@app.route('/', methods=['GET','POST'])
def home():
    data=request.json
    print ("Inside home definition")
    repo_path=os.path.join(path,request.json['repository']['name'])
    print ("repo path is ", repo_path)
    if os.path.isdir(repo_path):
        gitpull(repo_path)
        input=inputfunc(repo_path)
        if input['ApplicationType'] == 'dotnet':
            apprepo=request.json['repository']['clone_url']
            print ("Input selected is dotnet", apprepo)
            final_output=createdotnetjob(input,apprepo)
            return json.dumps(final_output)
        elif input['ApplicationType'] == 'Spring':
            apprepo=request.json['repository']['clone_url']
            final_output=createspringjob(input,apprepo)
            return json.dumps(final_output)
        else:
            return ('Invalid Application Type')
            print ("170 - Invalid application type") # printing
    else:
        gitclone(path,request.json['repository']['clone_url'])
        output=inputfunc(repo_path)
        if output['ApplicationType'] == 'dotnet':
            apprepo=request.json['repository']['clone_url']
            print ("Input cloned is dotnet", apprepo)
            final_output=createdotnetjob(output,apprepo)
            return json.dumps(final_output)
        elif output['ApplicationType'] == 'Spring':
            apprepo=request.json['repository']['clone_url']
            final_output=createspringjob(output,apprepo)
            return json.dumps(final_output)
        else:
            return ('Invalid Application Type')
            print ("185 - Invalid application type") # printing

app.run(host="0.0.0.0")
