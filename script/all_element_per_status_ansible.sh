#!/bin/bash

ansible kkinterface -m shell -a 'systemctl status kkinterface' 
ansible kkagg -m shell -a 'systemctl status kkagg' 
ansible kkpost -m shell -a 'for i in {1..6};do sudo systemctl status kkpost@post$i;done' 



