#!/usr/bin/env bash
#
# Create BubbleWrap portable app
#

SOFTWARE="wesnoth_1.18.5-linux64-x86-glibc_2.41"
EXEC="usr/games/wesnoth-1.18"
START="wesnoth"

URLS="
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18_1.18.5-1_amd64.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-data_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-did_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-dm_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-dw_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-ei_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-httt_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-l_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-low_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-music_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-nr_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-server_1.18.5-1_amd64.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-sof_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-sota_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-sotbe_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-thot_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-tools_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-trow_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-tsg_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-ttb_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-utbs_1.18.5-1_all.deb
    https://deb.debian.org/debian/pool/main/w/wesnoth-1.18/wesnoth-1.18-wof_1.18.5-1_all.deb

    https://deb.debian.org/debian/pool/main/b/boost1.83/libboost-filesystem1.83.0_1.83.0-4.2_amd64.deb
    https://deb.debian.org/debian/pool/main/b/boost1.83/libboost-iostreams1.83.0_1.83.0-4.2_amd64.deb
    https://deb.debian.org/debian/pool/main/b/boost1.83/libboost-locale1.83.0_1.83.0-4.2_amd64.deb
    https://deb.debian.org/debian/pool/main/b/boost1.83/libboost-program-options1.83.0_1.83.0-4.2_amd64.deb
    https://deb.debian.org/debian/pool/main/b/boost1.83/libboost-random1.83.0_1.83.0-4.2_amd64.deb
    https://deb.debian.org/debian/pool/main/b/boost1.83/libboost-thread1.83.0_1.83.0-4.2_amd64.deb
    https://deb.debian.org/debian/pool/main/f/fonts-adf/fonts-adf-oldania_0.20190904-3_all.deb
    https://deb.debian.org/debian/pool/main/f/fonts-android/fonts-droid-fallback_8.1.0r7-1~1.gbp36536b_all.deb
    https://deb.debian.org/debian/pool/main/f/fonts-lato/fonts-lato_2.015-1_all.deb
    https://deb.debian.org/debian/pool/main/f/fonts-lohit-beng-bengali/fonts-lohit-beng-bengali_2.91.5-3_all.deb
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
    --dev-bind-try /dev/shm /dev/shm \\
    --bind-try /run/user/\$(id -u)/pulse /run/user/\$(id -u)/pulse \\
    --bind-try \$HOME/.config/wesnoth \$HOME/.config \\
    --overlay-src /usr --overlay-src "\$MYDIR/usr" --ro-overlay /usr \\
    -- "\$MYDIR/$START"
EOF
chmod 755 "$SOFTWARE/$START.bwrap"

echo "DONE!"
