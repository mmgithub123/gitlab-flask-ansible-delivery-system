# gitlab-flask-ansible-delivery-system
gitlab-flask-ansible-delivery-system

此项目实现了gitops思想，一切资源由git管理，git上的变更触发发布。
此项目实现了声明式API，虽然不是kubernetes项目，但是项目本身使用了控制器模式的开发思想，
调谐的逻辑，使线上实际状态达成期望状态。
这里的期望状态是用ansible的hosts声明的，一方面ansible的hosts做为ansible自动化的数据来源，
另一方面因为这个文件本身就是ini格式的配置文件，且也说明了项目的机器与业务程序分布，所以就可以
做为期望的状态。

项目目录解读：

