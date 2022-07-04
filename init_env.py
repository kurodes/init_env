#!/usr/bin/env python3

# Please make sure this script is idempotent.
# 
# When use ssh remote command, you should be careful that:
#       1. The shell used by ssh remote commmand is a non-interactive shell,
#           so ssh remote command will not initiate the login environment using .zshrc.
#       2. Take care of the quoting (' and ") of commands.
#       3. Take care of the heredoc.



import subprocess as sp
import shlex
import sys
from time import sleep
from typing import Text

# SERVER = '166.111.69.18'
# USER = 'kuro'
SERVER = '10.0.2.148'
USER = 'lwh'
PORT = 22

GH_TOKEN = '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'

def local_cmd(cmd_str, retry=True):
    print(cmd_str)
    print(shlex.split(cmd_str))
    ret = sp.run(shlex.split(cmd_str), stdout=sp.PIPE, stderr=sp.STDOUT, text=True)
    if ret.returncode != 0:
        if retry:
            print('\033[31m' + ret.stdout + '\033[0m')
            sleep(1)
            local_cmd(cmd_str, retry=True)
        else:
            print('\033[31m' + ret.stdout + '\033[0m')
    else:
        print(ret.stdout)
    return ret.returncode


def local_cmd_bg(cmd_str):
    print(shlex.split(cmd_str))
    sp.Popen(shlex.split(cmd_str), stdout=sp.PIPE, stderr=sp.STDOUT, text=True)


def ssh_cmd(cmd_str, retry=True):
    return local_cmd(f'ssh -p {PORT} {USER}@{SERVER} {shlex.quote(cmd_str)}', retry)


def print_step(msg):
    print('\033[32m' + msg + '\033[0m')


if __name__ == "__main__":
    print(f'Prerequisites: \n\t1.You can ssh into USER@SERVER -p PORT w/o a password; \n\t2.USER can sudo w/o password.')
    ans = input(f'SERVER={SERVER}, USER={USER}, PORT={PORT} [y/n] ')
    if ans != 'y':
        if ans == 'n':
            SERVER = input('SERVER: ')
            USER = input('USER: ')
            PORT = input('PORT: ')
        else:
            print('Invalid input.')
            sys.exit(1)

    print_step('Forward network requests to the clash on the localhost')
    local_cmd_bg(f'ssh -NR 7890:127.0.0.1:7890 {USER}@{SERVER}')
    sleep(1)

    print_step('Install usefull tools')
    ssh_cmd('sudo apt-get install -y '
                          'zsh vim tmux htop tree build-essential cmake curl git most tldr hardinfo')
    
    print_step('Install prerequisites for kernel building')
    ssh_cmd('sudo apt-get install -y '
                          'git fakeroot build-essential ncurses-dev xz-utils libssl-dev bc flex libelf-dev bison dwarves zstd')

    print_step('Install gh')
    while ssh_cmd('gh --version', False) != 0:
        ssh_cmd("""
        curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
        sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
        sudo apt update
        sudo apt install gh
        """, False)
    
    print_step('Install from deb package: duf, btm')
    while ssh_cmd('duf --version', False) != 0:
        ssh_cmd(f'''
            rm -f /tmp/duf*amd64.deb
            export GH_TOKEN={GH_TOKEN}
            gh release download --pattern "duf*amd64.deb" -R https://github.com/muesli/duf -D /tmp
            sudo dpkg -i /tmp/duf*amd64.deb
            ''', False)
    while ssh_cmd('btm --version', False) != 0:
        ssh_cmd(f'''
            rm -f /tmp/bottom*amd64.deb
            export GH_TOKEN={GH_TOKEN}
            gh release download --pattern "bottom*amd64.deb" -R https://github.com/ClementTsang/bottom -D /tmp
            sudo dpkg -i /tmp/bottom*amd64.deb
            ''', False)

    print_step('Setup oh-my-zsh')
    ssh_cmd(f'sudo chsh -s /bin/zsh {USER}')

    print_step('Setup oh-my-zsh -> install oh-my-zsh')
    while ssh_cmd('[[ -e ~/.zshrc ]] && source ~/.zshrc && omz version', retry=False) != 0:
        ssh_cmd('[[ ! -e ~/.oh-my-zsh ]] || rm -rf ~/.oh-my-zsh')
        ssh_cmd('export all_proxy=socks5://127.0.0.1:7890; sleep 3; '
                              'sh -c \"$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)\"', False)

    print_step('Setup oh-my-zsh -> setup git proxy')
    sleep(1)
    ssh_cmd('git config --global http.proxy socks5://127.0.0.1:7890')

    print_step('Setup oh-my-zsh -> install plugins')
    LOCATION = '${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions'
    ssh_cmd(f'[[ -e {LOCATION} ]] || '
                          f'git clone https://github.com/zsh-users/zsh-autosuggestions {LOCATION}')
    LOCATION = '${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting'
    ssh_cmd(f'[[ -e {LOCATION} ]] || '
                          f'git clone https://github.com/zsh-users/zsh-syntax-highlighting.git {LOCATION}')
    LOCATION = '~/.fzf'
    ssh_cmd(f'[[ -e {LOCATION} ]] || '
                          f'(git clone https://github.com/junegunn/fzf.git {LOCATION}; '
                          f'echo y | {LOCATION}/install)')
    LOCATION = '${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/fzf-tab'
    ssh_cmd(f'[[ -e {LOCATION} ]] || '
                          f'git clone https://github.com/Aloxaf/fzf-tab.git {LOCATION}')

    print_step('Setup oh-my-zsh -> update ~/.zshrc')
    local_cmd(f'scp conf/zshrc {USER}@{SERVER}:~/.zshrc')

    print_step('Setup oh-my-zsh -> unset git proxy')
    ssh_cmd('git config --global --unset http.proxy')

    print_step('Setup git')
    ssh_cmd('git config --global user.email kuro_des@icloud.com')
    ssh_cmd('git config --global user.name kurodes')
    ssh_cmd('git config --global init.defaultBranch main')

    print_step('Setup tmux')
    local_cmd(f'scp conf/tmux.conf {USER}@{SERVER}:~/.tmux.conf')
    
    print_step('Setup vim')
    local_cmd(f'scp conf/vimrc {USER}@{SERVER}:~/.vimrc')

    print_step('Performance tuning')
    ssh_cmd('[[ -e /sys/devices/system/cpu/cpu0/cpufreq ]] && '
            'echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor', False)
