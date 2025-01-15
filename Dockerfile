FROM archlinux

# 更新系统并安装必要的软件
RUN pacman -Syu --noconfirm \
    openssh \
    python \
    python-pip \
    sudo \
    && pacman -Scc --noconfirm

WORKDIR /app
