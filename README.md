# 1996-2024 By Dr Colin Kong

These are production scripts and configuration files that I use and share. Originally the scripts
were started Bourne shell scripts started during my University days and continuously enhanced over
the years.

---
```
 * Jenkinsfile                     Jenkins pipeline configuration file
 * codefresh.yaml                  Codefresh pipeline configuration file
 * Makefile                        Makefile for testing
 * .gitattributes                  GIT settings (LFS support)
 * .pylintrc                       Python Pylint configuration file
 * bin/command_mod.py              Python command line handling module
 * bin/config_mod.py               Python configuration module
 * bin/config_mod.yaml             Python configuration YAML file
 * bin/crypt_mod.bash              Bash encrypted partitions handling module
 * bin/debug_mod.py                Python debugging tools module
 * bin/desktop_mod.py              Python graphical desktop module
 * bin/docker_mod.bash             Bash Docker utilities module
 * bin/file_mod.py                 Python file handling utility module
 * bin/git_mod.bash                Git utilities module
 * bin/host_mod.bash               Bash host connection utilities module
 * bin/logging_mod.py              Python log handling module
 * bin/network_mod.py              Python network handling utility module
 * bin/power_mod.py                Python power handling module
 * bin/pyld_mod.bash               Bash Python launcher module
 * bin/pyld_mod.py                 Python main program loader module
 * bin/qemu_mod.bash               Bash QEMU image file utilities module
 * bin/safe_mod.bash               Bash safe command module
 * bin/subtask_mod.py              Python sub task handling module
 * bin/task_mod.py                 Python task handling utility module
 * bin/venv_mod.bash               Bash Python Virtual Environments module
 * bin/python*                     Python startup wrapper
 * bin/*                           Python utilities and wrapper scripts
 * ansible/                        Ansible for local hosts
 * appimage/Makefile
 * appimage/bin/
 * appimage/0ad-0.0.26-deb11/      0AD 0.0.26 (Debian 11 backports) appimage
 * appimage/0ad-0.0.26-deb12/      0AD 0.0.26 (Debian 12) appimage
 * appimage/bash-5.1.4-deb11/      Bash 5.1.4 (Debian 11) appimage
 * appimage/bash-5.2.15-deb12/     Bash 5.2.15 (Debian 12) appimage
 * appimage/vlc-3.0.18-deb12/      VLC 3.0.18 (Debian 12) appimage
 * appimage/wesnoth-1.14.15-deb11/ Wesnoth 1.14.15 (Debian 11) appimage
 * appimage/wesnoth-1.16.8-deb11/  Wesnoth 1.16.8 (Debian 11 backports) appimage
 * appimage/wesnoth-1.16.9-deb12/  Wesnoth 1.16.9 (Debian 12) appimage
 * compile/                        Build scripts of open source software
 * config/Xresources               Copy to "$HOME/.Xresources" to set xterm resources
 * config/accels                   Copy to "$HOME/.config/geeqie" for keyboard shortcuts
 * config/adblock.txt              Adblock filter list
 * config/autostart.bash           Copy to "$HOME/.config/autostart.bash" & add to desktop auto startup
 * config/autostart-opt.bash       Copy to "$HOME/.config/autostart-opt.bash" for optional settings
 * config/autostart.desktop        Copy to "$HOME/.config/autostart/autostart.desktop" for XFCE autostart
 * config/config                   Copy to "$HOME/.ssh/config"
 * config/config-opt               Copy to "$HOME/.ssh/config-opt"
 * config/gitconfig                Copy to "$HOME/.gitconfig" and edit
 * config/iptables.conf            IPTABLES setup script
 * config/login                    Copy to "$HOME/.login" for csh/tcsh shells (translated ".profile")
 * config/mimeapps.list            Copy to "$HOME/.local/share/applications" for Mime definitions
 * config/minttyrc                 Copy to "$HOME/.minttyrc" for MSYS2 terminal
 * config/tmux.conf                Copy to "$HOME/.tmux.conf" fro TMUX terminal
 * config/profile                  Copy to "$HOME/.profile" for ksh/ash/bash shells settings
 * config/profile-opt              Copy to "$HOME/.profile-opt" for optional ksh/bash shells settings
 * config/rc.local                 Copy to "/etc/rc.local" for system startup commands
 * config/rc.local-opt             Copy to "/etc/rc.local-opt" for optional system startup commands
 * config/terminalrc               Copy to "$HOME/.config/xfce4/terminal" for XFCE terminal
 * config/vimrc                    Copy to "$HOME/.vimrc" for VIM defaults
 * config/userapp-evince.desktop   Copy to "$HOME/.local/share/applications" for Evince/Atril
 * config/userapp-gqview.desktop   Copy to "$HOME/.local/share/applications" for GQview/Geeqie
 * config/userapp-soffice.desktop  Copy to "$HOME/.local/share/applications" for LibreOffice
 * config/userapp-vlc.desktop      Copy to "$HOME/.local/share/applications" for VLC
 * config/vm-linux0.vbox           VirtualBox Linux example
 * config/vm-win10.vbox            VirtualBox Windows example
 * config/setup.bat                Configure Windows QEMU/VirtualBox VMs
 * config/setupwin.ash
 * config/xscreensaver             Copy to "$HOME/.xscreensaver" for XScreenSaver defaults
 * cloudformation/1pxy/            pxy CloudFormation example
 * cloudformation/multi-stacks/    multi-stacks CloudFormation example
 * cookiecutter/                   Cookie cutter example for Docker projects
 * docker/Makefile
 * docker/bin/
 * docker/almalinux-8/             almalinux:8 based Docker images
 * docker/almalinux-9/             almalinux:9 based Docker images
 * docker/alpine-3.17/             alpine:3.17 based Docker images
 * docker/alpine-3.18/             alpine:3.18 based Docker images
 * docker/busybox-1.36/            busybox:1.36 based Docker images
 * docker/centos-7/                centos:7 based Docker images
 * docker/debian-10/               debian:10-slim based Docker images
 * docker/debian-11/               debian:11-slim based Docker images
 * docker/debian-12/               debian:12-slim based Docker images
 * docker/golang-1.19/             golang:1.19-alpine based GO compiler app
 * docker/httpd-2.4/               httpd:2.4-alpine (Apache) based web server
 * docker/i386-alpine-3.18/        i386/alpine:3.18 based based Docker images
 * docker/i386-debian-11/          i386/debian:11-slim based Docker images
 * docker/i386-debian-12/          i386/debian:12-slim based Docker images
 * docker/nginx-1.24/              nginx:1.24-bullseye based reverse proxy server
 * docker/oraclelinux-8/           oralcelinux:8 based Docker images
 * docker/oraclelinux-9/           oralcelinux:9 based Docker images
 * docker/python-3.12/             python:3.12-slim-bookworm based Docker images
 * docker/registry-2.6/            registry:2.6 based Docker Registry server app
 * docker/scratch/                 scratch Docker image
 * docker/ubuntu-18.04/            ubuntu:18.04 based Docker images
 * docker/ubuntu-20.04/            ubuntu:20.04 based Docker images
 * docker/ubuntu-22.04/            ubuntu:22.04 based Docker images
 * etc/python-packages.bash        Install/check Python packages requirements
 * etc/python-requirements.txt     Default requirements file for Python
 * etc/python-requirements_*.txt   Additional requirements for Python versions
 * etc/setbin                      Hybrid Bourne/C-shell script for sh/ksh/bash/csh/tcsh initialization
 * etc/setbin.bat                  Windows Command prompt initialization
 * etc/setbin.ps1                  Windows Power shell initialization
 * kubernetes/Makefile
 * kubernetes/bin/
 * kubernetes/monitor-host/        Kubernetes: host monitoring (drtuxwang/debian-ops:stable)
 * kubernetes/nginx-proxy-fwd/     NGINX http/https proxy forwarding example
 * kubernetes/test-box/            Kubernetes: Test Box (drtuxwang/debian-ops:stable)
 * kubernetes/test-server/         Kubernetes: examples (drtuxwang/debian-ops:stable)
 * kubernetes/socat-fwd/           SOCAT forwarding example
 * kubernetes/test-cronjob/        Kubernetes: cronjob example (drtuxwang/busybox-bash:stable)
 * kubernetes/test-storage/        Kubernetes: Persistent Volume example
 * helm/Makefile
 * helm/bin/
 * helm/cassandra/                 Helm Chart: bitnami/cassandra 10.7.1 (app-3.11.13)
 * helm/etcd/                      Helm Chart: bitnami/etcd 9.9.1 (app-3.4.29)
 * helm/grafana/                   Helm Chart: bitnami/grafana 9.7.1 (app-9.5.6)
 * helm/jenkins/                   Helm Chart: bitnami/jenkins 12.5.1 (app-2.414.3)
 * helm/kafka/                     Helm Chart: bitnami/kafka 26.7.1 (app-3.5.2)
 * helm/mongodb/                   Helm Chart: bitnami/mongodb 14.6.1 (app-5.0.24)
 * helm/nexus/                     Helm Chart: oteemo/sonatype-nexus 5.4.1 (app-3.27.0)
 * helm/nginx/                     Helm Chart: bitnami/nginx 15.8.1 (app-1.18.0)
 * helm/oracle-xe/                 Helm Chart: Oracle XE test (gvenzl/oracle-xe:21.3.0-slim)
 * helm/postgresql/                Helm Chart: bitnami/postgresql 13.2.30 (app-11.22.0)
 * helm/prometheus/                Helm Chart: prometheus-community/prometheus 25.8.2 (app-2.37.8)
 * helm/pushgateway/               Helm Chart: prometheus-community/prometheus-pushgateway 2.4.2 (app-1.3.1)
 * helm/rabbitmq/                  Helm Chart: bitnami/rabbitmq 12.6.3 (app-3.10.25)
 * helm/test-box/                  Helm Chart: drtuxwang/test-box (drtuxwang/debian-ops:stable)
 * helm/test-server/               Helm Chart: drtuxwang/test-server (drtuxwang/debian-ops:stable)
 * helm/xfce-server/               Helm Chart: drtuxwang/xfce-server (drtuxwang/debian-xfce:stable)
 * python/simple-cython/           Simple Cython example
 * python/simple-flask/            Simple Flask demo
 * python/simple-package/          Simple Egg & WHL package
 * python/simple-tornado/          Tornado examples
 * qemu/*.vm.bash                  QEMU VM examples
 * qemu-system-aarch64.bash        QEMU System aarch64 (arm64) wrapper
 * qemu-system-x86_64.bash         QEMU System x86_64 (amd64) wrapper
 * terraform-aws/1pxy/             Terraform AWS: 1pxy example
 * terraform-aws/pxy-as/           Terraform AWS: pxy-as example
 * wipe/                           Disk wipe utility
 * zhspeak/                        Zhong Hua Speak 6.2.0 TTS software and data
```
