"""
    使用SSH连接
"""

import paramiko


def ssh_command(ip, user, passwd, command):
    # 实例化SSHClient
    client = paramiko.SSHClient()
    # 使用秘钥认证
    # client.load_host_keys('/home/justin/.ssh/know_hosts')
    # 保存密码
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接目标服务器
    client.connect(ip, username=user, password=passwd)
    # 打开会话
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)      # 发送命令
        print(ssh_session.recv(1024).decode())       # 返回命令执行结果
    return

ssh_command('10.10.10.61', 'zhang', 'ksbios', 'dir')