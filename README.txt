1996-2016 By Dr Colin Kong

These are production scripts and configuration files that I use and share. Originally the scripts
were started Bourne shell scripts started during my University days and continuously enhanced over
the years. Now most of the scripts are written in Python 3.

Makefile               Makefile for testing

bin/command_mod.py     Python command line handling module
bin/debug_mod.py       Python debugging tools module
bin/desktop_mod.py     Python X-windows desktop module
bin/file_mod.py        Python file handling utility module
bin/network_mod.py     Python network handling utility module
bin/power_mod.py       Python power handling module
bin/subtask_mod.py     Python sub task handling module
bin/task_mod.py        Python task handling utility module [Draft]

bin/7z                 Make a compressed archive in 7z format
bin/7z.bat             (uses p7zip)
bin/7za
bin/p7zip.py

bin/aftp               Automatic connection to FTP server anonymously
bin/aftp.py

bin/alarmclock         alarmclock wrapper (allowing non systems port)
bin/alarmclock.py

bin/aplay              Play MP3/OGG/WAV audio files in directory

bin/aplay.py           (uses vlc)

bin/aria2c             aria2c wrapper (allowing non systems port)
bin/aria2c.py          (bandwidth 512KB limit default using "trickle", "$HOME/.config/tickle.json)

bin/audacity           audacity wrapper (allowing non systems port)
bin/audacity.bat
bin/audacity.py

bin/avi                Encode AVI video using avconv (libxvid/libmp3lame)
bin/avi.py

bin/battery            Linux battery status utility
bin/battery.py

bin/bell               Play bell.ogg sound
bin/bell.ogg           (uses cvlc or ogg123)
bin/bell.py

bin/breaktimer         Break reminder timer
bin/breaktimer.py      (10 min default)

bin/bz2                Compress a file in BZIP2 format (allowing non systems port)
bin/bz2_.py

bin/calendar           Displays month or year calendar
bin/calendar.bat
bin/calendar_.py

bin/cdspeed            Set CD/DVD drive speed
bin/cdspeed.py         ("$HOME/.config/cdspeed.json")

bin/chkpath            Check PATH and return correct settings
bin/chkpath.bat
bin/chkpath.py

bin/chrome             chrome wrapper (allowing non systems port)
bin/chrome-proxy
bin/chrome-proxy.bat
bin/chrome.bat
bin/chrome.py

bin/chroot             chroot wrapper (allowing non systems port)
bin/chroot.py          (creates /shared mount automatically)

bin/clam               Run ClamAV anti-virus scanner
bin/clam.bat
bin/clam.py

bin/cluster            Run command on a subnet in parallel
bin/cluster.py

bin/cmd                wine wrapper (allowing non systems port)

bin/deb                Debian package management tools
bin/deb.py             (support offline repository searching and update checks
bin/debchkdir
bin/debchkdir.py
bin/debchkinstall
bin/debchkinstall.py
bin/debchkupdate
bin/debchkupdate.py
bin/debdistfind
bin/debdistfind.py
bin/debdistget
bin/debdistget.py
bin/debdistinfo
bin/debdistinfo.py

bin/df                 df wrapper (allowing non systems port)
bin/df.py              (KB default and fix format problems)

bin/dhcptable          Shows local DHCP hosts
bin/dhcptable.py

bin/eclipse            eclipse wrapper (allowing non systems port)
bin/eclipse.py

bin/espeak             espeak wrapper (allowing non systems port)
bin/espeak.py

bin/et                 et wrapper (allowing non systems port)
bin/et.py              (fix sound problems)

bin/evince             evince wrapper (allowing non systems port)
bin/evince.bat
bin/evince.py

bin/extfbfl            Extract Facebook friends list from saved HTML file
bin/extfbfl.bat
bin/extfbfl.py

bin/extjs              Extracts Javascript from a HTML file
bin/extjs.bat
bin/extjs.py

bin/exturl             Extracts http references from a HTML file
bin/exturl.bat
bin/exturl.py

bin/fcat               Concatenate files and print on the standard output
bin/fcat.bat           (similar to cat)
bin/fcat.py

bin/fchop              Chop up a file into chunks
bin/fchop.bat
bin/fchop.py

bin/fcount             Count number of lines and maximum columns used in file
bin/fcount.bat
bin/fcount.py

bin/fcp                Copy files and directories
bin/fcp.bat            (Preserving time stamps)
bin/fcp.py

bin/fcpall             Copy a file to multiple target files
bin/fcpall.bat
bin/fcpall.py

bin/fcplink            Replace symbolic link to files with copies
bin/fcplink.py

bin/fdiff              Show summary of differences between two directories recursively
bin/fdiff.bat
bin/fdiff.py

bin/fdu                Show file disk usage
bin/fdu.bat            (like du but same values independent of file system including Windows)
bin/fdu.py

bin/ffind              Find file or directory
bin/ffind.bat          (uses regular expression)
bin/ffind.py

bin/ffind0             Find zero sized files
bin/ffind0.bat
bin/ffind0.py

bin/ffix               Remove horrible characters in filename
bin/ffix.bat           (like spaces etc)
bin/ffix.py

bin/ffmpeg             ffmpeg wrapper (allowing non systems port)
bin/ffmpeg.py

bin/ffplay             ffplay wrapper (allowing non systems port)
bin/ffplay.py

bin/ffprobe            ffprobe wrapper (allowing non systems port)
bin/ffprobe.py

bin/fget               Download http/https/ftp/file URLs
bin/fget.bat
bin/fget.py

bin/fgrep.bat          Print lines matching a pattern
bin/fgrep.py           (Windows only)

bin/fhead              Output the first n lines of a file
bin/fhead.bat          (like head)
bin/fhead.py

bin/firefox            firefox wrapper (allowing non systems port)
bin/firefox.bat        (supports "-copy", "-no-remote" and "-reset" enhancements)
bin/firefox.py

bin/fixwav             Normalize volume of wave files (-16.0dB rms mean volume)
bin/fixwav.py          (uses normalize-audio)

bin/flashgot-term      Firefox Flashgot terminal startup script

bin/flink              Recursively link all files
bin/flink.py

bin/fls                Show full list of files
bin/fls.bat
bin/fls.py

bin/fmod               Set file access mode
bin/fmod.bat
bin/fmod.py

bin/fmv                Move or rename files
bin/fmv.bat
bin/fmv.py

bin/fopen              Open files using default application
bin/fopen.py           (hardwired application list)

bin/fpeek              Dump the first and last few bytes of a binary file
bin/fpeek.bat
bin/fpeek.py

bin/fprint             Sends text/images/postscript/PDF to printer
bin/fprint.py

bin/frm                Remove files or directories
bin/frm.bat
bin/frm.py

bin/frn                Rename file/directory by replacing some characters
bin/frn.bat
bin/frn.py

bin/fsame              Show files with same MD5 checksums
bin/fsame.bat
bin/fsame.py

bin/fsort              Unicode sort lines of a file
bin/fsort.bat
bin/fsort.py

bin/fstat              Display file status
bin/fstat.bat
bin/fstat.py

bin/fstrings           Print the strings of printable characters in files
bin/fstrings.bat       (like strings)
bin/fstrings.py

bin/fsub               Replace contents of multiple files
bin/fsub.bat           (uses regular expression to match text)
bin/fsub.py

bin/fsum               Calculate checksum using MD5, file size and file modification time
bin/fsum.bat           (can produce ".fsum" files)
bin/fsum.py

bin/ftail              Output the last n lines of a file
bin/ftail.bat          (like tail)
bin/ftail.py

bin/ftodos             Converts file to "\r\n" newline format
bin/ftodos.bat
bin/ftodos.py

bin/ftolower           Convert filename to lowercase
bin/ftolower.bat
bin/ftolower.py

bin/ftomac             Converts file to "\r" newline format
bin/ftomac.bat
bin/ftomac.py

bin/ftouch             Modify access times of all files in directory recursively
bin/ftouch.bat
bin/ftouch.py

bin/ftounix            Converts file to "\n" newline format
bin/ftounix.bat
bin/ftounix.py

bin/ftoupper           Convert filename to uppercase
bin/ftoupper.bat
bin/ftoupper.py

bin/ftp                ftp wrapper (allowing non systems port)
bin/ftp.py

bin/fwatch             Watch file system events
bin/fwatch.py          (uses inotifywait)

bin/fwhich             Locate a program file
bin/fwhich.bat
bin/fwhich.py

bin/fwrapper           Create wrapper to run script/executable
bin/fwrapper.py

bin/fzero              Zero device or create zero file
bin/fzero.bat
bin/fzero.py

bin/g++                g++ wrapper (allowing non systems port)
bin/g++.bat
bin/gxx_.py

bin/gcc                gcc wrapper (allowing non systems port)
bin/gcc.bat
bin/gcc.py

bin/gedit              gedit wrapper (allowing non systems port)
bin/gedit.py

bin/gem                Wrapper to select "umask 022"
bin/gem.py

bin/getip              Get the IP number of hosts
bin/getip.bat
bin/getip.py

bin/geturl             Multi-threaded download accelerator
bin/geturl.py          (use aria2c)

bin/gfortran           gfortran wrapper (allowing non systems port)
bin/gfortran.bat
bin/gfortran.py

bin/gimp               gimp wrapper (allowing non systems port)
bin/gimp.bat
bin/gimp.py

bin/git                git wrapper (allowing non systems port)
bin/git.bat
bin/git.py
bin/git-bash.bat       git bash shell for Windows
bin/gitk               gitk wrapper (allowing non systems port)
bin/gitk.bat
bin/gitk.py
bin/gittime            Modify file time to original GIT author time
bin/gittime.py

bin/gnomine            gnome-mines/gnomine wrapper (allowing non systems port)
bin/gnomine.py         (can pick using old gnomines name)

bin/google             Google search engine submission
bin/google.py

bin/gpg                gpg wrapper (allowing non systems port)
bin/gpg.py             (contains enhanced functions "gpg -h")

bin/gqview             gqview wrapper (allowing non systems port)
bin/gqview.bat         (uses gqview)
bin/gqview.py          (uses geeqie)

bin/graph              Generate multiple graph files with X/Y plots
bin/graph.py           (uses gnuplot)

bin/gz                 Compress a file in GZIP format (allowing non systems port)
bin/gz.py

bin/halt               Fast shutdown using "/proc/sysrq-trigger"

bin/htmlformat         HTML file re-formatter
bin/htmlformat.bat
bin/htmlformat.py

bin/httpd              Start a simple Python HTTP server
bin/httpd.bat
bin/httpd.py

bin/index              Produce "index.fsum" file and "..fsum" cache files
bin/index.bat
bin/index.py

bin/isitup             Checks whether a host is up
bin/isitup.bat
bin/isitup.py

bin/iso                Make a portable CD/DVD archive in ISO9660 format
bin/iso.py

bin/iterm              iTerm2 (allowing non systems port)
bin/iterm.py

bin/jar                jar wrapper (allowing non systems port)
bin/jar.py             (Java jar archiver)

bin/java               java wrapper (allowing non systems port)
bin/java.py            (Java run time)

bin/javac              javac wrapper (allowing non systems port)
bin/javac.py           (Java compiler)

bin/jpeg2ps            jpeg2ps wrapper (allowing non systems port)
bin/jpeg2ps.py

bin/jsformat           Javascript file re-formatter
bin/jsformat.bat
bin/jsformat.py

bin/jsonformat         JSON file re-formatter
bin/jsonformat.bat
bin/jsonformat.py

bin/jython.py

bin/keymap.tcl         TCL/TK widget for setting keymaps

bin/md5                Calculate MD5 checksums of files
bin/md5.bat
bin/md5.py

bin/md5cd              Calculate MD5 checksums for CD/DVD data disk
bin/md5cd.py

bin/menu               TCL/TK menu system
bin/menu.py            (this can be used independent of GNOME/KDE/XFCE menu system)
bin/menu_document.tcl
bin/menu_games.tcl
bin/menu_graphics.tcl
bin/menu_main.tcl
bin/menu_multimedia.tcl
bin/menu_network.tcl
bin/menu_radiotuner.tcl
bin/menu_system.tcl
bin/menu_utility.tcl

bin/mirror             Copy all files/directory inside a directory into mirror directory
bin/mirror.bat
bin/mirror.py

bin/mkcd               Make data/audio/video CD/DVD using CD/DVD writer
bin/mkcd.py            (uses wodim, icedax, cdrdao)

bin/mkpasswd           Create Create secure random password.
bin/mkpasswd.bat
bin/mkpasswd.py

bin/mksshkeys          Create SSH keys and setup access to remote systems
bin/mksshkeys.py

bin/mousepad           mousepad wrapper (allowing non systems port)
bin/mousepad.py        (XFCE editor)

bin/mp3                Encode MP3 audio using avconv (libmp3lame)
bin/mp3.py

bin/mp4                Encode MP4 video using avconv (libx264/aac)
bin/mp4.py

bin/meld               Meld wrapper (allowing non systems port)
bin/meld.bat
bin/meld.py

bin/myqdel             MyQS personal batch system for each user
bin/myqdel.py
bin/myqexec
bin/myqexec.py
bin/myqsd
bin/myqsd.py
bin/myqstat
bin/myqstat.py
bin/myqsub
bin/myqsub.py

bin/nautilus           nautilus wrapper (allowing non systems port)
bin/nautilus.py

bin/netnice            Run a command with limited network bandwidth (uses trickle)
bin/netnice.py

bin/normalize          normalize wrapper (allowing non systems port)
bin/normalize.py

bin/ntpdate            Run daemon to update time once every 24 hours
bin/ntpdate.py

bin/ocr                Convert image file to text using OCR
bin/ocr.py             (uses tesseract)

bin/ogg                Encode OGG audio using avconv (libvorbis)
bin/ogg.py

bin/pause              Pause until user presses <ENTER/RETURN> key
bin/pause.bat
bin/pause.py

bin/pbsetup            pbsetup wrapper (allowing non systems port)
bin/pbsetup.py         (Punk Buster)

bin/pcheck             Check JPEG picture files
bin/pcheck.py

bin/pcunix.bat         Start PCUNIX on Windows

bin/pdf                Create PDF file from text/images/postscript/PDF files
bin/pdf.py

bin/2to3               Python 3.x script wrappers (allowing non systems port)
bin/2to3.bat
bin/2to3-3.4
bin/2to3-3.4.bat
bin/ansible-playbook
bin/aws
bin/aws.bat
bin/aws_.py
bin/django-admin
bin/django-admin.bat
bin/django_admin_.py
bin/flask
bin/flask.bat
bin/flask_.py
bin/glances
bin/ipdb3
bin/ipdb3.bat
bin/ipython
bin/ipython.bat
bin/ipython3
bin/ipython3.4.bat
bin/pep8
bin/pep8.bat
bin/pip
bin/pip.bat
bin/pip3
bin/pip3.bat
bin/pip3.4
bin/pip3.4.bat
bin/pydoc3
bin/pydoc3.bat
bin/pydoc3.4
bin/pydoc3.4.bat
bin/pylint
bin/pylint.bat
bin/virtualenv
bin/virtualenv.bat

bin/pidgin             pidgin wrapper (allowing non systems port)
bin/pidgin.bat
bin/pidgin.py

bin/play               Play multimedia file/URL
bin/play.py            (uses vlc and ffprobe)

bin/phtml              Generate XHTML files to view pictures
bin/phtml.bat
bin/phtml.py

bin/plink              Create links to JPEG files
bin/plink.py

bin/pmeg               Resize large picture images to mega-pixels limit
bin/pmeg.py            (uses convert from ImageMagick)

bin/pnum               Renumber picture files into a numerical series
bin/pnum.bat
bin/pnum.py

bin/pop                Send popup message to display
bin/pop.jar            (uses Java)
bin/pop.py

bin/procexp            Windows procexp wrapper (allowing non systems port)
bin/procexp.bat
bin/procexp.py

bin/pyld.py            Load Python main program as module (must have Main class)
bin/test_pyld.py       Unit testing suite for "pyld.py"

bin/pyprof             Profile Python 3.x program
bin/pyprof.bat
bin/pyprof.py

bin/python             Python startup (allowing non systems port)
bin/python.bat
bin/python2
bin/python2.7
bin/python2.7.bat
bin/python2.bat
bin/python3
bin/python3.0
bin/python3.1
bin/python3.2
bin/python3.3
bin/python3.4
bin/python3.4.bat
bin/python3.5
bin/python3.bat
bin/python3.6

bin/pyuntar.py         Unpack an archive in TAR format.

bin/pyz                Make a Python3 ZIP Application in PYZ format
bin/pyz.py

bin/qmail              Qwikmail, commandline E-mailer
bin/qmail.py

bin/readcd             Copy CD/DVD data as a portable ISO/BIN image file
bin/readcd.py

bin/ripcd              Rip CD audio tracks as WAVE sound files
bin/ripcd.py

bin/ripdvd             Rip Video DVD title to file
bin/ripdvd.py

bin/rpm                rpm wrapper (allowing non systems port)
bin/rpm.py

bin/run                Run a command immune to terminal hangups
bin/run.py

bin/say                Speak words using Espeak TTS engine
bin/say.py             (uses espeak)

bin/scp.bat            Windows scp wrapper (uses PuTTY)

bin/sdd                Securely backup/restore partitions using SSH protocol
bin/sdd.py

bin/sftp.bat           Windows sftp wrapper (uses PuTTY)

bin/shuffle            Print arguments in random order
bin/shuffle.bat
bin/shuffle.py

bin/skype              skype wrapper (allowing non systems port)
bin/skype.py

bin/smount             Securely mount a file system using SSH protocol
bin/smount.py          (uses fuse.sshfs)

bin/soffice            soffice wrapper (allowing non systems port)
bin/soffice.bat        (LibreOffice)
bin/soffice.py

bin/ssh.bat            Windows ssh wrapper (uses PuTTY)

bin/ssync              Securely synchronize file system using SSH protocol
bin/ssync.py           (uses rsync)

bin/sumount            Unmount file system securely mounted with SSH protocol
bin/sumount.py

bin/svncviewer         Securely connect to VNC server using SSH protocol
bin/svncviewer.py

bin/sysinfo            System configuration detection tool
bin/sysinfo.bat
bin/sysinfo.py
bin/sysinfo.sh         Old Bourne shell version

bin/tar                tar wrapper (allowing non systems port)
bin/tar.bat            (with Python enhancements)
bin/tar.py

bin/terraform          terraform wrapper (allowing non systems port)
bin/terraform.py

bin/tbz                Make a compressed archive in TAR.BZ2
bin/tbz.bat
bin/tbz.py

bin/tgz                Make a compressed archive in TAR.GZ format
bin/tgz.bat
bin/tgz.py

bin/thunderbird        thunderbird wrapper (allowing non systems port)
bin/thunderbird.bat
bin/thunderbird.py

bin/tinyproxy          tinyproxy wrapper (allowing non systems port)
bin/tinyproxy.py

bin/tkill              Kill tasks by process ID or name
bin/tkill.bat
bin/tkill.py

bin/tls                Show full list of files
bin/tls.bat
bin/tls.py

bin/tlz                Make a compressed archive in TAR.LZMA format
bin/tlz.py

bin/tmux               tmux wrapper (allowing non systems port)
bin/tmux.py

bin/tocapital          Print arguments wth first letter in upper case
bin/tocapital.bat
bin/tocapital.py

bin/tolower            Print arguments in lower case
bin/tolower.bat
bin/tolower.py

bin/top                top wrapper (allowing non systems port)
bin/top.py

bin/toupper            Print arguments in upper case
bin/toupper.bat
bin/toupper.py

bin/traceroute         traceroute wrapper (allowing non systems port)
bin/traceroute.bat
bin/traceroute.py

bin/twait              Wait for task to finish then launch command
bin/twait.bat
bin/twait.py

bin/txz                Make a compressed archive in TAR.XZ format
bin/txz.py

bin/un7z               Unpack a compressed archive in 7Z format
bin/un7z.bat
bin/un7z.py

bin/unace              Unpack a compressed archive in ACE format
bin/unace.py

bin/unbz2              Uncompress a file in BZIP2 format (allowing non systems port)
bin/unbz2.py

bin/undeb              Unpack a compressed archive in DEB format
bin/undeb.py

bin/unetbootin         unetbootin wrapper (allowing non systems port)
bin/unetbootin.bat
bin/unetbootin.py

bin/ungpg              Unpack an encrypted archive in gpg (pgp compatible) format
bin/ungpg.py

bin/ungz               Uncompress a file in GZIP format (allowing non systems port)
bin/ungz.py

bin/uniso              Unpack a portable CD/DVD archive in ISO9660 format
bin/uniso.py

bin/unjar              Unpack a compressed JAVA archive in JAR format
bin/unjar.py

bin/unpdf              Unpack PDF file into series of JPG files
bin/unpdf.py

bin/unrar              Unpack a compressed archive in RAR format
bin/unrar.py

bin/unrpm              Unpack a compressed archive in RPM format
bin/unrpm.py

bin/unsql              Unpack a sqlite database file
bin/unsql.py

bin/untar              Unpack a compressed archive in
bin/untar.bat          TAR/TAR.GZ/TAR.BZ2/TAR.LZMA/TAR.XZ/TAR.7Z/TGZ/TBZ/TLZ/TXZ format.
bin/untar.py

bin/untbz              Unpack a compressed archive in TAR.BZ2 format
bin/untbz.bat
bin/untbz.py

bin/untgz              Unpack a compressed archive in TAR.GZ format.
bin/untgz.bat
bin/untgz.py

bin/untlz              Unpack a compressed archive in TAR.LZMA format.
bin/untlz.py

bin/untxz              Unpack a compressed archive in TAR.XZ format
bin/untxz.py

bin/unwine             Shuts down WINE and all Windows applications
bin/unwine.py

bin/ungz               Uncompress a file in XZ format (allowing non systems port)
bin/unxz.py

bin/unzip              unzip wrapper (allowing non systems port)
bin/unzip.py

bin/vbox               VirtualBox virtual machine manager
bin/vbox.py            (uses VBoxManage)

bin/vi                 vi wrapper (allowing non systems port)
bin/vi.bat
bin/vi.py

bin/vim                vim wrapper (allowing non systems port)
bin/vim.bat
bin/vim.py

bin/vlc                vlc wrapper (allowing non systems port)
bin/vlc.bat
bin/vlc.py

bin/vmware             VMware Player launcher

bin/vncpasswd          vncpasswd wrapper (allowing non systems port)
bin/vncpasswd.py

bin/vncserver          vncserver wrapper (allowing non systems port)
bin/vncserver.py

bin/vncviewer          vncviewer wrapper (allowing non systems port)
bin/vncviewer.bat
bin/vncviewer.py

bin/vplay              Play AVI/FLV/MP4 video files in directory.
bin/vplay.py           (uses vlc)

bin/wav                Encode WAV audio using avconv (pcm_s16le).
bin/wav.py

bin/wget               wget wrapper (allowing non systems port)
bin/wget.py            (bandwidth 512KB limit default using "trickle", "$HOME/.config/trickle.json)

bin/wine               wine wrapper (allowing non systems port)
bin/wine.py

bin/wipe               wipe wrapper (allowing non systems port)
bin/wipe.py            (wipe is C disk wiper)

bin/xcalc              Start GNOME/KDE/XFCE calculator
bin/xcalc.py

bin/xdesktop           Start GNOME/KDE/XFCE file manager
bin/xdesktop.py

bin/xdiff              Graphical file comparison and merge tool
bin/xdiff.bat          (uses meld)
bin/xdiff.py

bin/xedit              Start GNOME/KDE/XFCE graphical editor
bin/xedit.py

bin/xlight             Desktop screen backlight utility
bin/xlight.py

bin/xlock              Start GNOME/KDE/XFCE screen lock
bin/xlock.py

bin/xlogout            Shutdown X-windows
bin/xlogout.py

bin/xmixer             Start GNOME/KDE/XFCE audio mixer
bin/xmixer.py

bin/xmlcheck           Check XML file for errors
bin/xmlcheck.bat
bin/xmlcheck.py

bin/xmlformat          XML file re-formatter
bin/xmlformat.bat
bin/xmlformat.py

bin/xreset             Reset to default screen resolution
bin/xreset.py

bin/xrun               Run GUI software and restore resolution
bin/xrun.py

bin/xsnapshot          Start GNOME/KDE/XFCE screen snapshot
bin/xsnapshot.py

bin/xsudo              Run sudo command in new terminal session
bin/xsudo.py

bin/xterm              Start GNOME/KDE/XFCE/Invisible terminal session
bin/xterm.py

bin/xvolume            Desktop audio volume utility
bin/xvolume.py         (uses pacmd)

bin/xz                 Compress a file in XZ format (allowing non systems port)
bin/xz.py

bin/youtube            Youtube video downloader
bin/youtube.py         (uses youtube-dl)

bin/yping              Ping a host until a connection is made
bin/yping.bat
bin/yping.py

bin/zhspeak            Zhong Hua Speak, Chinese TTS software
bin/zhspeak.py
bin/zhspeak.tcl

bin/zip                zip wrapper (allowing non systems port)
bin/zip.py

bin/cda.bat            Windows command prompt batch file
bin/cdb.bat            for changing directory to %cda%..%cdz%
bin/cdc.bat
bin/cdd.bat
bin/cde.bat
bin/cdf.bat
bin/cdg.bat
bin/cdh.bat
bin/cdi.bat
bin/cdj.bat
bin/cdk.bat
bin/cdl.bat
bin/cdm.bat
bin/cdn.bat
bin/cdo.bat
bin/cdp.bat
bin/cdq.bat
bin/cdr.bat
bin/cds.bat
bin/cdt.bat
bin/cdu.bat
bin/cdv.bat
bin/cdw.bat
bin/cdx.bat
bin/cdy.bat
bin/cdz.bat
bin/mka.bat            Windows command prompt batch file
bin/mkb.bat            for setting %cda%..%cdz% to current working driectory
bin/mkc.bat
bin/mkd.bat
bin/mke.bat
bin/mkf.bat
bin/mkg.bat
bin/mkh.bat
bin/mki.bat
bin/mkj.bat
bin/mkk.bat
bin/mkl.bat
bin/mkm.bat
bin/mkn.bat
bin/mko.bat
bin/mkp.bat
bin/mkq.bat
bin/mkr.bat
bin/mks.bat
bin/mkt.bat
bin/mku.bat
bin/mkv.bat
bin/mkw.bat
bin/mkx.bat
bin/mky.bat
bin/mkz.bat
bin/scd.bat
bin/mka.bat            Show settings of %cda%..%cdz% environmental variables

config/Xresources               Copy to "$HOME/.Xresources" to set xterm resources
config/autoexec.sh              Copy to "$HOME/.config/autoexec.sh" & add to desktop auto startup
config/autoexec-local.sh        Copy to "$HOME/.config/autoexec-local.sh" for local settings
config/bashrc                   Copy to "/root/.bashrc" for "root" account settings
config/config                   Copy to "$HOME/.ssh/config"
config/docker-init              Docker init script
config/docker-init-home         Docker init script plugin for fixing $HOME directory
config/docker-init-resolvconf   Docker init script plugin for fixing "resolvconf"
config/gitconfig                Copy to "$HOME/.gitconfig" and edit
config/gqview-userapp.desktop   Copy to "$HOME/.local/share/applications" for Geeqie
config/login                    Copy to "$HOME/.login" for csh/tcsh shells (translated ".profile")
config/mimeapps.list            Copy to "$HOME/.local/share/applications" for Mime definitions
config/minttyrc                 Copy to "$HOME/.minttyrc" for MSYS2 terminal
config/tmux.conf                Copy to "$HOME/.tmux.conf" fro TMUX terminal
config/offline                  Wrapper script to run any command in off line mode (read comments)
config/profile                  Copy to "$HOME/.profile" for ksh/bash shells
config/profile-local            Copy to "$HOME/.profile-local" for ksh/bash shells
config/rc.local                 Copy to "/etc/rc.local" for auto running commands
config/rc.mount                 Copy to "/etc/rc.mount" for mounting removable disks
config/soffice-userapp.desktop  Copy to "$HOME/.local/share/applications" for LibreOffice
config/terminalrc               Copy to "$HOME/.config/xfce4/terminal" for XFCE terminal
config/vimrc                    Copy to "$HOME/.vimrc" for VIM defaults
config/com.googlecode.iterm2.plist Copy to "$HOME/Library/Preference" for iTerm2 on Mac
config/xscreensaver             Copy to "$HOME/.xscreensaver" for XScreenSaver defaults

etc/setbin                Hybrid Bourne/C-shell script for sh/ksh/bash/csh/tcsh initialization
etc/setbin.bat            Windows Command prompt initialization
etc/setbin.ps1            Windows Power shell initialization
etc/python3-requirements  Python requirements "python3 -m pip install -r requirements.txt"

examples/cloudformation/1pxy/1pxy.json                CloudFormation: 1pxy example
examples/cloudformation/1pxy/Makefile
examples/cloudformation/1pxy/submit.sh

examples/cloudformation/multi-stacks/Makefile         CloudFormation: multi-stacks example
examples/cloudformation/multi-stacks/main_stack.json
examples/cloudformation/multi-stacks/pxy_stack.json
examples/cloudformation/multi-stacks/sg_stack.json
examples/cloudformation/multi-stacks/submit.sh

examples/docker/centos/Dockerfile                     CentOS docker image
examples/docker/centos/Makefile
examples/docker/debian/Dockerfile                     Debian docker image
examples/docker/debian/Makefile
examples/docker/debian-openvpn/Dockerfile             Debian OpenVPN docker image
examples/docker/debian-openvpn/Makefile
examples/docker/ubuntu/Dockerfile                     Ubuntu docker image
examples/docker/ubuntu/Makefile

examples/kubernetes/debian-lxc/Makefile               Kubernetes example
examples/kubernetes/debina-lxc/test-ns.json
examples/kubernetes/debian-lxc/debian-pod.json
examples/kubernetes/debian-lxc/debian-rc.json
examples/kubernetes/debian-lxc/debian-svc.json

examples/python/simple-package/Makefile               Simple Egg & WHL package
examples/python/simple-package/RUN
examples/python/simple-package/setup.py
examples/python/simple-package/hello/__init__.py
examples/python/simple-pakcage/hello/message.py
examples/python/simple-flask/Makefile                 Simple Flask demo
examples/python/simple-flask/RUN
examples/python/simple-flask/simple_flask.py
examples/python/simple-flask/templates/hello.html
examples/python/simple-tornado/tornado_client.py      Tornado web client example
examples/python/simple-tornado/tornado_server.py      Tornado web server example

examples/terraform-aws/1pxy/aws_config.tf             Terraform AWS: 1pxy example
examples/terraform-aws/1pxy/aws_resources.tf
examples/terraform-aws/1pxy/pxy_resources.tf
examples/terraform-aws/1pxy/pxy_variables.tf
examples/terraform-aws/pxy-as/aws_config.tf           Terraform AWS: pxy-as example
examples/terraform-aws/pxy-as/aws_resources.tf
examples/terraform-aws/pxy-as/pxy_resources.tf
examples/terraform-aws/pxy-as/pxy_variables.tf

