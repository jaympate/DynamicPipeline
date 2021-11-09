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
    if input['BuildType'] == 'dotnet':
        pipelinescript ='dotnet.groovy'
        return pipelinescript
    else:
       return False
        
"""def modifyyamlforspring(yamlcontent,input,apprepo):
    for elem in yamlcontent:
        elem['job']['name']=input['ApplicationName']
        elem['job']['display-name']=input['BuildName']
        elem['job']['builders'][0]['maven-target']['maven-version']=input['Maven_Version']
        elem['job']['builders'][0]['maven-target']['pom']=input['pom_path']
        elem['job']['publishers'][0]['archive']['artifacts']=input['build_artifact_path']
        elem['job']['scm'][0]['git']['url']=apprepo    
        break
    return yamlcontent"""

def modifyyamlfordotnet(yamlcontent,input,apprepo,pipelinescript):
    for elem in yamlcontent:
        elem['job']['name']=input['ApplicationName']
        elem['job']['parameters'][0]['string']['default']=input['BuildName']
        elem['job']['parameters'][1]['string']['default']=apprepo
        elem['job']['parameters'][2]['string']['default']=config['credentials_id']
        elem['job']['parameters'][3]['string']['default']=input['FileName']   # Input the application file name
        elem['job']['parameters'][4]['string']['default']=input['Branch']     # The branch where the developer code is committed
        elem['job']['pipeline-scm']['scm'][0]['git']['url']=config['job_git_url']
        elem['job']['pipeline-scm']['scm'][0]['git']['credentials-id']=config['credentials_id']
        elem['job']['pipeline-scm']['script-path']='pipeline/'+ pipelinescript
        elem['job']['builders'][0]['msbuild']['solution-file']=input['FileName'] # The builder name that needs to be used
        break
    return yamlcontent

def inputfunc(str):
    with open(os.path.join(path,str)+'/pipeline_config.json') as f:
        input=json.load(f)
        return input

def createdotnetjob(input,apprepo):
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
                return ('dotnet job created')
            else:
                return ('error writing yaml file')
                               
        else:
            return ('Invalid Pipeline Type')
            
    else:
        gitclone(path,config['job_git_url'])
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
        else:
             return ('Invalid Pipeline Type')

"""def createspringjob(input,apprepo):
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
            return ('error writing yaml file')"""

    
@app.route('/', methods=['GET','POST'])
def home():
    data=request.json
    repo_path=os.path.join(path,request.json['repository']['name'])
    if os.path.isdir(repo_path):
        gitpull(repo_path)
        input=inputfunc(repo_path)
        if input['ApplicationType'] == 'dotnet':
            apprepo=request.json['repository']['clone_url']
            final_output=createdotnetjob(input,apprepo)
            return json.dumps(final_output)
        """elif input['ApplicationType'] == 'Spring':
            apprepo=request.json['repository']['clone_url']
            final_output=createspringjob(input,apprepo)
            return json.dumps(final_output)
        else:
            return ('Invalid Application Type')"""
    else:
        gitclone(path,request.json['repository']['clone_url'])
        output=inputfunc(repo_path)
        if output['ApplicationType'] == 'dotnet':
            apprepo=request.json['repository']['clone_url']
            final_output=createdotnetjob(output,apprepo)
            return json.dumps(final_output)
        """elif output['ApplicationType'] == 'Spring':
            apprepo=request.json['repository']['clone_url']
            final_output=createspringjob(output,apprepo)
            return json.dumps(final_output)
        else:
            return ('Invalid Application Type')"""

app.run(host="0.0.0.0")
