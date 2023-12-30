import jenkins
import os
import polling
import requests
import json
import sys
import datetime
import time
import regex as re

os.environ["PYTHONHTTPSVERIFY"] = str(0)
rest_api=os.environ["REST_API"] 
service_url = "http://{}/latest_job".format(rest_api)
db_url = "http://{}/build_info".format(rest_api)
stage_url = "https://insights.infra.tssrd.hpecorp.net/api/cdpstagemetric"


def get_secret(secret_name):
    try:
        with open('/run/secrets/{0}'.format(secret_name), 'r') as secret_file:
            return secret_file.read()
    except IOError:
        return None

def get_nested_parameters(parameter_name, class_name, build_info):
    dicts = filter(lambda x: "_class" in x, build_info["actions"])
    if class_name == "jenkins.metrics.impl.TimeInQueueAction":
        return dict_Item(parameter_name, "_class", class_name, dicts)
    if class_name == "hudson.model.ParametersAction":
        try:
            params_dicts = dict_Item("parameters", "_class", class_name, dicts)
            return dict_Item("value","name", parameter_name, params_dicts)
        except:
            return None
    if class_name == "hudson.maven.reporters.MavenAggregatedArtifactRecord":
        return  dict_Item(parameter_name,"_class", class_name, dicts)

def dict_Item(value, dict_key, key, dicts):
    return next((item[value] for item in dicts if item[dict_key] == key), None)

def get_last_completed_build_info(server, job_name):
    job_info = server.get_job_info(job_name)
    build_number = job_info["lastCompletedBuild"]["number"]
    build_info = server.get_build_info(job_name, build_number, depth=2)
    return build_info

def update_info(jobs):
    for job in jobs["job_list"]:
        repo = job["component_name"]
        for item in job["job_details"]:
            try:
                server = jenkins.Jenkins(item["job_url"], username=jenkins_username, password=jenkins_password, timeout=10)
                build_info = get_last_completed_build_info(server, item["job_name"])
                classinfo = build_info.get('_class')

                env = get_nested_parameters("ENV", "hudson.model.ParametersAction", build_info)
                
                db_result = requests.get("{0}?job_name=eq.{1}&or=(env.eq.{2},env.is.null)".format(service_url, item["job_name"], env), timeout=15)
                db_result.raise_for_status()
                print(str(datetime.datetime.now())+" "+str(db_result.status_code)+" Status Code for "+item["job_name"])

                db_build_number = db_result.json()[-1:] if not db_result.json()[-1:] else db_result.json()[-1]["build_number"]
                metricid = db_result.json()[-1:] if not db_result.json()[-1:] else db_result.json()[-1]["id"]
                if db_build_number != build_info["number"]:

                    headers = {
                        "Authorization": "Bearer {}".format(jwt),
                        "Content-Type": "application/json", 
                        "Prefer": "return=representation"
                    }

                    total_duration = get_nested_parameters("totalDurationMillis", "jenkins.metrics.impl.TimeInQueueAction", build_info)
                    queue_duration = get_nested_parameters("queuingTimeMillis", "jenkins.metrics.impl.TimeInQueueAction", build_info)

                    if item["vsm_stage"] == "release":
                        version = build_info["displayName"]
                        if not re.match(r'.*RC\-.*\d$',version):
                            if re.match(r'^\#\d+$',version) and re.match(r'^(sbs-|eaas).*',repo): 
                                version = get_nested_parameters("RELEASE_VERSION", "hudson.model.ParametersAction", build_info)
                            elif re.match(r'^\#\d+$',version) and re.match(r'^(sa_isaport).*',repo):
                                version = get_nested_parameters("CURRENT_SNAPSHOT_VERSION", "hudson.model.ParametersAction", build_info)
                            else:
                                try:
                                    version = "RC-"+str(build_info["number"])+"-"+build_info["changeSets"][0]["items"][0]["date"].split(" ")[0].replace("-",".")
                                except:
                                    version = "Null"
                    else:
                        version = get_nested_parameters(item["version"], "hudson.model.ParametersAction", build_info)

                    if item["vsm_stage"] == "performance-tests":
                        repo = get_nested_parameters("REPO", "hudson.model.ParametersAction", build_info)

                    payload = {
                        "job_name": item["job_name"],
                        "build_number": build_info["number"],
                        "version": version,
                        "env": env,
                        "start_time": int(round(build_info["timestamp"]/1000)),
                        "queue_duration": int(round(queue_duration/1000)),
                        "total_duration": int(round(total_duration/1000)),
                        "build_status": build_info["result"], 
                        "vsm_stage": item["vsm_stage"],
                        "repo": repo 
                    }
                    payload_json = json.dumps(payload)

                    response = requests.post(db_url, headers=headers, data=payload_json, timeout=20)
                    response.raise_for_status()
                    print(str(datetime.datetime.now())+" "+str(response.status_code)+" Status code for insertion of build metric "+item["job_name"]+" env "+str(env))
                    metricid = response.json()[0].get('id')
                else:
                  print(str(datetime.datetime.now())+" "+str(db_build_number)+" Build Number already exists for "+item["job_name"]+" env "+str(env))

                db_result = requests.get("{0}?metricid=eq.{1}".format(stage_url, metricid), timeout=15, verify=False)
                db_result.raise_for_status()
                if (not db_result.json()):
                    headers = {
                                "Authorization": "Bearer {}".format(jwt),
                                "Content-Type": "text/csv"
                                }
                    payload = "stagename,metricid,status,stagestarttime,duration,stageerror"+"\n"

                    if (classinfo != "hudson.maven.MavenModuleSetBuild"):
                        response = requests.get("{0}wfapi/describe".format(build_info["url"]), timeout=15, verify=False)
                        response.raise_for_status()
                        for stage in response.json().get('stages'):
                            error = (str(stage.get('error', {}).get('type'))+":"+str(stage.get('error', {}).get('message'))).replace(",",";")
                            error = error if error != "None:None" else "None"
                            payload = payload+stage.get('name').replace(",",":")+","+str(metricid)+","+stage.get('status')+","+str(stage.get('startTimeMillis'))+","+str(stage.get('durationMillis'))+","+error+"\n"
                    else:
                        moduleList = get_nested_parameters("moduleRecords", "hudson.maven.reporters.MavenAggregatedArtifactRecord", build_info)
                        for module in moduleList:
                            payload = payload+module["mainArtifact"]["artifactId"]+","+str(metricid)+","+module["parent"]["result"]+","+str(module["parent"]["timestamp"])+","+str(module["parent"]["duration"])+"\n"
                    stage_response = requests.post(stage_url, headers=headers, data=payload, timeout=20, verify=False)
                    stage_response.raise_for_status()
                    print(str(datetime.datetime.now())+" "+str(stage_response.status_code)+" Status code for insertion of stage metric "+item["job_name"]+" env "+str(env))
                else:
                    print(str(datetime.datetime.now())+" Stage metrics already exists for "+item["job_name"]+" build number "+str(db_build_number))
            except:
                print(str(datetime.datetime.now())+" Unexpected error in {}: ".format(item["job_name"]), sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)
                pass
            time.sleep(5)

jenkins_username = get_secret("jenkins_username")
jenkins_password = get_secret("jenkins_password")
jwt = get_secret("jwt")

with open("/jobs_config", "r") as jobs_file:
    jobs = json.load(jobs_file)

counter = 1
while counter <= int(os.environ["APP_COUNTER"]):
    print(str(datetime.datetime.now())+" Current count is: "+str(counter))
    update_info(jobs)
    time.sleep(5)
    if counter == int(os.environ["APP_COUNTER"]):
        print("Polling completed")
        sys.exit(0)
    counter += 1
