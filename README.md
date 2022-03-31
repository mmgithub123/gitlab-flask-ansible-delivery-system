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
