#!/bin/bash

ansible kkpost -m shell -a 'for i in {1..6};do sudo systemctl status kkpost@post$i;done' 
ansible kkagg -m shell -a 'systemctl status kkagg' 
ansible kkfront -m shell -a 'systemctl status kkfront' 
ansible kkinterface -m shell -a 'systemctl status kkinterface' 
