# gitlab-flask-ansible-delivery-system
gitlab-flask-ansible-delivery-system


此项目实现了gitops思想，一切资源由git管理，git上的变更触发发布。


此项目实现了声明式API，虽然不是kubernetes项目，但是项目本身使用了控制器模式的开发思想，
调谐的逻辑，使线上实际状态达成期望状态。


这里的期望状态是用ansible的hosts声明的，一方面ansible的hosts做为ansible自动化的机器ip来源，
另一方面因为这个文件本身就是ini格式的配置文件，且也说明了项目的机器与业务程序分布，所以就可以
做为期望的状态。



项目目录解读：


gitlab-flask-ansible-delivery-system/systemdService

可执行程序的systemd service文件所在目录。这个项目里程序使用systemd进行管理。

目录里分别有：

kkinterface.service

kkagg.service

kkpost.service

三个systemd service文件，分别对应kkinterface，kkagg，kkpost三个可执行程序




gitlab-flask-ansible-delivery-system/bin    可执行程序所在目录（这里因为网络原因没有upload编译好的二进制go程序，直接放的go源代码作为示范例子）

目录里分别有：

kkinterface

kkagg

kkpost

三个示范可执行程序



gitlab-flask-ansible-delivery-system/conf   项目配置文件所在目录

目录里分别有：

kkinterface.yaml

kkagg.yaml

kkpost.yaml

三个配置文件，分别与bin目录里的三个可执行程序相对应




---------------------------------------------------------------------------------------------------------------------

统一的定时任务脚本管理，用gitops的方法管理多集群的定时任务。
使用systemd 的timer单元服务
配合ansible  hosts声明：
[script-online-deployment]
online_script_dir-/opt/cloudscan/script/

[clean-var-log]
1.1.1.1
2.2.2.2
3.3.3.3
4.4.4.4
33.33.33.33
44.44.44.44
55.55.55.55

例如，
实现集群内所有机器系统日志的清理，只保留最近一周的日志，定期删除一周之前的日志。
程序在：
/timerScript/clean-var-log.sh
systemd timer+service 实现的定时任务配置文件在：
/timerService/clean-var-log.service
/timerService/clean-var-log.timer

python发布程序/delivery.py  会根据hosts声明在每台机器上依照标准化创建/opt/cloudscan/script/目录，并把脚本程序clean-var-log.sh放入这个目录。
然后根据hosts声明在每台机器将clean-var-log.service和clean-var-log.timer放入/usr/lib/systemd/system目录，然后用systemctl启动clean-var-log.timer。
这样就实现了集群内每一台机器的定时任务程序管理。

根据需要，扩展其他任务时，只需在git内建立相应的文件，更新hosts声明即可。实现gitops+声明式发布。
