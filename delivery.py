from flask import Flask, request
import hashlib
import os
import shutil
import git
import configparser
import requests
import json

app = Flask(__name__)

valid_token = ''
valid_ip = ''

wechat_robot_webhook_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='


base_dir = '/home/devops/deploy/'
repo_dir = '/home/devops/deploy/cloudscan-deploy/'
prev_repo_dir = '/home/devops/deploy/cloudscan-deploy-prev/'
dot_git_dir = '/home/devops/deploy/cloudscan-deploy/.git'

repo_script_dir = repo_dir + 'script/'

repo_bin_dir = repo_dir + 'bin/'
prev_repo_bin_dir = prev_repo_dir + 'bin/'

repo_timer_script_dir = repo_dir + 'timerScript/'
prev_repo_timer_script_dir = prev_repo_dir + 'timerScript/'

repo_conf_dir = repo_dir + 'conf/'
prev_repo_conf_dir = prev_repo_dir + 'conf/'

repo_systemd_service_dir = repo_dir + 'systemdService/'
prev_repo_systemd_service_dir = prev_repo_dir + 'systemdService/'

repo_timer_service_dir = repo_dir + 'timerService/'
prev_repo_timer_service_dir = prev_repo_dir + 'timerService/'

hosts_dir = repo_dir + 'hosts'
prev_hosts_dir = prev_repo_dir + 'hosts'


git_url = ''
ssh_key = ''

def get_entity_from_hosts(hosts_dir, entity_name):
    hosts_config = configparser.ConfigParser(allow_no_value=True)
    hosts_config.read(hosts_dir)
    entity_config = hosts_config.items(entity_name)
    entity_list = []
    if entity_name == "bin-list":
        for entity_tuple in entity_config:
            entity_list.append(entity_tuple[0][4:])
        return entity_list

    if entity_name == "script-online-deployment" or entity_name == "all-linux":
        for entity_tuple in entity_config:
            entity_list.append(entity_tuple[0])
        return entity_list

    if entity_name == "windows-engine-list" or entity_name == "linux-engine-list":
        for entity_tuple in entity_config:
            entity_list.append(entity_tuple[0][7:])
        return entity_list




linux_engine_list = get_entity_from_hosts(hosts_dir, 'linux-engine-list')
windows_engine_list = get_entity_from_hosts(hosts_dir, 'windows-engine-list')
bin_list = get_entity_from_hosts(hosts_dir, 'bin-list')
script_dir_list = get_entity_from_hosts(hosts_dir, 'script-online-deployment')
print(linux_engine_list)
print(windows_engine_list)
print(bin_list)
print(script_dir_list)


def send_wechat_robot_message(message):
    headers = {'Content-Type': 'application/json'}
    data = {
            "msgtype": "text",
            "text": {
                "content": ""+message+""
            }
    }
    response = requests.post(url=wechat_robot_webhook_url, headers=headers, data=json.dumps(data))

    if response.status_code != 200:
        print("send wechat robot message error")

def get_hosts_dict(file_path):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(file_path)
    return config


def get_diff_hosts(now_hosts, prev_hosts):
    pass


# write into ini
# config.add_section('login') # add new section
# config.set('login','username','admin')
# config.set('login','password','123456')
# config.write(open(path,'a'))


# get file md5
def get_file_md5(filename):
    with open(filename, 'rb') as fp:
        data = fp.read()
    file_md5 = hashlib.md5(data).hexdigest()
    return file_md5


# get zip ext name from some dir
def get_zip_name_from_file():
    for root, dirs, files in os.walk(repo_bin_dir):
        files.sort()
        zip_program = files.pop()
        zip_name = zip_program[0:6]
        return zip_name


def make_online_project_dir(*ip):
    #online_host_config = get_hosts_dict(hosts_dir)
    #online_bin_dir = online_host_config.get('projectconf','online_bin_dir')
    #online_conf_dir = online_host_config.get('projectconf','online_conf_dir')
    #project_base = online_host_config.get('projectconf','project_base')
    online_bin_dir = '/opt/cloudscan/gobin'
    online_conf_dir = '/opt/cloudscan/conf'
    online_scand_conf_dir = '/opt/cloudscan/conf/conf'
    project_base = '/opt/cloudscan'
    scand_dir = '/data/scandir'
    names =globals()
    online_dir_list = get_entity_from_hosts(hosts_dir, 'script-online-deployment')
    for online_dir in online_dir_list:
        dir_name_value_list = online_dir.split("-")
        names[dir_name_value_list[0]] = dir_name_value_list[1]
    #print(online_script_dir)

    if len(ip) > 0:
        # deploy for ip list
        for ip_str in ip[0]:
            system_command_str = "ansible " + ip_str + " -m shell -a \" mkdir -p " + online_bin_dir +";mkdir -p "+ online_conf_dir +";mkdir -p "+ online_script_dir +";mkdir -p "+ online_scand_conf_dir +";mkdir -p "+ scand_dir +";chmod -R 777 "+ scand_dir +";chown -R app:app "+ project_base +";chown -R app:app "+ online_script_dir +" \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)



def chown_to_program_user(ansible_group):
    system_command_str = "ansible " + ansible_group + " -m shell -a \" chown -R app:app /opt/cloudscan;chown -R app:app /opt/cloudscan/script \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
    print(system_command_str)
    os.system(system_command_str)


def restart_bin(go_bin_name, *ip):
    if len(ip) > 0:
        for ip_str in ip[0]:
            if go_bin_name.find('cs') != 0:#not start with cs
                system_command_str = "ansible " + ip_str + " -m shell -a 'systemctl restart cs" + go_bin_name + ";systemctl status cs" + go_bin_name + "' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
                print(system_command_str)
                os.system(system_command_str)
            else:
                if go_bin_name == "cspost":
                    system_command_str = "ansible " + ip_str + " -m shell -a 'for i in {1..6};do sudo systemctl restart cspost@post$i;sudo systemctl status cspost@post$i;done' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
                    print(system_command_str)
                    os.system(system_command_str)
                else:
                    system_command_str = "ansible " + ip_str + " -m shell -a 'systemctl restart " + go_bin_name + ";systemctl status " + go_bin_name + "' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
                    print(system_command_str)
                    os.system(system_command_str)
    else:
        #go_bin_name is engine name or bin grogram name
        if go_bin_name.find('cs') != 0:#not start with cs
            system_command_str = "ansible " + go_bin_name + " -m shell -a 'systemctl restart cs" + go_bin_name + ";systemctl status cs" + go_bin_name + "' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
        else:
            if go_bin_name == "cspost":
                ansible_group = go_bin_name
                system_command_str = "ansible " + ansible_group + " -m shell -a 'for i in {1..6};do sudo systemctl restart cspost@post$i;sudo systemctl status cspost@post$i;done' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
                print(system_command_str)
                os.system(system_command_str)
            else:
                ansible_group = go_bin_name
                system_command_str = "ansible " + ansible_group + " -m shell -a 'systemctl restart " + go_bin_name + ";systemctl status " + go_bin_name + "' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
                print(system_command_str)
                os.system(system_command_str)


def restart_timer_script(service_file_name, *ip):
    go_bin_name = service_file_name
    if len(ip) > 0:
        for ip_str in ip[0]:
            system_command_str = "ansible " + ip_str + " -m shell -a 'systemctl restart " + go_bin_name + ";systemctl status " + go_bin_name + "' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
    else:
            ansible_group = service_file_name[0:-6]
            system_command_str = "ansible " + ansible_group + " -m shell -a 'systemctl restart " + go_bin_name + ";systemctl status " + go_bin_name + "' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)


def stop_bin(go_bin_name, *ip):
    if len(ip) > 0:
        for ip_str in ip[0]:
            if go_bin_name == "cspost":
                system_command_str = "ansible " + ip_str + " -m shell -a 'for i in {1..6};do sudo systemctl stop cspost@post$i;sudo systemctl status cspost@post$i;done' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
                print(system_command_str)
                os.system(system_command_str)
            else:
                system_command_str = "ansible " + ip_str + " -m shell -a 'systemctl stop " + go_bin_name + ";systemctl status " + go_bin_name + "' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
                print(system_command_str)
                os.system(system_command_str)
    else:
        if go_bin_name == "cspost":
            ansible_group = go_bin_name
            system_command_str = "ansible " + ansible_group + " -m shell -a 'for i in {1..6};do sudo systemctl stop cspost@post$i;sudo systemctl status cspost@post$i;done' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
        else:
            ansible_group = go_bin_name
            system_command_str = "ansible " + ansible_group + " -m shell -a 'systemctl stop " + go_bin_name + ";systemctl status " + go_bin_name + "' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)


# stop some engine's csscand daemon, if give second param, just stop that ip's engine csscand daemon
def stop_csscand_engine_bin(engine_name, *ip):
    if len(ip) > 0:
        for ip_str in ip[0]:
            system_command_str = "ansible " + ip_str + " -m shell -a 'systemctl stop cs" + engine_name + ";systemctl status cs" + engine_name + "' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
    else:
        ansible_group = engine_name
        system_command_str = "ansible " + ansible_group + " -m shell -a 'systemctl stop cs" + engine_name + ";systemctl status cs" + engine_name + "' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)

def deploy_scand(scand_name):
    if scand_name == 'csscand.exe':
        os.system("sh "+repo_script_dir+"windows_all_element_per_stop_ansible.sh")
        os.system("sh "+repo_script_dir+"scp_all_windows_bin.sh")
        os.system("sh "+repo_script_dir+"windows_all_element_per_start_ansible.sh")
    if scand_name == "csscand":
        os.system("sh "+repo_script_dir+"scp_all_linux_bin.sh")
        os.system("sh "+repo_script_dir+"all_element_engine_per_restart_ansible.sh")


def deploy_linux_engine_csscand(csscand_name, engine):
    system_command_str = "ansible " + engine + " -m copy -a \"src='" + repo_bin_dir + csscand_name + "' dest='/opt/cloudscan/gobin/"+csscand_name+"' mode='0755'\" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
    print(system_command_str)
    #os.system(system_command_str)
    chown_to_program_user(engine)


# deploy all bin program, but don't incloud csscand
def deploy_bin(go_bin_name, *ip):
    if len(ip) > 0:
        # deploy for ip list
        for ip_str in ip[0]:
            system_command_str = "ansible " + ip_str + " -m copy -a \"src='" + repo_bin_dir + go_bin_name + "' dest='/opt/cloudscan/gobin/"+go_bin_name+"' mode='0755'\" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
            chown_to_program_user(ip_str)

    else:
        ansible_group = go_bin_name
        system_command_str = "ansible " + ansible_group + " -m copy -a \"src='" + repo_bin_dir + go_bin_name + "' dest='/opt/cloudscan/gobin/"+go_bin_name+"' mode='0755'\" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)
        chown_to_program_user(ansible_group)


def deploy_timer_script_file(go_bin_name, *ip):
    if len(ip) > 0:
        # deploy for ip list
        for ip_str in ip[0]:
            system_command_str = "ansible " + ip_str + " -m copy -a \"src='" + repo_timer_script_dir + go_bin_name + "' dest='"+online_script_dir+""+go_bin_name+"' mode='0755'\" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
            chown_to_program_user(ip_str)

    else:
        ansible_group = go_bin_name[:-3]
        system_command_str = "ansible " + ansible_group + " -m copy -a \"src='" + repo_timer_script_dir + go_bin_name + "' dest='"+online_script_dir+""+go_bin_name+"' mode='0755'\" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)
        chown_to_program_user(ansible_group)


def deploy_windows_bin(bin_name, engine_name):
    system_command_str = "ansible "+engine_name+" -m win_copy -a 'src=" + repo_bin_dir + bin_name + " dest=D:\\\\v0.0.0\\\\app\\\\csscand.exe'"
    print(system_command_str)
    os.system(system_command_str)


def restart_windows_bin(engine_name):
    system_command_str = "ansible "+engine_name+" -m win_shell -a 'd:\\v0.0.0\\supervisord.exe ctl start "+engine_name+" /u csscand /P g575JwqwJkLDBpbq'"
    print(system_command_str)
    os.system(system_command_str)


def stop_windows_bin(engine_name):
    system_command_str = "ansible "+engine_name+" -m win_shell -a 'd:\\v0.0.0\\supervisord.exe ctl stop "+engine_name+" /u csscand /P g575JwqwJkLDBpbq'"
    print(system_command_str)
    os.system(system_command_str)


def restart_csscand_engine_bin(engine_name):
    system_command_str = "ansible " + engine_name + " -m shell -a 'systemctl restart cs" + engine_name + ";systemctl status cs" + engine_name + "' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
    print(system_command_str)
    os.system(system_command_str)



def deploy_windows_conf_file(conf_file_name, *engine_name):
    if len(engine_name) > 0:
        # deploy just some engine
        system_command_str = "ansible "+engine_name[0]+" -m win_copy -a 'src=" + repo_conf_dir + conf_file_name + " dest=D:\\\\v0.0.0\\\\supervisord.conf'"
        print(system_command_str)
        os.system(system_command_str)
    else:
        system_command_str = "ansible windows -m win_copy -a 'src=" + repo_conf_dir + conf_file_name + " dest=D:\\\\v0.0.0\\\\supervisord.conf'"
        print(system_command_str)
        os.system(system_command_str)


# deploy all conf file ,but don't incloud csscand
def deploy_conf_file(conf_file_name, *ip):
    if len(ip) > 0:
        # deploy for ip list
        bin_name = conf_file_name[:-5]
        for ip_str in ip[0]:
            system_command_str = "ansible " + ip_str + " -m copy -a \"src='" + repo_conf_dir + conf_file_name + "' dest='/opt/cloudscan/conf/"+conf_file_name+"'\" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
            chown_to_program_user(bin_name)
            ip_str_to_list = []
            ip_str_to_list.append(ip_str)
            restart_bin(bin_name, ip_str_to_list)
    else:
        ansible_group = conf_file_name[:-5]
        system_command_str = "ansible " + ansible_group + " -m copy -a \"src='" + repo_conf_dir + conf_file_name + "' dest='/opt/cloudscan/conf/"+conf_file_name+"'\" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)
        chown_to_program_user(ansible_group)
        restart_bin(ansible_group)

def deploy_csscand_conf_file(conf_file_name, *ip):
    if len(ip) > 0:
        # deploy for ip list
        for ip_str in ip[0]:
            system_command_str = "ansible " + ip_str + " -m copy -a \"src='" + repo_conf_dir + "conf/" + conf_file_name + "' dest='/opt/cloudscan/conf/conf/"+conf_file_name+"'\" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
            chown_to_program_user(ip_str)

    else:
        ansible_group = conf_file_name[8:-5]
        system_command_str = "ansible " + ansible_group + " -m copy -a \"src='" + repo_conf_dir + "conf/" + conf_file_name + "' dest='/opt/cloudscan/conf/conf/"+conf_file_name+"'\" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)
        chown_to_program_user(ansible_group)
        restart_csscand_engine_bin(ansible_group)


def remove_csscand_conf_file(conf_file_name, *ip):
    if len(ip) > 0:
        # remove for ip list
        for ip_str in ip[0]:
            system_command_str = "ansible " + ip_str + " -m shell -a 'cd /opt/cloudscan/conf/conf/ && rm -f "+conf_file_name+"' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
    else:
        ansible_group = conf_file_name[8:-5]
        system_command_str = "ansible " + ansible_group + " -m shell -a 'cd /opt/cloudscan/conf/conf/ && rm -f "+conf_file_name+"' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)

def remove_bin_conf_file(conf_file_name, *ip):
    if len(ip) > 0:
        # remove for ip list
        for ip_str in ip[0]:
            system_command_str = "ansible " + ip_str + " -m shell -a 'cd /opt/cloudscan/conf/ && rm -f "+conf_file_name+"' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
    else:
        ansible_group = conf_file_name[:-5]
        system_command_str = "ansible " + ansible_group + " -m shell -a 'cd /opt/cloudscan/conf/ && rm -f "+conf_file_name+"' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)


def remove_bin(bin_name, *ip):
    if len(ip) > 0:
        # remove for ip list
        for ip_str in ip[0]:
            system_command_str = "ansible " + ip_str + " -m shell -a 'cd /opt/cloudscan/gobin/ && rm -f "+bin_name+"' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
    else:
        ansible_group = bin_name
        system_command_str = "ansible " + ansible_group + " -m shell -a 'cd /opt/cloudscan/gobin/ && rm -f "+bin_name+"' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)


def deploy_service_file(service_file_name, *ip):
    if linux_engine_list.count(service_file_name[2:-8]) or windows_engine_list.count(service_file_name[2:-8]):
        ansible_group = service_file_name[2:-8]
    else:
        ansible_group = service_file_name[:-8]

    if len(ip) > 0:
        # deploy for ip list
        for ip_str in ip[0]:
            system_command_str = "ansible " + ip_str + " -m copy -a \"src='" + repo_systemd_service_dir + service_file_name + "' dest='/usr/lib/systemd/system'\" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
            system_command_str = "ansible " + ip_str + " -m shell -a \" systemctl daemon-reload \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
            system_command_str = "ansible " + ip_str + " -m shell -a \" systemctl enable " + service_file_name +" \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
            ip_str_to_list = []
            ip_str_to_list.append(ip_str)
            restart_bin(ansible_group, ip_str_to_list)
    else:
        system_command_str = "ansible " + ansible_group + " -m copy -a \"src='" + repo_systemd_service_dir + service_file_name + "' dest='/usr/lib/systemd/system'\" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)
        system_command_str = "ansible " + ansible_group + " -m shell -a \" systemctl daemon-reload \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)
        system_command_str = "ansible " + ansible_group + " -m shell -a \" systemctl enable " + service_file_name +" \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)
        restart_bin(ansible_group)


def deploy_timer_service_file(service_file_name, *ip):

    if service_file_name[-8:] == ".service":
        ansible_group = service_file_name[:-8]
    if service_file_name[-6:] == ".timer":
        ansible_group = service_file_name[:-6]

    if len(ip) > 0:
        # deploy for ip list
        for ip_str in ip[0]:
            system_command_str = "ansible " + ip_str + " -m copy -a \"src='" + repo_timer_service_dir + service_file_name + "' dest='/usr/lib/systemd/system'\" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
            system_command_str = "ansible " + ip_str + " -m shell -a \" systemctl daemon-reload \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
            system_command_str = "ansible " + ip_str + " -m shell -a \" systemctl enable " + service_file_name +" \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
            ip_str_to_list = []
            ip_str_to_list.append(ip_str)
            if service_file_name[-6:] == ".timer":
                restart_timer_script(service_file_name, ip_str_to_list)
    else:
        system_command_str = "ansible " + ansible_group + " -m copy -a \"src='" + repo_timer_service_dir + service_file_name + "' dest='/usr/lib/systemd/system'\" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)
        system_command_str = "ansible " + ansible_group + " -m shell -a \" systemctl daemon-reload \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)
        system_command_str = "ansible " + ansible_group + " -m shell -a \" systemctl enable " + service_file_name +" \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)
        if service_file_name[-6:] == ".timer":
            restart_timer_script(service_file_name)


def remove_csscand_service_file(service_file_name, *ip):
    if len(ip) > 0:
        # remove for ip list
        for ip_str in ip[0]:
            system_command_str = "ansible " + ip_str + " -m shell -a 'cd /usr/lib/systemd/system && rm -f "+service_file_name+"' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
            system_command_str = "ansible " + ip_str + " -m shell -a \" systemctl daemon-reload \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
            system_command_str = "ansible " + ip_str + " -m shell -a \" systemctl disable " + service_file_name +" \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
    else:
        ansible_group = service_file_name[2:-8]
        system_command_str = "ansible " + ansible_group + " -m shell -a 'cd /usr/lib/systemd/system && rm -f "+service_file_name+"' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)
        system_command_str = "ansible " + ansible_group + " -m shell -a \" systemctl daemon-reload \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)
        system_command_str = "ansible " + ansible_group + " -m shell -a \" systemctl disable " + service_file_name +" \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)


def remove_bin_service_file(service_file_name, *ip):
    if len(ip) > 0:
        # remove for ip list
        for ip_str in ip[0]:
            system_command_str = "ansible " + ip_str + " -m shell -a 'cd /usr/lib/systemd/system && rm -f "+service_file_name+"' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
            system_command_str = "ansible " + ip_str + " -m shell -a \" systemctl daemon-reload \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
            system_command_str = "ansible " + ip_str + " -m shell -a \" systemctl disable " + service_file_name +" \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
            print(system_command_str)
            os.system(system_command_str)
    else:
        ansible_group = service_file_name[:-8]
        system_command_str = "ansible " + ansible_group + " -m shell -a 'cd /usr/lib/systemd/system && rm -f "+service_file_name+"' --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)
        system_command_str = "ansible " + ansible_group + " -m shell -a \" systemctl daemon-reload \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)
        system_command_str = "ansible " + ansible_group + " -m shell -a \" systemctl disable " + service_file_name +" \" --private-key " + ssh_key + "  --become  --become-method=sudo  --become-user=root"
        print(system_command_str)
        os.system(system_command_str)


def deploy_bin_program(repo_bin_dir, prev_repo_bin_dir):
    # deploy bin program
    repo_bin_list = os.listdir(repo_bin_dir)
    prev_repo_bin_list = os.listdir(prev_repo_bin_dir)
    for bin_file in repo_bin_list:
        if bin_file == '.gitignore':
            continue
        if prev_repo_bin_list.count(bin_file):
            print("the bin file had deploy before,we check if it have changed")
            repo_bin_file_md5 = get_file_md5(repo_bin_dir + bin_file)
            prev_repo_bin_file_md5 = get_file_md5(prev_repo_bin_dir + bin_file)
            if repo_bin_file_md5 == prev_repo_bin_file_md5:
                print("the bin file do not change,we do not need deploy it")
            else:
                print(
                    "the bin file had changed, we need deploy the new version")
                if bin_file == "csscand" or bin_file == "csscand.exe":
                    deploy_scand(bin_file)
                    continue
                deploy_bin(bin_file)
                restart_bin(bin_file)
        else:
            print(
                "the bin file is new file, we do not deploy it before,now we deploy it"
            )
            if bin_file == "csscand" or bin_file == "csscand.exe":
                deploy_scand(bin_file)
                continue
            deploy_bin(bin_file)
            restart_bin(bin_file)


def deploy_timer_script_program(repo_bin_dir, prev_repo_bin_dir):
    # deploy bin program
    repo_bin_list = os.listdir(repo_bin_dir)
    prev_repo_bin_list = os.listdir(prev_repo_bin_dir)
    for bin_file in repo_bin_list:
        if bin_file == '.gitignore':
            continue
        if prev_repo_bin_list.count(bin_file):
            print("the bin file had deploy before,we check if it have changed")
            repo_bin_file_md5 = get_file_md5(repo_bin_dir + bin_file)
            prev_repo_bin_file_md5 = get_file_md5(prev_repo_bin_dir + bin_file)
            if repo_bin_file_md5 == prev_repo_bin_file_md5:
                print("the bin file do not change,we do not need deploy it")
            else:
                print(
                    "the bin file had changed, we need deploy the new version")
                deploy_timer_script_file(bin_file)
                restart_timer_script(bin_file[:-3]+".timer")
        else:
            print(
                "the bin file is new file, we do not deploy it before,now we deploy it"
            )
            deploy_timer_script_file(bin_file)
            restart_timer_script(bin_file[:-3]+".timer")


def deploy_windows_csscand_conf_file(conf_file_name):
    ansible_group = conf_file_name[8:-5]
    system_command_str = "ansible "+ansible_group+" -m win_copy -a 'src=" + repo_conf_dir +"conf/"+ conf_file_name + " dest=D:\\\\v0.0.0\\\\conf\\\\"+conf_file_name+"'"
    print(system_command_str)
    os.system(system_command_str)
    restart_windows_bin(ansible_group)


def remove_windows_csscand_conf_file(conf_file_name):
    ansible_group = conf_file_name[8:-5]
    system_command_str = "ansible "+ansible_group+" -m win_shell -a \"Remove-Item -Path 'D:\\\\v0.0.0\\\\conf\\\\"+conf_file_name+"'\""
    print(system_command_str)
    os.system(system_command_str)

    # here, must remove prev_repo_dir's windows csscand conf file,so in deploy stage, the file will consider the new file and deploy(but in this moment,the ansible machine list is not incloud had removed machine)
    system_command_str = "cd "+prev_repo_conf_dir+"conf && rm -f "+conf_file_name+""
    print(system_command_str)
    os.system(system_command_str)


def deploy_csscand_conf(repo_conf_dir, prev_repo_conf_dir):
    repo_conf_list = os.listdir(repo_conf_dir)
    prev_repo_conf_list = os.listdir(prev_repo_conf_dir)
    for conf_file in repo_conf_list:
        if prev_repo_conf_list.count(conf_file):
            print("the conf file had deploy before,we check if it have changed")
            repo_conf_file_md5 = get_file_md5(repo_conf_dir + conf_file)
            prev_repo_conf_file_md5 = get_file_md5(prev_repo_conf_dir + conf_file)
            if repo_conf_file_md5 == prev_repo_conf_file_md5:
                print("the conf file "+conf_file+" do not change,we do not need deploy it")
            else:
                print("the conf file "+conf_file+"had changed, we need deploy the new version")
                engine_name = conf_file[8:-5]
                if linux_engine_list.count(engine_name):
                    deploy_csscand_conf_file(conf_file)
                if windows_engine_list.count(engine_name):
                    deploy_windows_csscand_conf_file(conf_file)

        else:
            print(
                "the conf file "+conf_file+" is new file, we do not deploy it before,now we deploy it"
            )
            engine_name = conf_file[8:-5]
            if linux_engine_list.count(engine_name):
                deploy_csscand_conf_file(conf_file)
            if windows_engine_list.count(engine_name):
                deploy_windows_csscand_conf_file(conf_file)


def deploy_conf(repo_conf_dir, prev_repo_conf_dir):
    repo_conf_list = os.listdir(repo_conf_dir)
    prev_repo_conf_list = os.listdir(prev_repo_conf_dir)
    for conf_file in repo_conf_list:
        if conf_file == 'engines.yaml' or conf_file == 'make_online_scand_conf.sh' or conf_file == 'csscand.yaml':
            continue
        if conf_file == 'supervisord.conf':
            deploy_windows_conf_file(conf_file)
            continue
        if conf_file == 'conf':
            now_conf = repo_conf_dir + conf_file + "/"
            prev_conf = prev_repo_conf_dir + conf_file + "/"
            deploy_csscand_conf(now_conf, prev_conf)
            continue
        if prev_repo_conf_list.count(conf_file):
            print("the conf file "+conf_file+" had deploy before,we check if it have changed")
            repo_conf_file_md5 = get_file_md5(repo_conf_dir + conf_file)
            prev_repo_conf_file_md5 = get_file_md5(prev_repo_conf_dir + conf_file)
            if repo_conf_file_md5 == prev_repo_conf_file_md5:
                print("the conf file "+conf_file+"do not change,we do not need deploy it")
            else:
                print("the conf file "+conf_file+"had changed, we need deploy the new version")
                deploy_conf_file(conf_file)

        else:
            print(
                "the conf file "+conf_file+"is new file, we do not deploy it before,now we deploy it"
            )
            deploy_conf_file(conf_file)


def deploy_systemd_service(repo_systemd_service_dir, prev_repo_systemd_service_dir):
    repo_systemd_service_list = os.listdir(repo_systemd_service_dir)
    prev_repo_systemd_service_list = os.listdir(prev_repo_systemd_service_dir)
    for service_file in repo_systemd_service_list:
        if prev_repo_systemd_service_list.count(service_file):
            print("the service file "+service_file+" had deploy before,we check if it have changed")
            repo_service_file_md5 = get_file_md5(repo_systemd_service_dir + service_file)
            prev_repo_service_file_md5 = get_file_md5(prev_repo_systemd_service_dir + service_file)
            if repo_service_file_md5 == prev_repo_service_file_md5:
                print("the service file "+service_file+"do not change,we do not need deploy it")
            else:
                print("the service file "+service_file+"had changed, we need deploy the new version")
                deploy_service_file(service_file)

        else:
            print(
                "the service file "+service_file+"is new file, we do not deploy it before,now we deploy it"
            )
            deploy_service_file(service_file)


def deploy_timer_service(repo_systemd_service_dir, prev_repo_systemd_service_dir):
    repo_systemd_service_list = os.listdir(repo_systemd_service_dir)
    prev_repo_systemd_service_list = os.listdir(prev_repo_systemd_service_dir)
    for service_file in repo_systemd_service_list:
        if prev_repo_systemd_service_list.count(service_file):
            print("the service file "+service_file+" had deploy before,we check if it have changed")
            repo_service_file_md5 = get_file_md5(repo_systemd_service_dir + service_file)
            prev_repo_service_file_md5 = get_file_md5(prev_repo_systemd_service_dir + service_file)
            if repo_service_file_md5 == prev_repo_service_file_md5:
                print("the service file "+service_file+"do not change,we do not need deploy it")
            else:
                print("the service file "+service_file+"had changed, we need deploy the new version")
                deploy_timer_service_file(service_file)

        else:
            print(
                "the service file "+service_file+"is new file, we do not deploy it before,now we deploy it"
            )
            deploy_timer_service_file(service_file)


def deploy_from_hosts(hosts_dict, prev_hosts_dict):
    for key, value in hosts_dict.items():
        if not prev_hosts_dict.has_section(key):
            # the new ansible group,we must check it is new bin program or new engine,
            # if it is new bin program,we will deploy it in deploy bin conf systemdService stage
            # so here, we do the add new engine stage
            # now, our deploy mode is don't add new engine in new machine,just add engine in old machine,
            # so, we don't deploy cscand bin file.(#deploy_linux_engine_csscand("csscand", key))
            # and,todo support add new engine on new machine. in this monment we must collect all ip from
            # hosts and check if the engine group's ip in there
            if key.find('cs') == -1:
                print(key)
                if linux_engine_list.count(key):
                    print(key)
                    deploy_csscand_conf_file("csscand-"+key+".yaml")
                    deploy_service_file("cs"+key+".service")
                    restart_bin(key)
                if windows_engine_list.count(key):
                    print(key)
                    deploy_windows_csscand_conf_file("csscand-"+key+".yaml")
                    deploy_windows_conf_file("supervisord.conf", key)
                    #deploy_windows_bin("csscand.exe", key)
                    restart_windows_bin(key)
                continue
            else:
                continue
        new_engine_ip_list = list(set(hosts_dict.items(key)).difference(set(prev_hosts_dict.items(key))))
        if not new_engine_ip_list:
            # empty set, there is no machine added
            continue
        else:
            ip_list = []
            for ip_tuple in new_engine_ip_list:
                ip_list.append(ip_tuple[0])
            print(ip_list)
            if linux_engine_list.count(key):
                #now the ansible hosts not support key=value format
                make_online_project_dir(ip_list)
                deploy_csscand_conf_file("csscand-"+key+".yaml", ip_list)
                deploy_service_file("cs"+key+".service", ip_list)
                deploy_bin("csscand", ip_list)
                restart_bin(key, ip_list)
            if windows_engine_list.count(key):
                # now windows deploy all
                deploy_windows_csscand_conf_file("csscand-"+key+".yaml")
                deploy_windows_conf_file("supervisord.conf", key)
                deploy_windows_bin("csscand.exe", key)
                restart_windows_bin(key)
            if bin_list.count(key):
                make_online_project_dir(ip_list)
                deploy_conf_file(key + ".yaml", ip_list)
                deploy_service_file(key+".service", ip_list)
                deploy_bin(key, ip_list)
                restart_bin(key, ip_list)


def remove_from_hosts(hosts_dict, prev_hosts_dict):
    for key, value in prev_hosts_dict.items():
        if not hosts_dict.has_section(key):
            #now,we don't fouse on remove engine or remove program,we just do remove some engine on some machine
            continue
        remove_engine_ip_list = list(set(prev_hosts_dict.items(key)).difference(set(hosts_dict.items(key))))
        if not remove_engine_ip_list:
            # empty set, there is no engine item change
            continue
        else:
            ip_list = []
            for ip_tuple in remove_engine_ip_list:
                ip_list.append(ip_tuple[0])
            print(ip_list)
            print(key)
            if linux_engine_list.count(key):
                # before remove egnine on this machine,we stop this engine's csscand
                stop_csscand_engine_bin(key, ip_list)
                remove_csscand_conf_file("csscand-"+key+".yaml", ip_list)
                remove_csscand_service_file("cs"+key+".service", ip_list)
            if windows_engine_list.count(key):
                # now windows remove all,and deploy all new item in deploy stage
                stop_windows_bin(key)
                remove_windows_csscand_conf_file("csscand-"+key+".yaml")
            if bin_list.count(key):
                stop_bin(key, ip_list)
                remove_bin(key, ip_list)
                remove_bin_conf_file(key+".yaml", ip_list)
                remove_bin_service_file(key+".service", ip_list)



def deploy_timer_script():
    all_linux_list = get_entity_from_hosts(hosts_dir, 'all-linux')
    make_online_project_dir(all_linux_list)
    deploy_timer_service(repo_timer_service_dir,prev_repo_timer_service_dir)
    deploy_timer_script_program(repo_timer_script_dir, prev_repo_timer_script_dir)



@app.route("/", methods=["POST"])
def deployment():
    if request.method == 'POST':
        if request.headers['X-Gitlab-Token'] != valid_token:
            print('wrong action')
            os.exit()
        if request.remote_addr != valid_ip:
            print('wrong user ip')
            os.exit()

        print('right user ip and right aciton begin deploy')
        send_wechat_robot_message("deployment start")

        try:
            shutil.rmtree(prev_repo_dir)
        except Exception as e:
            print('maybe no such dir we have deleted prev_repo_dir')
            print(e)

        os.rename(repo_dir, prev_repo_dir)

        # repo = git.Repo.clone_from(url=git_url, to_path=repo_dir)
        git.Repo.clone_from(url=git_url, to_path=repo_dir)
        # remote = repo.remote()
        try:
            shutil.rmtree(dot_git_dir)
        except Exception as e:
            print('maybe no such dir we have deleted .git')
            print(e)


        # deploy remove engine from machine ,the remove action must before copy ansible hosts
        hosts_dict = get_hosts_dict(hosts_dir)
        prev_hosts_dict = get_hosts_dict(prev_hosts_dir)
        remove_from_hosts(hosts_dict, prev_hosts_dict)

        print('after remove from hosts, we can copy the new ansible hosts to /etc/ansible/hosts,so we have all new resource group')
        os.system("sudo cp "+repo_dir+"hosts /etc/ansible/hosts")

        # deploy from hosts change
        hosts_dict = get_hosts_dict(hosts_dir)
        prev_hosts_dict = get_hosts_dict(prev_hosts_dir)
        deploy_from_hosts(hosts_dict, prev_hosts_dict)

        # deploy conf first
        deploy_conf(repo_conf_dir, prev_repo_conf_dir)

        # deploy systemd servie
        deploy_systemd_service(repo_systemd_service_dir,prev_repo_systemd_service_dir)

        # deploy bin program
        deploy_bin_program(repo_bin_dir, prev_repo_bin_dir)

        # deploy timer script
        deploy_timer_script()


        # commit_log =repo.git.log()
        # log_list = commit_log.split("\n")
        # for item in log_list:
        #    print('begin')
        #    print(item)
        #    print('after')

        print('deploy done, please check wechat message')
        send_wechat_robot_message("deployment done")

        return 'deploy successed'
