1996-2015 By Dr Colin Kong

These are production scripts and configuration files that I use and share. Originally the scripts
were started Bourne shell scripts started during my University days and continuously enhanced over
the years. Now most of the scripts are written in Python 3.

etc/setbin       Hybrid Bourne/C-shell script for sh/ksh/bash/csh/tcsh initialization
etc/setbin.bat   Windows Command prompt initialization
etc/setbin.ps1   Windows Power shell initialization

config/Xresources               Copy to "$HOME/.Xresources" to set xterm resources
config/autoexec.sh              Copy to "$HOME/.config/autoexec.sh" & add to desktop auto startup
config/autoexec-local.sh        Copy to "$HOME/.config/autoexec-local.sh" for local settings
config/gqview-userapp.desktop   Copy to "$HOME/.local/share/applications" for Geeqie
config/login                    Copy to "$HOME/.login" for csh/tcsh shells (translated ".profile")
config/mimeapps.list            Copy to "$HOME/.local/share/applications" for Mime definitions
config/profile                  Copy to "$HOME/.profile" for ksh/bash shells (translated ".login")
config/rc.local                 Copy to "/etc/rc.local" for Ubuntu & Debian VMs
config/soffice-userapp.desktop  Copy to "$HOME/.local/share/applications" for LibreOffice

bin/7z                 Make a compressed archive in 7z format
bin/7z.bat             (uses p7zip or 7zip)
bin/7z.py
bin/7za
bin/7za.py

bin/acroread           acroread wrapper (allowing non systems port)
bin/acroread.py

bin/aftp               Automatic connection to FTP server anonymously
bin/aftp.py

bin/alarmclock         alarmclock wrapper (allowing non systems port)
bin/alarmclock.py

bin/aplay              Play MP3/OGG/WAV audio files in directory

bin/aplay.py           (uses vlc)

bin/aria2c             aria2c wrapper (allowing non systems port)
bin/aria2c.py          (bandwidth 512KB limit default using "trickle", "$HOME/.config/trickle.json)

bin/audacity           audacity wrapper (allowing non systems port)
bin/audacity.bat
bin/audacity.py

bin/avconv             avconv wrapper (allowing non systems port)
bin/avconv.py

bin/avi                Encode AVI video using avconv (libxvid/libmp3lame)
bin/avi.py

bin/avplay             avplay wrapper (allowing non systems port)
bin/avplay.py

bin/avprobe            avprobe wrapper (allowing non systems port)
bin/avprobe.py

bin/battery            Linux battery status utility
bin/battery.py

bin/bell               Play bell.ogg sound
bin/bell.ogg           (uses cvlc or ogg123)
bin/bell.py

bin/breaktimer         Break reminder timer
bin/breaktimer.py      (10 min default)

bin/bz2                Compress a file in BZIP2 format
bin/bz2.py

bin/cal                Displays month or year calendar
bin/cal.bat
bin/cal.py
bin/calendar           Print large monthly calendar
bin/calendar.bat
bin/calendar.py

bin/cdinst.bat         Windows command prompt batch file to "cd %INSTDIR%"

bin/cdspeed            Set CD/DVD drive speed
bin/cdspeed.py         ("$HOME/.config/cdspeed.xml)

bin/cdsrc.bat          Windows command prompt batch file to "cd %SRCDIR%"
bin/cdtest.bat         Windows command prompt batch file to "cd %TESTDIR%"

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

bin/cpuz               Windows "cpuz_x32.exe" wrapper (allowing non systems port)
bin/cpuz.bat
bin/cpuz.py

bin/deb                Debian package management tools
bin/deb-chkdir         (support offline repository searching and update checks)
bin/deb-chkdir.py
bin/deb-chkinstall
bin/deb-chkinstall.py
bin/deb-chkupdate
bin/deb-chkupdate.py
bin/deb-distfind
bin/deb-distfind.py
bin/deb-distget
bin/deb-distget.py
bin/deb-distinfo
bin/deb-distinfo.py
bin/deb.py

bin/df                 df wrapper (allowing non systems port)
bin/df.py              (KB default and fix format problems)

bin/dhcptable          Shows local DHCP hosts
bin/dhcptable.py

bin/dsmj               dsmj wrapper (allowing non systems port)
bin/dsmj.py            (IBM backup/restore tool)

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

bin/fedit              Edit multiple files
bin/fedit.py           (uses vim)

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

bin/fixwav             Normalize volume of wave files to 8 dB
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

bin/fspell             Check spelling of file
bin/fspell.py          (uses aspell)

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

bin/fzero              Zero device or create zero file
bin/fzero.bat
bin/fzero.py

bin/g++                g++ wrapper (allowing non systems port)
bin/g++.bat
bin/g++.py

bin/gcc                gcc wrapper (allowing non systems port)
bin/gcc.bat
bin/gcc.py

bin/gedit              gedit wrapper (allowing non systems port)
bin/gedit.py

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

bin/gnome-mines        gnome-mines wrapper (allowing non systems port)
bin/gnome-mines.py     (can pick using old gnomines name)

bin/gpg                gpg wrapper (allowing non systems port)
bin/gpg.py             (contains enhanced functions "gpg -h")

bin/gqview             gqview wrapper (allowing non systems port)
bin/gqview.bat         (uses gqview)
bin/gqview.py          (uses geeqie)

bin/graph              Generate multiple graph files with X/Y plots
bin/graph.py           (uses gnuplot)

bin/gz                 Compress a file in GZIP format
bin/gz.py

bin/halt               Fast shutdown using "/proc/sysrq-trigger"

bin/httpd              Start a simple Python HTTP server
bin/httpd.bat
bin/httpd.py

bin/index              Produce "index.fsum" file and "..fsum" cache files
bin/index.bat
bin/index.py

bin/inkscape           inkscape wrapper (allowing non systems port)
bin/inkscape.bat
bin/inkscape.py

bin/irecorder          irecorder wrapper (allowing non systems port)
bin/irecorder.bat      (Windows CD/DVD burner tool)
bin/irecorder.py

bin/isitup             Checks whether a host is up
bin/isitup.bat
bin/isitup.py

bin/iso                Make a portable CD/DVD archive in ISO9660 format
bin/iso.py

bin/iview              iview wrapper (allowing non systems port)
bin/iview.bat          (Windows IrfanView iamge viewer)
bin/iview.py

bin/jar                jar wrapper (allowing non systems port)
bin/jar.py             (Java jar archiver)

bin/java               java wrapper (allowing non systems port)
bin/java.py            (Java run time)

bin/javac              javac wrapper (allowing non systems port)
bin/javac.py           (Java compiler)

bin/juniper            Connect to Juniper Network Connect VPN
bin/juniper.py

bin/jython             jython wrapper (allowing non systems port)
bin/jython.py

bin/keymap.tcl         TCL/TK widget for setting keymaps

bin/malias             Look up mail aliases in ".mailrc" file
bin/malias.py

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
bin/menu_linux.tcl
bin/menu_main.tcl
bin/menu_multimedia.tcl
bin/menu_network.tcl
bin/menu_radiotuner.tcl
bin/menu_system.tcl
bin/menu_utility.tcl
bin/menu_windows.tcl

bin/mirror             Copy all files/directory inside a directory into mirror directory
bin/mirror.bat
bin/mirror.py

bin/mkcd               Make data/audio/video CD/DVD using CD/DVD writer
bin/mkcd.py            (uses wodim, icedax, cdrdao)

bin/mkinst.bat         Windows command prompt batch file set %INSTDIR%

bin/mksrc.bat          Windows command prompt batch file set %SRCDIR%

bin/mksshkeys          Create SSH keys and setup access to remote systems
bin/mksshkeys.py

bin/mktest.bat         Windows command prompt batch file set %TESTDIR%

bin/mock_pyld.py       Unit testing mocking for pyld.py

bin/mousepad           mousepad wrapper (allowing non systems port)
bin/mousepad.py        (XFCE editor)

bin/mp3                Encode MP3 audio using avconv (libmp3lame)
bin/mp3.py

bin/mp4                Encode MP4 video using avconv (libx264/aac)
bin/mp4.py

bin/mpg                Encode MPEG video using avconv (mpeg2/ac3)
bin/mpg.py

bin/mplayer            mplayer wrapper (allowing non systems port)
bin/mplayer.py

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

bin/nhs                nhs wrapper (allowing non systems port)
bin/nhs.py

bin/normalize          normalize wrapper (allowing non systems port)
bin/normalize.py

bin/ntpdate            Run daemon to update time once every 24 hours
bin/ntpdate.py

bin/ocr                Convert image file to text using OCR
bin/ocr.py             (uses tesseract)

bin/ogg                Encode OGG audio using avconv (libvorbis)
bin/ogg.py

bin/onall              onall wrapper (allowing non systems port)
bin/onall.py

bin/open               Open files using default application
bin/open.py            (hardwired application list)

bin/patchlib.py        Unit testing patching library

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

bin/pep8               pep8 wrapper (allowing non systems port)
bin/pep8.bat
bin/pep8.py

bin/pframe             Resize/rotate picture images to fit digital photo frames
bin/pframe.py

bin/pidgin             pidgin wrapper (allowing non systems port)
bin/pidgin.bat
bin/pidgin.py

bin/pip                Wrapper to select "umask 022"
bin/pip.py
bin/pip3
bin/pip3.py

bin/play               Play multimedia file/URL
bin/play.py            (uses vlc and avprobe)

bin/phtml              Generate XHTML files to view pictures
bin/phtml.bat
bin/phtml.py

bin/plink              Create links to JPEG files
bin/plink.py
g
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

bin/pyc                Check and compile Python 3.x modules to ".pyc" byte code
bin/pyc.bat
bin/pyc.py

bin/pyld.py            Load Python main program as module (must have Main class)

bin/pyprof             Profile Python 3.x program
bin/pyprof.bat
bin/pyprof.py

bin/pytest             Run Python unittests in module files
bin/pytest.bat
bin/pytest.py

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
bin/python3.bat

bin/pyuntar.py         Unpack an archive in TAR format.

bin/pyz                Make a Python3 ZIP Application in PYZ format
bin/pyz.py

bin/qmail              Qwikmail, commandline E-mailer
bin/qmail.py

bin/readcd             Copy CD/DVD data as a portable ISO/BIN image file
bin/readcd.py

bin/renwin             Rename window title
bin/renwin.py

bin/ripcd              Rip CD audio tracks as WAVE sound files
bin/ripcd.py

bin/ripdvd             Rip Video DVD title to file
bin/ripdvd.py

bin/rpm                rpm wrapper (allowing non systems port)
bin/rpm.py

bin/run                Run a command immune to terminal hangups
bin/run.py

bin/runxpcs            Run XPCS phone system
bin/runxpcs.py

bin/say                Speak words using Espeak TTS engine
bin/say.py             (uses espeak)

bin/scp.bat            Windows scp wrapper (uses PuTTY)

bin/sdd                Securely backup/restore partitions using SSH protocol
bin/sdd.py

bin/setproxy           Determine proxy server address
bin/setproxy.py

bin/sftp.bat           Windows sftp wrapper (uses PuTTY)

bin/shuffle            Print arguments in random order
bin/shuffle.bat
bin/shuffle.py

bin/skype              skype wrapper (allowing non systems port)
bin/skype.py

bin/smount             Securely mount a file system using SSH protocol
bin/smount.py          (uses fuse.sshfs)

bin/smplayer           smplayer wrapper (allowing non systems port)
bin/smplayer.py

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

bin/syslib.py          Python system interaction Library (Python 3)
bin/syslib2.py         Python system interaction Library (Python 2.7 & 3)

bin/tar                tar wrapper (allowing non systems port)
bin/tar.bat            (with Python enhancements)
bin/tar.py

bin/tbz                Make a compressed archive in TAR.BZ2 format
bin/tbz.bat
bin/tbz.py

bin/test_pyld.py       Unit testing suite for "pyld.py"

bin/testdisk           testdisk wrapper (allowing non systems port)
bin/testdisk.py

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

bin/tocapital          Print arguments wth first letter in upper case
bin/tocapital.bat
bin/tocapital.py

bin/tolower            Print arguments wth first letter in upper case
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

bin/unbz2              Uncompress a file in BZIP2 format
bin/unbz2.py

bin/undeb              Unpack a compressed archive in DEB format
bin/undeb.py

bin/unetbootin         unetbootin wrapper (allowing non systems port)
bin/unetbootin.bat
bin/unetbootin.py

bin/ungpg              Unpack an encrypted archive in gpg (pgp compatible) format
bin/ungpg.py

bin/ungz               Unpack an encrypted archive in gpg (pgp compatible) format
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

bin/unzip              unzip wrapper (allowing non systems port)
bin/unzip.py

bin/vbox               VirtualBox virtual machine manager
bin/vbox.py            (uses VBoxManage)

bin/vi                 vi  wrapper (allowing non systems port)
bin/vi.bat
bin/vi.py

bin/vim                vim wrapper (allowing non systems port)
bin/vim.py

bin/vinagre            vinagre wrapper (allowing non systems port)
bin/vinagre.py

bin/vlc                vlc wrapper (allowing non systems port)
bin/vlc.bat
bin/vlc.py

bin/vmware             VMware Player launcher
bin/vmware.py          (uses vmplayer)

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
bin/wget.py

bin/wine               wine wrapper (allowing non systems port)
bin/wine.py

bin/wipe               wipe wrapper (allowing non systems port)
bin/wipe.py            (wipe is C disk wiper)

bin/xcalc              Start GNOME/KDE/XFCE calculator
bin/xcalc.py

bin/xdesktop           Start GNOME/KDE/XFCE file manager
bin/xdesktop.py

bin/xdiff              Graphical file comparison and merge tool
bin/xdiff.py           (uses meld)

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
