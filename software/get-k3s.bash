#!/usr/bin/env bash
#
# K3S 1.31.14-1 (Official) portable app
#

set -e


app_settings() {
    NAME="k3s"
    VERSION="1.31.14+k3s1"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_${VERSION//+k3s/-}-$PORT"
    APP_FILES="
        https://github.com/k3s-io/k3s/releases/download/v$VERSION/k3s
        https://github.com/k3s-io/k3s/releases/download/v$VERSION/k3s-airgap-images-amd64.tar.zst
    "
    APP_SHELL='
        cat << EOF > k3s-server
#!/usr/bin/env bash

CLASS=\${1:-}
if [ ! "\$CLASS" ]
then
    echo "Usage: \$0 \$(ls -1t "\${0%/*}/.."/*linux64*x86*/k3s-[1-9]* 2> /dev/null | sort -n | sed -e "s/.*k3s-//;s/[.][^.]*$//" | uniq | tr "\\n" "|" | sed -e "s/|$//")"
    exit 1
fi
shift

VERSION=\$(ls -1t "\${0%/*}/.."/*linux64*x86*/k3s-\$CLASS.* 2> /dev/null | sort -n | tail -n 1)
if [ ! -f "\$VERSION" ]
then
    echo "\$0: ***ERROR*** Cannot find \"k3s-\$CLASS.*\" executable."
    exit 1
fi

echo "\$(realpath "\$VERSION") server \$@"
sleep 2
exec "\$VERSION" server --write-kubeconfig-mode 755 "\$@"
EOF
        cat << EOF > crictl
#!/usr/bin/env bash

DEFAULT=\$(ls -1t "\${0%/*}/.."/*linux64*x86*/k3s-[1-9]* 2> /dev/null | sort -n | tail -n 1)
CLASS=\$("\$DEFAULT" kubectl version 2> /dev/null | grep "^Server.*v" | sed -e "s/.*v//" | cut -f1-2 -d.)
VERSION=\$(ls -1t "\${0%/*}/.."/*linux64*x86*/k3s-\$CLASS.* 2> /dev/null | sort -n | tail -n 1)

if [ -x "\$VERSION" ]
then
    exec "\$VERSION" "\${0##*/}" "\$@"
else
    exec "\$DEFAULT" "\${0##*/}" "\$@"
fi
EOF
        cp -p crictl kubectl
        mv k3s k3s-'${VERSION//+k3s/-}'
        ln -sf k3s-'${VERSION//+k3s/-}' k3s
        chmod 755 k3s* crictl kubectl
        touch -r k3s-'${VERSION//+k3s/-}' k3s k3s-server crictl kubectl

        cat repositories | tr , "\n" | cut -f2-4 -d\" | sed -e "s/.:../:/" | \
            sort > ../k3s-rancher_'${VERSION//+k3s/-}'.tar.list
        tar ../k3s-rancher_'${VERSION//+k3s/-}'.tar.7z blobs index.json manifest.json oci-layout repositories
        touch -r ../Downloads/k3s-airgap-images-amd64.tar.zst ../k3s-rancher_'${VERSION//+k3s/-}'.tar.*
        rm -rf blobs index.json manifest.json oci-layout repositories
    '
    APP_START="k3s"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    exec "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" app_settings
