#!/usr/bin/env bash

cd "${0%/*}/.."

for HOST in $*
do
    ANSIBLE_USER=$(ansible-inventory --inventory=inventory/my_nodes --host "$HOST" --yaml 2> /dev/null | awk '/ansible_user: / {printf("%s@", $2)}')
    for KEY in $(ssh -G "$ANSIBLE_USER$HOST" 2> /dev/null | awk '/^identityfile / {print $2}' | sed -e "s@\~@$HOME@")
    do
        if [ -f "$KEY" ]
        then
            ID=$(awk '{print $3}' "$KEY.pub" 2> /dev/null)
            if [ ! "$(ssh-add -l 2> /dev/null | grep -E " ($KEY|$ID) ")" -a "$SSH_AUTH_SOCK" ]
            then
                echo -e "\033[33mSSH key for $ANSIBLE_USER$HOST: ssh-add $KEY\033[0m"
                ssh-add $KEY
            fi
            break
        fi
    done
done
