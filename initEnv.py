#!/usr/bin/env python3

# This script configures the target machine by using the root kuser

# This script is idempotent

import subprocess as sp
import shlex

knode = '10.0.2.148'
kuser = 'lala'
kpasswd = 'Wenhao1998'


def remoteCmd(kuser, knode, remote_cmd, check=True):
    cmd = f'ssh {kuser}@{knode} {shlex.quote(remote_cmd)}'
    print(cmd)
    args = shlex.split(cmd)
    print(args)
    ret = sp.run(args, stdout=sp.PIPE, stderr=sp.STDOUT, check=False)
    if check and ret.returncode != 0:
        raise Exception(ret.stdout.decode())
    print(ret.stdout.decode())


def localCmd(local_cmd, check=True):
    ret = sp.run(shlex.split(local_cmd), stdout=sp.PIPE,
                 stderr=sp.STDOUT, check=False)
    if check and ret.returncode != 0:
        raise Exception(ret.stdout.decode())
    print(ret.stdout.decode())


if __name__ == "__main__":
    print('Create kuser')
    remoteCmd('root', knode,
              f'useradd --create-home {kuser} && echo {kuser}:{kpasswd} | chpasswd', False)

    print('Grant Root')
    remoteCmd('root', knode, 'grep {} /etc/sudoers || echo {} >> /etc/sudoers'.format(
        kuser, shlex.quote(f'{kuser} ALL=(ALL) NOPASSWD:ALL')))

    print('Install public key')
    localCmd(
        f'sshpass -p {kpasswd} ssh-copy-id -o StrictHostKeyChecking=no {kuser}@{knode}')

    print('Install Dependencies')
    remoteCmd('root', knode,
              'sudo apt-get install zsh htop tree autojump build-essential curl git most -y')

    print('Config Git')
    remoteCmd(kuser, knode, 'git config --global user.email "kuro_des@icloud.com"')
    remoteCmd(kuser, knode, 'git config --global user.name "kurodes"')

    print('Zsh as Default')
    remoteCmd('root', knode, f'chsh -s /bin/zsh {kuser}')

    print('On My Zsh')
    remoteCmd(kuser, knode, 'grep all_proxy ~/.zshrc || \
        echo {} >> ~/.zshrc'.format(shlex.quote('export all_proxy=socks5://10.0.2.207:7890')))
    # if you want $() be evaluated on remote server, then use double quote and not use shlex.quote
    remoteCmd(kuser, knode, '[[ -e ~/.oh-my-zsh ]] || \
        sh -c \"$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)\"')
    # remoteCmd(kuser, knode, 'grep all_proxy ~/.zshrc || \
    #     echo {} >> ~/.zshrc'.format(shlex.quote('export all_proxy=socks5://10.0.2.207:7890')))
    remoteCmd(kuser, knode, '[[ -e ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions ]] || \
        git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions')
    remoteCmd(kuser, knode, '[[ -e ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting ]] || \
        git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting')
    remoteCmd(kuser, knode, '[[ -e ~/.fzf ]] || \
        (git clone --depth 1 http://github.com/junegunn/fzf.git ~/.fzf; echo y | ~/.fzf/install)')
    remoteCmd(kuser, knode, '[[ -e ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/fzf-tab ]] || \
        git clone https://github.com/Aloxaf/fzf-tab ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/fzf-tab')
    localCmd(f'scp zshrc {kuser}@{knode}:~/.zshrc')


    # p = subprocess.Popen(shlex.split(f'ssh root@{knode} \'passwd {kuser}\''), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # p.stdin.write('Wenhao1998=\n'.encode())
    # p.stdin.write('Wenhao1998=\n'.encode())
    # print(p.communicate()[0].decode())
    # p.wait(timeout=10)
    # p.returncode != 0: raise Exception(p.stdout.decode())


    # start = timer()
    # with Popen("bash ./start_client.sh " + str(s_th) + " " + str(c_th), shell=True, stdout=PIPE, preexec_fn=os.setsid) as process:
    #     try:
    #         output = process.communicate(timeout=60 * 8)[0]
    #     except TimeoutExpired:
    #         os.killpg(process.pid, signal.SIGINT) # send signal to the process group
    #         output = process.communicate()[0]
    #     print('Elapsed seconds: {:.2f}'.format(timer() - start))
    