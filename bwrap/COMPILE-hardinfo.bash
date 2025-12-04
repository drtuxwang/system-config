#!/usr/bin/env bash
#
# Create hardinfo portable app
#

SOFTWARE="hardinfo_0.5.1-linux64-x86-glibc_2.36"
EXEC="usr/bin/hardinfo"
START="hardinfo"
URLS="
    https://deb.debian.org/debian/pool/main/h/hardinfo/hardinfo_0.5.1+git20180227-2.1+b1_amd64.deb
"

# Download and unpack
for URL in $URLS
do
    wget --timestamping "$URL" || exit 1
done
rm -rf "$SOFTWARE" && mkdir -p "$SOFTWARE"
for URL in $URLS
do
    DEB=${URL##*/}
    echo "=> $SOFTWARE  # Unpack $DEB"
    rm -f data.tar.*
    ar x $DEB || exit 1
    tar xf data.tar.* -C "$SOFTWARE" || exit 1
done
rm -rf "$SOFTWARE/etc"

# Setup startup
echo "=> $SOFTWARE/$START"
ln -sf "$EXEC" "$SOFTWARE/$START"
touch -r "$SOFTWARE/$EXEC" "$SOFTWARE/$START.bwrap"
echo "=> $SOFTWARE/$START.bwrap"
cat > "$SOFTWARE/$START.bwrap" << EOF
#!/usr/bin/env bash

MYDIR=\$(realpath "\${0%/*}")
/usr/bin/bwrap \\
    --ro-bind / / \\
    --tmpfs /home \\
    --tmpfs /media \\
    --tmpfs /mnt \\
    --tmpfs /srv \\
    --tmpfs /tmp \\
    --dev dev \\
    --ro-bind-try "\$MYDIR" "\$MYDIR" \\
    --dev-bind-try /dev/dri /dev/dri \\
    --bind-try /run/user/\$(id -u)/pulse /run/user/\$(id -u)/pulse \\
    --bind-try \$HOME/.config/0ad \$HOME/.config/0ad \\
    --overlay-src /usr --overlay-src "\$MYDIR/usr" --ro-overlay /usr \\
    -- "\$MYDIR/$START"
EOF
chmod 755 "$SOFTWARE/$START.bwrap"

echo "DONE!"
