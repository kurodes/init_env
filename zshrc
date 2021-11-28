export ZSH="/home/lwh/.oh-my-zsh"
ZSH_THEME="agnoster"
plugins=(
    git
    fzf-tab
    autojump
    zsh-autosuggestions
    zsh-syntax-highlighting
)
source $ZSH/oh-my-zsh.sh
export PAGER="most"
export all_proxy=socks5://10.0.2.207:7890
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh
