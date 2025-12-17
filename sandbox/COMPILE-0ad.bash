#!/usr/bin/env bash
#
# 0AD 0.27.1 (Debian 13) bubblewrap portable app
#

SOFTWARE="0ad_0.27.1-linux64-x86-glibc_2.41"
EXEC="usr/games/0ad"
START="0ad"
URLS="
    https://deb.debian.org/debian/pool/main/0/0ad/0ad_0.27.0-2+b1_amd64.deb
    https://deb.debian.org/debian/pool/main/0/0ad-data/0ad-data_0.27.0-1_all.deb
    https://deb.debian.org/debian/pool/main/0/0ad-data/0ad-data-common_0.27.0-1_all.deb

    https://deb.debian.org/debian/pool/main/b/boost1.83/libboost-filesystem1.83.0_1.83.0-4.2_amd64.deb
    https://deb.debian.org/debian/pool/main/e/enet/libenet7_1.3.18+ds-1+b1_amd64.deb
    https://deb.debian.org/debian/pool/main/f/fmtlib/libfmt10_10.1.1+ds1-4_amd64.deb
    https://deb.debian.org/debian/pool/main/f/fonts-freefont/fonts-freefont-ttf_20211204+svn4273-2_all.deb
    https://deb.debian.org/debian/pool/main/g/gloox/libgloox18_1.0.28-1+b3_amd64.deb
    https://deb.debian.org/debian/pool/main/m/miniupnpc/libminiupnpc18_2.2.8-2+b2_amd64.deb
    https://deb.debian.org/debian/pool/main/p/pcre2/libpcre2-32-0_10.46-1~deb13u1_amd64.deb
    https://deb.debian.org/debian/pool/main/t/tex-gyre/fonts-texgyre_20180621-6_all.deb
    https://deb.debian.org/debian/pool/main/w/wxwidgets3.2/libwxbase3.2-1t64_3.2.8+dfsg-2_amd64.deb
    https://deb.debian.org/debian/pool/main/w/wxwidgets3.2/libwxgtk-gl3.2-1t64_3.2.8+dfsg-2_amd64.deb
    https://deb.debian.org/debian/pool/main/w/wxwidgets3.2/libwxgtk3.2-1t64_3.2.8+dfsg-2_amd64.deb

    https://deb.debian.org/debian/pool/main/g/glibc/libc6_2.41-12_amd64.deb
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
