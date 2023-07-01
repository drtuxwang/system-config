# 1996-2023 By Dr Colin Kong

These are production scripts and configuration files that I use and share. Originally the scripts
were started Bourne shell scripts started during my University days and continuously enhanced over
the years.

---
```
 * Jenkinsfile              Jenkins pipeline configuration file
 * codefresh.yaml           Codefresh pipeline configuration file
 * Makefile                 Makefile for testing
 * .pylintrc                Python Pylint configuration file
 * bin/command_mod.py       Python command line handling module
 * bin/test_command_mod.py  Unit testing suite for "command_mod.py"
 * bin/config_mod.py        Python config module for handling "config_mod.yaml)
 * bin/config_mod.yaml      Configuration file apps, bindings & parameters
 * bin/debug_mod.py         Python debugging tools module
 * bin/desktop_mod.py       Python X-windows desktop module
 * bin/file_mod.py          Python file handling utility module
 * bin/logging_mod.py       Python logging handling module
 * bin/network_mod.py       Python network handling utility module
 * bin/power_mod.py         Python power handling module
 * bin/subtask_mod.py       Python sub task handling module
 * bin/task_mod.py          Python task handling utility module
 * bin/python               Python startup wrapper
 * bin/python.bat
 * bin/python2
 * bin/python2.bat
 * bin/python2.7
 * bin/python2.7.bat
 * bin/python3
 * bin/python3.bat
 * bin/python3.5
 * bin/python3.6
 * bin/python3.7
 * bin/python3.8
 * bin/python3.9
 * bin/python3.10
 * bin/python3.10.bat
 * bin/python3.11
 * bin/2to3                 Python 3.x script wrappers
 * bin/2to3.bat
 * bin/ansible
 * bin/ansible-galaxy
 * bin/ansible-inventory
 * bin/ansible-playbook
 * bin/ansible-vault
 * bin/ansible-venv
 * bin/appimage-builder
 * bin/appimage-builder-venv
 * bin/aws
 * bin/aws-venv
 * bin/awscli-venv
 * bin/cookiecutter
 * bin/cookiecutter.bat
 * bin/cqlsh
 * bin/cqlsh-venv
 * bin/cython
 * bin/cython.bat
 * bin/cythonize
 * bin/cythonize.bat
 * bin/devpi
 * bin/devpi.bat
 * bin/devpi-venv
 * bin/devpi-client-venv
 * bin/django-admin
 * bin/django-admin.bat
 * bin/django-admin-venv
 * bin/django-venv
 * bin/docker-compose
 * bin/docker-compose-venv
 * bin/flask
 * bin/flask.bat
 * bin/flask-venv
 * bin/glances
 * bin/glances-venv
 * bin/gtts-cli
 * bin/imagehash-venv
 * bin/ipdb3
 * bin/ipdb3.bat
 * bin/ipython
 * bin/ipython.bat
 * bin/ipython3
 * bin/ipython3.bat
 * bin/jinja2
 * bin/markdown2
 * bin/markdown2.bat
 * bin/mypy
 * bin/mypy.bat
 * bin/nexus3
 * bin/nexus3-venv
 * bin/nexus3-cli-venv
 * bin/pip
 * bin/pip.bat
 * bin/pip3
 * bin/pip3.bat
 * bin/poetry
 * bin/poetry-venv
 * bin/pycodestyle
 * bin/pycodestyle.bat
 * bin/pydisasm
 * bin/pydisasm-venv
 * bin/pydoc
 * bin/pydoc3
 * bin/pydoc3.bat
 * bin/pyflakes
 * bin/pyflakes.bat
 * bin/pylint
 * bin/pylint.bat
 * bin/virtualenv
 * bin/virtualenv.bat
 * bin/yt-dlp
 * bin/yt-dlp.bat
 * bin/yt-dlp-venv
 * bin/xdis-venv
 * bin/0ad                  Sandbox for "0ad" launcher
 * bin/_0ad.py
 * bin/7z                   Make a compressed archive in 7z format
 * bin/7z.bat               (uses p7zip)
 * bin/_7z.py
 * bin/aftp                 Automatic connection to FTP server anonymously
 * bin/aftp.py
 * bin/aplay                Play MP3/OGG/WAV audio files in directory
 * bin/aplay.py             (uses vlc)
 * bin/appimagetoo          Sandbox for "appimagetool" launcher
 * bin/appimagetool.py
 * bin/aria2c               Wrapper for "aria2c" command
 * bin/aria2c.py            (bandwidth 512KB limit default using "trickle", "$HOME/.config/tickle.json)
 * bin/asmc                 Wrapper for "asmc" command
 * bin/audacity             Sandbox for "audacity" launcher
 * bin/audacity.py
 * bin/avi                  Encode AVI video using avconv (libxvid/libmp3lame)
 * bin/avi.py
 * bin/battery              Monitor laptop battery
 * bin/battery.py
 * bin/bell                 Play bell.ogg sound
 * bin/bell.ogg             (uses cvlc or ogg123)
 * bin/bell.py
 * bin/bson                 Convert BSON/JSON/XML/YAML to BSON
 * bin/bson.bat
 * bin/bson_.py
 * bin/breaktimer           Break reminder timer
 * bin/breaktimer.py        (10 min default)
 * bin/busybox.bat
 * bin/bz2                  Compress a file in BZIP2 format
 * bin/bz2_.py
 * bin/cal                  Wrapper for "cal" command
 * bin/cal.py
 * bin/calendar             Displays month or year calendar
 * bin/calendar.bat
 * bin/calendar_.py
 * bin/cdspeed              Set CD/DVD drive speed
 * bin/cdspeed.py           ("$HOME/.config/cdspeed.json")
 * bin/chkconfig            Check BSON/JSON/YAML configuration files for errors
 * bin/chkconfig.bat
 * bin/chkconfig.py
 * bin/chkpath              Check PATH and return correct settings
 * bin/chkpath.bat
 * bin/chkpath.py
 * bin/chksequence          Check for missing sequence in numbered files
 * bin/chksequence.bat
 * bin/chksequence.py
 * bin/chkxml               Check XML file for errors
 * bin/chkxml.bat
 * bin/chkxml.py
 * bin/chrome               Wrapper for "google-chrome" command
 * bin/chrome.bat
 * bin/chrome.py
 * bin/chromium             Wrapper for "chromium" command
 * bin/chromium.bat
 * bin/chromium.py
 * bin/chroot               Wrapper for "chroot" command
 * bin/chroot.py            (creates /shared mount automatically)
 * bin/clam                 Run ClamAV anti-virus scanner
 * bin/clam.bat
 * bin/clam.py
 * bin/cluster              Run command on a subnet in parallel
 * bin/cluster.py
 * bin/countdown            Count down alarm after delay or specific time
 * bin/countdown.py
 * bin/deb                  Debian package management tools
 * bin/deb.py               (support offline repository searching and update checks
 * bin/debcheck
 * bin/debcheck.py
 * bin/debget
 * bin/debget.py
 * bin/debgrep
 * bin/debgrep.py
 * bin/debinstall
 * bin/debinstall.py
 * bin/debupdate
 * bin/debupdate.py
 * bin/dep                  Wrapper for "dep" Golang command
 * bin/dockerreg            Docker Registry tool
 * bin/dockerreg.bat
 * bin/dockerreg.py
 * bin/docker-sandbox       Starts Docker sandbox environment
 * bin/docker-sudo          Starts Docker sudo app
 * bin/dpkg                 Wrapper for "dpkg" command (force system Python)
 * bin/dpkg.py
 * bin/dropbox              Dropbox file sharing client.
 * bin/dropbox_.py
 * bin/eclipse              Wrapper for 'eclipse' command
 * bin/eclipse.py
 * bin/edge                 Wrapper for "microsoft-edge" command
 * bin/edge.py
 * bin/egrep                Wrapper to avoid GNU egrep usage
 * bin/espeak               Wrapper for "espeak espeak
 * bin/espeak.py
 * bin/et                   Sandbox for ET Wolf launcher
 * bin/et.py
 * bin/et.tcl
 * bin/etl                  ET Legacy game launcher
 * bin/etl.py
 * bin/evince               Sandbox for "atril/evince" launcher
 * bin/evince.py
 * bin/extjs                Extracts Javascript from a HTML file
 * bin/extjs.bat
 * bin/extjs.py
 * bin/exturl               Extracts http references from a HTML file
 * bin/exturl.bat
 * bin/exturl.py
 * bin/f7z                  Compress a file in 7ZIP format
 * bin/f7z.7z
 * bin/fcat                 Concatenate files and print on the standard output
 * bin/fcat.bat             (similar to cat)
 * bin/fcat.py
 * bin/fchop                Chop up a file into chunks
 * bin/fchop.bat
 * bin/fchop.py
 * bin/fcount               Count number of lines and maximum columns used in file
 * bin/fcount.bat
 * bin/fcount.py
 * bin/fcp                  Copy files and directories (preserving time stamps)
 * bin/fcp.bat
 * bin/fcp.py
 * bin/fcpall               Copy a file to multiple target files
 * bin/fcpall.bat
 * bin/fcpall.py
 * bin/fcplink              Replace symbolic link to files with copies
 * bin/fcplink.py
 * bin/fdiff                Show summary of differences between two directories recursively
 * bin/fdiff.bat
 * bin/fdiff.py
 * bin/fdu                  Show file disk usage
 * bin/fdu.bat              (like du but same values independent of file system including Windows)
 * bin/fdu.py
 * bin/ffile                Determine file type
 * bin/ffile.bat
 * bin/ffile.py
 * bin/ffind                Find file or directory (uses regular expression)
 * bin/ffind.bat
 * bin/ffind.py
 * bin/ffind0               Find zero sized files
 * bin/ffind0.bat
 * bin/ffind0.py
 * bin/ffix                 Remove horrible characters in filename
 * bin/ffix.bat             (like spaces etc)
 * bin/ffix.py
 * bin/ffmpeg               Wrapper for "ffmpeg" command
 * bin/ffplay               Wrapper for "ffplay" command
 * bin/ffprobe              Wrapper for "ffprobe" command
 * bin/fget                 Download http/https/ftp/file URLs
 * bin/fget.bat
 * bin/fget.py
 * bin/fgrep.bat            Print lines matching a pattern
 * bin/fgrep.py             (Windows only)
 * bin/fhead                Output the first n lines of a file
 * bin/fhead.bat            (like head)
 * bin/fhead.py
 * bin/file-roller          Wrapper for "engrampa/file-roller" command
 * bin/file_roller_.py
 * bin/firefox              Wrapper for "firefox" command
 * bin/firefox.bat          (supports "-copy", "-no-remote" and "-reset" enhancements)
 * bin/firefox.py
 * bin/fixwav               Normalize volume of wave files (-16.0dB rms mean volume)
 * bin/fixwav.py
 * bin/flink                Recursively link all files
 * bin/flink.py
 * bin/fls                  Show full list of files
 * bin/fls.bat
 * bin/fls.py
 * bin/fmkdir               Create a single lower case directory
 * bin/fmkdir.bat
 * bin/fmkdir.py
 * bin/fmod                 Set file access mode
 * bin/fmod.bat
 * bin/fmod.py
 * bin/fmv                  Move or rename files
 * bin/fmv.bat
 * bin/fmv.py
 * bin/fpar2                Calculate PAR2 parity checksum and repair tool.
 * bin/fpar2.bat
 * bin/fpar2.py
 * bin/fpeek                Dump the first and last few bytes of a binary file
 * bin/fpeek.bat
 * bin/fpeek.py
 * bin/fprint               Sends text/images/postscript/PDF to printer
 * bin/fprint.py
 * bin/frm                  Remove files or directories
 * bin/frm.bat
 * bin/frm.py
 * bin/frn                  Rename file/directory by replacing some characters
 * bin/frn.bat
 * bin/frn.py
 * bin/fsame                Show files with same MD5 checksums
 * bin/fsame.bat
 * bin/fsame.py
 * bin/fsort                Unicode sort lines of a file
 * bin/fsort.bat
 * bin/fsort.py
 * bin/fstat                Display file status
 * bin/fstat.bat
 * bin/fstat.py
 * bin/fstrings             Print the strings of printable characters in files
 * bin/fstrings.bat         (like strings)
 * bin/fstrings.py
 * bin/fsub                 Substitute patterns on lines in files
 * bin/fsub.bat             (uses regular expression to match text)
 * bin/fsub.py
 * bin/fsum                 Calculate checksum using MD5, file size and file modification time
 * bin/fsum.bat             (can produce ".fsum" files)
 * bin/fsum.py
 * bin/ftail                Output the last n lines of a file
 * bin/ftail.bat            (like tail)
 * bin/ftail.py
 * bin/ftodos               Converts file to "\r\n" newline format
 * bin/ftodos.bat
 * bin/ftodos.py
 * bin/ftolower             Convert filename to lowercase
 * bin/ftolower.bat
 * bin/ftolower.py
 * bin/ftomac               Converts file to "\r" newline format
 * bin/ftomac.bat
 * bin/ftomac.py
 * bin/ftouch               Modify access times of all files in directory recursively
 * bin/ftouch.bat
 * bin/ftouch.py
 * bin/ftounix              Converts file to "\n" newline format
 * bin/ftounix.bat
 * bin/ftounix.py
 * bin/ftoupper             Convert filename to uppercase
 * bin/ftoupper.bat
 * bin/ftoupper.py
 * bin/ftp                  Wrapper for "ftp" command
 * bin/ftp.py
 * bin/fwatch               Watch file system events
 * bin/fwatch.py            (uses inotifywait)
 * bin/fwhich               Locate a program file
 * bin/fwhich.bat
 * bin/fwhich.py
 * bin/fwrapper             Create wrapper to run script/executable
 * bin/fwrapper.py
 * bin/fzero                Zero device or create zero file
 * bin/fzero.bat
 * bin/fzero.py
 * bin/gcc                  Wrapper for "gcc" command
 * bin/gcc.bat
 * bin/g++                  Wrapper for "g++" command
 * bin/g++.bat
 * bin/gfortran             Wrapper for "gfortran" command
 * bin/gfortran.bat
 * bin/gedit                Wrapper for "gedit" command
 * bin/gedit.py
 * bin/gem                  Wrapper for "gem" Ruby command
 * bin/getip                Get the IP number of hosts
 * bin/getip.bat
 * bin/getip.py
 * bin/geturl               Multi-threaded download accelerator
 * bin/geturl.py            (use aria2c)
 * bin/gimp                 Sandbox for "gimp" launcher
 * bin/gimp.bat
 * bin/gimp.py
 * bin/git                  Wrapper for "git" command
 * bin/git.bat
 * bin/git_.py
 * bin/git-bash.bat         git bash shell for Windows
 * bin/gitk                 Wrapper for "gitk" commamd
 * bin/gitk.bat
 * bin/gitk.py
 * bin/git-lfs              git large file storage plugin
 * bin/git_lfs_.py
 * bin/git-time             git original author time plugin
 * bin/git_time_.py
 * bin/scalar
 * bin/scalar.py
 * bin/gnomine              Wrapper for "gnome-mines" command
 * bin/gnomine.py           (can pick using old gnomines name)
 * bin/go                   Go wrapper (golang)
 * bin/go.py
 * bin/gparted              Wrapper for "gparted" command
 * bin/gparted.py
 * bin/gpg                  Make an encrypted archive in gpg (pgp compatible) format.
 * bin/gpg.py
 * bin/gqview               Wrapper for "geeqie" command
 * bin/gqview.py
 * bin/graph                Generate multiple graph files with X/Y plots (uses gnuplot)
 * bin/gqview               Wrapper for "geeqie" command
 * bin/gqview.bat
 * bin/graph.py
 * bin/grpcurl              Wrapper for "grpcurl" command
 * bin/grpcurl.py
 * bin/gz                   Compress a file in GZIP format
 * bin/gz.py
 * bin/halt                 Fast shutdown using "poweroff" and "/proc/sysrq-trigger"
 * bin/hardinfo             Wrapper for "hardinfo" command
 * bin/hardinfo.py
 * bin/hearts               Sandbox for "hearts" launcher
 * bin/hearts.py
 * bin/helm                 helm wrapper (for Kubernetes)
 * bin/helm.py
 * bin/htmlformat           Re-format XHTML file.
 * bin/htmlformat.bat
 * bin/htmlformat.py
 * bin/httpd                Sandbox a simple Python HTTP server
 * bin/httpd.bat
 * bin/httpd.py
 * bin/index                Produce "index.fsum" file and "..fsum" cache files
 * bin/index.bat
 * bin/index.py
 * bin/inkscape             Sandbox for "inkscape" launcher
 * bin/inkscape.py
 * bin/isitup               Checks whether a host is up
 * bin/isitup.bat
 * bin/isitup.py
 * bin/iso                  Make a portable CD/DVD archive in ISO9660 format
 * bin/iso.py
 * bin/iterm                Wrapper for "iterm" Mac command
 * bin/jar                  JAVA jar tool launcher
 * bin/jar.py
 * bin/java                 JAVA launcher
 * bin/java.py
 * bin/javac                Wrapper for "javac" command
 * bin/jsformat             Javascript file re-formatter
 * bin/jsformat.bat
 * bin/jsformat.py
 * bin/json                 Convert BSON/JSON/YAML to JSON
 * bin/json.bat
 * bin/json_.py
 * bin/jsonformat           Re-format JSON file.
 * bin/jsonformat.bat
 * bin/jsonformat.py
 * bin/jython               Wrapper for "jython" command
 * bin/k3s                  Wrapper for "k3s" command
 * bin/k3s-server
 * bin/keymap.tcl           TCL/TK widget for setting keymaps
 * bin/keytool              Wrapper for "keytool" Java command
 * bin/kmodsign             Wrapper for Kernel's sign-file command
 * bin/kmodsign.py
 * bin/kubectl              Wrapper for "kubectl" command
 * bin/kubectl.bat
 * bin/kubectl.py
 * bin/kubeseal             Wrapper for "kubeseal" command
 * bin/lsblk                Wrapper for "lsblk" command (sensible defaults)
 * bin/lsblk.py
 * bin/markdown             Convert Markdown files to valid XHTML
 * bin/markdown.bat
 * bin/markdown.py
 * bin/md5                  Calculate MD5 checksums of files
 * bin/md5.bat
 * bin/md5.py
 * bin/sha256               Calculate SHA256 checksums of files
 * bin/sha256.bat
 * bin/sha256.py
 * bin/sha512               Calculate SHA512 checksums of files
 * bin/sha512.bat
 * bin/sha512.py
 * bin/md5cd                Calculate MD5 checksums for CD/DVD data disk
 * bin/md5cd.py
 * bin/meld                 Wrapper for "meld" command
 * bin/meld.bat
 * bin/meld.py
 * bin/menu                 TCL/TK menu system
 * bin/menu.py              (this can be used independent of GNOME/KDE/XFCE menu system)
 * bin/menu.tcl.jinja2
 * bin/menu.yaml
 * bin/mget                 M3U8 streaming video downloader
 * bin/mget.py
 * bin/mirror               Copy all files/directory inside a directory into mirror directory
 * bin/mirror.bat
 * bin/mirror.py
 * bin/mkcd                 Make data/audio/video CD/DVD using CD/DVD writer
 * bin/mkcd.py              (uses wodim, icedax, cdrdao)
 * bin/mkpasswd             Create Create secure random password.
 * bin/mkpasswd.bat
 * bin/mkpasswd.py
 * bin/mksshkeys            Create SSH keys and setup access to remote systems
 * bin/mksshkeys.py
 * bin/mousepad             Wrapper for "mousepad" command
 * bin/mousepad.py
 * bin/mp3                  Encode MP3 audio using avconv (libmp3lame)
 * bin/mp3.py
 * bin/mp4                  Encode MP4 video using avconv (libx264/aac)
 * bin/mp4.py
 * bin/mvn                  MAVEN launcher
 * bin/mvn.py
 * bin/myqdel               MyQS personal batch system for each user
 * bin/myqdel.py
 * bin/myqexec
 * bin/myqexec.py
 * bin/myqsd
 * bin/myqsd.py
 * bin/myqstat
 * bin/myqstat.py
 * bin/myqsub
 * bin/myqsub.py
 * bin/nautilus             Wrapper for "nautilus" command
 * bin/nautilus.py
 * bin/netnice              Run a command with limited network bandwidth (uses trickle)
 * bin/netnice.py
 * bin/netroute             Trace network route to host
 * bin/netroute.bat
 * bin/netroute.py
 * bin/node                 Wrapper for "node" Node.js command
 * bin/npm                  Wrapper for "npm" Node.js command
 * bin/ntpdate              Wrapper for "ntpdate" command
 * bin/ntpdate.py
 * bin/ntplib               Set the date and time via NTP pool
 * bin/ntplib_.py
 * bin/ocr                  Convert image file to text using OCR (uses tesseract)
 * bin/ocr.py
 * bin/ogg                  Encode OGG audio using avconv (libvorbis)
 * bin/ogg.py
 * bin/open                 Open files using hardwired application mapping
 * bin/open.py
 * bin/padman               Sandbox for "wop" launcher
 * bin/padman.py
 * bin/par2                 Wrapper for "par2" command
 * bin/par2.bat
 * bin/pause                Pause until user presses ENTER/RETURN key
 * bin/pause.bat
 * bin/pause.py
 * bin/pbsetup              PUNK BUSTER SETUP launcher
 * bin/pbsetup.py
 * bin/pcheck               Check JPEG picture files
 * bin/pcheck.py
 * bin/pcunix.bat           Start PCUNIX on Windows
 * bin/pdf                  Create PDF file from text/images/postscript/PDF files
 * bin/pdf.py
 * bin/pidgin               Wrapper for "pidgin" command
 * bin/pidgin.bat
 * bin/pidgin.py
 * bin/play                 Play multimedia file/URL
 * bin/play.py              (uses vlc and ffprobe)
 * bin/phtml                Generate XHTML files to view pictures
 * bin/phtml.bat
 * bin/phtml.py
 * bin/plink                Create links to JPEG files
 * bin/plink.py
 * bin/pmeg                 Resize large picture images to mega-pixels limit
 * bin/pmeg.py              (uses convert from ImageMagick)
 * bin/pnum                 Renumber picture files into a numerical series
 * bin/pnum.bat
 * bin/pnum.py
 * bin/pop                  Send popup message to display
 * bin/pop.jar              (uses Java)
 * bin/pop.py
 * bin/psame                Show picture files with same finger print
 * bin/psame.bat
 * bin/psame-venv
 * bin/psame.py
 * bin/psum                 Calculate checksum using imagehash, file size and file modification time
 * bin/psum.bat
 * bin/psum-venv
 * bin/psum.py
 * bin/pyc                  Compile Python source file to PYC file
 * bin/pyc.bat
 * bin/pyc.py
 * bin/pyld.bash            Python loading module for sh/ksh/bash wrapper scripts
 * bin/pyld.py              Load Python main program as module (must have Main class)
 * bin/pyld_gen.py          Wrapper for generic command
 * bin/test_pyld.py         Unit testing suite for "pyld.py"
 * bin/pyprof               Profile Python 3.x program
 * bin/pyprof.bat
 * bin/pyprof.py
 * bin/pyz                  Make a Python 3 ZIP Application in PYZ format
 * bin/pyz.py
 * bin/random               Generate random integer from range.
 * bin/random.bat
 * bin/random_.py
 * bin/readcd               Copy CD/DVD data as a portable ISO/BIN image file
 * bin/readcd.py
 * bin/robo3t               Sandbox for "robo3t" launcher
 * bin/robo3t.py
 * bin/ripcd                Rip CD audio tracks as WAVE sound files
 * bin/ripcd.py
 * bin/ripdvd               Rip Video DVD title to file
 * bin/ripdvd.py
 * bin/rpm                  Wrapper for "rpm" command
 * bin/rpm.py
 * bin/run                  Run a command immune to terminal hangups
 * bin/run.py
 * bin/rotate               Rotate image file clockwise
 * bin/rotate.py
 * bin/sandbox              Sandbox command/shell with read/write and network restrictions
 * bin/sandbox.py
 * bin/say                  Speak words using Google TTS engine
 * bin/say.py               (uses espeak)
 * bin/scp.bat              Windows scp wrapper (uses PuTTY)
 * bin/sdd                  Securely backup/restore partitions using SSH protocol
 * bin/sdd.py
 * bin/sequence             Generate sequences with optional commas
 * bin/sequence.bat
 * bin/sequence.py
 * bin/sftp.bat             Windows sftp wrapper (uses PuTTY)
 * bin/shotcut              Sandbox for "shotcut" launcher
 * bin/shotcut.py
 * bin/shuffle              Print arguments in random order
 * bin/shuffle.bat
 * bin/shuffle.py
 * bin/smount               Securely mount a file system using SSH protocol
 * bin/smount.py            (uses fuse.sshfs)
 * bin/soffice              Sandbox for "soffice" launcher
 * bin/soffice.bat          (LibreOffice)
 * bin/soffice.py
 * bin/sqlplus              Sqlplus wrapper (for Oracle Instant Client)
 * bin/sqlplus64
 * bin/sqlplus.bat
 * bin/sqlplus.py
 * bin/ssh.bat              Windows ssh wrapper (uses PuTTY)
 * bin/ssh-askpass          Wrapper for "ssh-askpass" command
 * bin/ssh_askpass_.py
 * bin/ssync                Securely synchronize file system using SSH protocol
 * bin/ssync.py             (uses rsync)
 * bin/sudo                 Wrapper for "sudo" command
 * bin/sudo.bat
 * bin/sudo.py
 * bin/sumount              Unmount file system securely mounted with SSH protocol
 * bin/sumount.py
 * bin/svncviewer           Sandbox for securely connecting to VNC server using SSH protocol
 * bin/svncviewer.py
 * bin/swell-foop           Sandbox for "swell-foop" command
 * bin/swell_foop_.py
 * bin/sysinfo              System configuration detection tool
 * bin/sysinfo.bat
 * bin/sysinfo.py
 * bin/sysinfo.sh           Old Bourne shell version
 * bin/systemd-analyze      systemd-analyze wrapper (filter buggy firmware/loader timings)
 * bin/systemd_analyze_.py
 * bin/t7z                  Make a compressed archive in TAR.&Z format
 * bin/t7z.py
 * bin/tar                  Make uncompressed archive in TAR format
 * bin/tar.bat
 * bin/tar.py
 * bin/tar_py.py
 * bin/teams                Wrapper for "teams" command
 * bin/teams.py
 * bin/terraform            Wrapper for "terraform" command
 * bin/tbz                  Make a compressed archive in TAR.BZ2
 * bin/tbz.bat
 * bin/tbz.py
 * bin/tgz                  Make a compressed archive in TAR.GZ format
 * bin/tgz.bat
 * bin/tgz.py
 * bin/tiller               Wrapper for "tiller" Helm 2 command
 * bin/tiller.py
 * bin/tinyproxy            Wrapper for "tinyproxy" command
 * bin/tinyproxy.py
 * bin/tkill                Kill tasks by process ID or name
 * bin/tkill.bat
 * bin/tkill.py
 * bin/tls                  Show full list of files
 * bin/tls.bat
 * bin/tls.py
 * bin/tlz                  Make a compressed archive in TAR.LZMA format
 * bin/tlz.py
 * bin/tmux                 Wrapper for "tmux" command
 * bin/tmux.py
 * bin/tocapital            Print arguments wth first letter in upper case
 * bin/tocapital.bat
 * bin/tocapital.py
 * bin/tolower              Print arguments in lower case
 * bin/tolower.bat
 * bin/tolower.py
 * bin/top                  Wrapper for "top" command
 * bin/top.py
 * bin/toupper              Print arguments in upper case
 * bin/toupper.bat
 * bin/toupper.py
 * bin/twait                Wait for task to finish then launch command
 * bin/twait.bat
 * bin/twait.py
 * bin/txz                  Make a compressed archive in TAR.XZ format
 * bin/txz.py
 * bin/tzs                  Make a compressed archive in TAR.ZSTD format
 * bin/tzs.py
 * bin/un7z                 Unpack a compressed archive in 7Z format
 * bin/un7z.bat
 * bin/un7z.py
 * bin/unace                Unpack a compressed archive in ACE format
 * bin/unace.py
 * bin/unbz2                Uncompress a file in BZIP2 format
 * bin/unbz2.py
 * bin/undeb                Unpack a compressed archive in DEB format
 * bin/undeb.py
 * bin/undmg                Unpack a compressed DMG disk file
 * bin/undmg.py
 * bin/ungpg                Unpack an encrypted archive in gpg (pgp compatible) format
 * bin/ungpg.py
 * bin/ungz                 Uncompress a file in GZIP format
 * bin/ungz.py
 * bin/uninitrd             Unpack a compressed archive in INITRAMFS format
 * bin/uninitrd.py
 * bin/uniso                Unpack a portable CD/DVD archive in ISO9660 format
 * bin/uniso.py
 * bin/unjar                Unpack a compressed JAVA archive in JAR format
 * bin/unjar.py
 * bin/unpdf                Unpack PDF file into series of JPG files
 * bin/unpdf.py
 * bin/unpyc                De-compile PYC file to Python source file
 * bin/unpyc.bat
 * bin/unpyc.py
 * bin/unrar                Unpack a compressed archive in RAR format
 * bin/unrar.py
 * bin/unrpm                Unpack a compressed archive in RPM format
 * bin/unrpm.py
 * bin/unsquashfs           Unpack a compressed archive in SQUASHFS format
 * bin/unsquashfs.py
 * bin/unsqlite             Unpack a sqlite database file
 * bin/unsqlite.py
 * bin/unt7z                Unpack a compressed archive in TAR.7Z format
 * bin/unt7z.py
 * bin/untar                Unpack a compressed archive in
 * bin/untar.bat            TAR/TAR.GZ/TAR.BZ2/TAR.LZMA/TAR.XZ/TAR.7Z/TGZ/TBZ/TLZ/TXZ format.
 * bin/untar.py
 * bin/untar_py.py
 * bin/untbz                Unpack a compressed archive in TAR.BZ2 format
 * bin/untbz.bat
 * bin/untbz.py
 * bin/untgz                Unpack a compressed archive in TAR.GZ format.
 * bin/untgz.bat
 * bin/untgz.py
 * bin/untlz                Unpack a compressed archive in TAR.LZMA format.
 * bin/untlz.py
 * bin/untxz                Unpack a compressed archive in TAR.XZ format
 * bin/untxz.py
 * bin/untzs                Unpack a compressed archive in TAR.ZSTD format
 * bin/untzs.py
 * bin/unwine               Shuts down WINE and all Windows applications
 * bin/unwine.py
 * bin/unxz                 Uncompress a file in XZ format
 * bin/unxz.py
 * bin/unz                  Unpack a compressed archive using suitable tool.
 * bin/unz.py
 * bin/unzip                Unpack a compressed archive in ZIP format.
 * bin/unzip.py
 * bin/unzst                Uncompress a file in ZST format.
 * bin/unzst.py
 * bin/urldecode            Decode URL query strings.
 * bin/urldecode.py
 * bin/ut                   Urban Terror game launcher
 * bin/ut.py
 * bin/vbox                 VirtualBox virtual machine manager
 * bin/vbox.py              (uses VBoxManage)
 * bin/vget                 Streaming video downloader using yt-dlp
 * bin/vget.py
 * bin/vi                   Wrapper for "vim" command
 * bin/vim
 * bin/vi.bat
 * bin/vim.bat
 * bin/vim.py
 * bin/view                 View files using hardwired application mapping
 * bin/view.py
 * bin/virtualbox           Wrapper for "virtualbox" command
 * bin/virtualbox.py
 * bin/vlc                  Sandbox for "vlc" launcher
 * bin/vlc.bat
 * bin/vlc.py
 * bin/vlcget               Streaming video downloader using VLC
 * bin/vlcget.py
 * bin/vmware               VMware Player launcher
 * bin/vmware.py
 * bin/vncpasswd            Wrapper for "vncpasswd command
 * bin/vncpasswd.py
 * bin/vncserver            Wrapper for "vncserver" command
 * bin/vncserver.py
 * bin/vncviewer            Wrapper for "vncviewer" command
 * bin/vncviewer.bat
 * bin/vncviewer.py
 * bin/vplay                Play AVI/FLV/MP4 video files in directory.
 * bin/vplay.py             (uses vlc)
 * bin/warsow               Wrapper for "warsow" command
 * bin/wav                  Encode WAV audio using avconv (pcm_s16le).
 * bin/wav.py
 * bin/wesnoth              Sandbox for "wesnoth" launcher
 * bin/wesnoth.py
 * bin/wget                 Wrapper for "wget" command
 * bin/wget.py
 * bin/wine                 Wrapper for "wine" command
 * bin/wine64
 * bin/wine.py
 * bin/cmd
 * bin/weather              Current weather search
 * bin/weather.bat
 * bin/weather.py
 * bin/wipe                 Wrapper for "wipe" C disk wiper command
 * bin/xcalc                Start GNOME/KDE/XFCE calculator
 * bin/xcalc.py
 * bin/xclip                Wrapper for "xclip" command
 * bin/xclip.py
 * bin/xdesktop             Start GNOME/KDE/XFCE file manager
 * bin/xdesktop.py
 * bin/xdiff                Graphical file comparison and merge tool
 * bin/xdiff.bat            (uses meld)
 * bin/xdiff.py
 * bin/xfreerdp.tcl         XFreeRDP TCL/TK panel
 * bin/xedit                Start GNOME/KDE/XFCE graphical editor
 * bin/xedit.py
 * bin/xfcp                 Copy file from clipboard location
 * bin/xfcp.py
 * bin/xlight               Desktop screen backlight utility
 * bin/xlight.py
 * bin/xlock                Start GNOME/KDE/XFCE screen lock
 * bin/xlock.py
 * bin/xlogout              Shutdown X-windows
 * bin/xlogout.py
 * bin/xmail                Start E-mail in web browser
 * bin/xmail.py
 * bin/xmixer               Start GNOME/KDE/XFCE audio mixer
 * bin/xmixer.py
 * bin/xml                  Convert BSON/JSON/XML/YAML to XML
 * bin/xml_.py
 * bin/xmlformat            Re-format XML file.
 * bin/xmlformat.bat
 * bin/xmlformat.py
 * bin/xournal              Sandbox for "xournalpp" launcher
 * bin/xournal.bat
 * bin/xournal.py
 * bin/xreset               Reset to default screen resolution
 * bin/xreset.py
 * bin/xrun                 Run command in new terminal session
 * bin/xrun.py
 * bin/xrun.tcl
 * bin/xsnapshot            Start GNOME/KDE/XFCE screen snapshot
 * bin/xsnapshot.py
 * bin/xsudo                Run sudo command in new terminal session
 * bin/xsudo.py
 * bin/xterm                Wrapper for "xterm" command
 * bin/xterm.py
 * bin/xvolume              Desktop audio volume utility (uses pacmd)
 * bin/xvolume.py
 * bin/xweb                 Start web browser
 * bin/xweb.py
 * bin/xz                   Compress a file in XZ format
 * bin/xz.py
 * bin/yaml                 Convert BSON/JSON/YAML to YAML
 * bin/yaml.bat
 * bin/yaml_.py
 * bin/yping                Ping a host until a connection is made
 * bin/yping.bat
 * bin/yping.py
 * bin/zhspeak              Zhong Hua Speak, Chinese TTS software
 * bin/zhspeak.py
 * bin/zhspeak.tcl
 * bin/z                    Make a compressed archive using suitable tool.
 * bin/z.py
 * bin/zcat                 Concatenate compressed files and print on the standard output
 * bin/zcat.py
 * bin/zip                  Make a compressed archive in ZIP format.
 * bin/zip.py
 * bin/zoom                 Wrapper for "zoom" command
 * bin/zst                  Compress a file in ZST format.
 * bin/zst.py
 * bin/zstd                 Wrapper for "zstd" command
 * bin/zstd_.py
 * bin/cdinst.bat           Windows command prompt batch file or changing directory
 * bin/cdsrc.bat
 * bin/cdtest.bat
 * bin/mkinst.bat
 * bin/mksrc.bat
 * bin/mktest.bat
 * bin/scd.bat
 * ansible/Makefile
 * ansible/ansible.cfg                   Ansible local hosts playbook
 * ansible/bin/show-tags.bash
 * ansible/bin/ssh-keys.bash
 * ansible/inventory/group_vars/all
 * ansible/inventory/group_vars/local_hosts
 * ansible/inventory/group_vars/local_nodes
 * ansible/inventory/group_vars/local_vmhosts
 * ansible/inventory/host_vars/debian11.local
 * ansible/inventory/host_vars/debian12.local
 * ansible/inventory/host_vars/debianmac.local
 * ansible/inventory/host_vars/hotdog.local
 * ansible/inventory/host_vars/koko.local
 * ansible/inventory/host_vars/netbook.local
 * ansible/inventory/host_vars/netty.local
 * ansible/inventory/host_vars/ryzen.local
 * ansible/inventory/host_vars/viva.local
 * ansible/inventory/host_vars/webtv.local
 * ansible/inventory/host_vars/xiaobear.local
 * ansible/inventory/local_nodes
 * ansible/local-playbook.yaml
 * ansible/roles/ansible-user/tasks/main.yaml
 * ansible/roles/local-system/defaults/main.yaml
 * ansible/roles/local-system/files/iptables
 * ansible/roles/local-system/files/nopasswd-users
 * ansible/roles/local-system/tasks/main.yaml
 * ansible/roles/local-system/tasks/system-setup.yaml
 * ansible/roles/local-system/tasks/tlp-setup.yaml
 * ansible/roles/local-system/templates/iptables.conf
 * ansible/roles/local-system/templates/rc.local-opt
 * ansible/roles/local-users/defaults/main.yaml
 * ansible/roles/local-users/meta/main.yaml
 * ansible/roles/user-home/defaults/main.yaml
 * ansible/roles/user-home/files/accels
 * ansible/roles/user-home/files/animate.desktop
 * ansible/roles/user-home/files/geeqierc.xml
 * ansible/roles/user-home/files/gimp.desktop
 * ansible/roles/user-home/files/play.desktop
 * ansible/roles/user-home/files/rotate-270.desktop
 * ansible/roles/user-home/files/rotate-90.desktop
 * ansible/roles/user-home/files/thunar.xml
 * ansible/roles/user-home/files/vlcrc
 * ansible/roles/user-home/tasks/cmdline-apps.yaml
 * ansible/roles/user-home/tasks/gui-apps.yaml
 * ansible/roles/user-home/tasks/login-user.yaml
 * ansible/roles/user-home/tasks/main.yaml
 * ansible/roles/user-home/templates/htoprc
 * ansible/roles/user-home/templates/netnice.json
 * ansible/roles/user-home/vars/main.yaml
 * appimage/Makefile
 * appimage/bin/build-appimage.bash      Wrapper for "appimage-builder" command
 * appimage/bin/gpg                      Disable GPG signing
 * appimage/bin/appimage/bin/zsyncmake   Disable ".zsync" creation
 * appimage/0ad-0.0.26/AppImageBuilder.yaml
 * appimage/0ad-0.0.26/Makefile
 * appimage/bash-5.1.4/AppImageBuilder.yaml
 * appimage/bash-5.1.4/Makefile          Bash 5.1.4 (Debian 11)
 * appimage/wesnoth-1.14.15/AppImageBuilder.yaml
 * appimage/wesnoth-1.14.15/Makefile     Wesnoth 1.14.15 (Debian 11))
 * appimage/wesnoth-1.16.8/AppImageBuilder.yaml
 * appimage/wesnoth-1.16.8/Makefile      Wesnoth 1.16.8 (Debian 11 backports)
 * compile/COMPILE-7zip.bash             7zip compile script
 * compile/COMPILE-aria2.bash            Aria2 compile script
 * compile/COMPILE-git.bash              Git compile script
 * compile/COMPILE-openmpi.bash          Open MPI compile script
 * compile/COMPILE-par2.bash             Par2cmdline compile script
 * compile/COMPILE-python-2.7.bash       Python 2.7 compile script
 * compile/COMPILE-python-3.5.bash       Python 3.5 compile script
 * compile/COMPILE-python-3.6.bash       Python 3.6 compile script
 * compile/COMPILE-python-3.7.bash       Python 3.7 compile script
 * compile/COMPILE-python-3.8.bash       Python 3.8 compile script
 * compile/COMPILE-python-3.9.bash       Python 3.9 compile script
 * compile/COMPILE-python-3.10.bash      Python 3.10 compile script
 * compile/COMPILE-python-3.11.bash      Python 3.11 compile script
 * compile/COMPILE-tinyproxy             TinyProxy compile script
 * compile/COMPILE-tmux                  TMUX compile script
 * compile/COMPILE-unrar                 UnRar compile script
 * compile/COMPILE-xz-utils              XZ-Utils compile script
 * compile/COMPILE-zstd                  Zstandard compile script
 * config/Xresources                     Copy to "$HOME/.Xresources" to set xterm resources
 * config/accels                         Copy to "$HOME/.config/geeqie" for keyboard shortcuts
 * config/adblock.txt                    Adblock filter list
 * config/autostart.bash                 Copy to "$HOME/.config/autostart.bash" & add to desktop auto startup
 * config/autostart-opt.bash             Copy to "$HOME/.config/autostart-opt.bash" for optional settings
 * config/autostart.desktop              Copy to "$HOME/.config/autostart/autostart.desktop" for XFCE autostart
 * config/config                         Copy to "$HOME/.ssh/config"
 * config/gitconfig                      Copy to "$HOME/.gitconfig" and edit
 * config/iptables.conf                  IPTABLES setup script
 * config/login                          Copy to "$HOME/.login" for csh/tcsh shells (translated ".profile")
 * config/mimeapps.list                  Copy to "$HOME/.local/share/applications" for Mime definitions
 * config/minttyrc                       Copy to "$HOME/.minttyrc" for MSYS2 terminal
 * config/tmux.conf                      Copy to "$HOME/.tmux.conf" fro TMUX terminal
 * config/profile                        Copy to "$HOME/.profile" for ksh/ash/bash shells settings
 * config/profile-opt                    Copy to "$HOME/.profile-opt" for optional ksh/bash shells settings
 * config/rc.local                       Copy to "/etc/rc.local" for system startup commands
 * config/rc.local-opt                   Copy to "/etc/rc.local-opt" for optional system startup commands
 * config/terminalrc                     Copy to "$HOME/.config/xfce4/terminal" for XFCE terminal
 * config/vimrc                          Copy to "$HOME/.vimrc" for VIM defaults
 * config/vm-linux0.vbox                 VirtualBox Linux example
 * config/vm-win10.vbox                  VirtualBox Windows example
 * config/userapp-evince.desktop         Copy to "$HOME/.local/share/applications" for Evince/Atril
 * config/userapp-gqview.desktop         Copy to "$HOME/.local/share/applications" for GQview/Geeqie
 * config/userapp-soffice.desktop        Copy to "$HOME/.local/share/applications" for LibreOffice
 * config/userapp-vlc.desktop            Copy to "$HOME/.local/share/applications" for VLC
 * config/winsetup.bat                   Configure Windows VirtualBox VMs
 * config/winsetup.bash
 * config/xscreensaver                   Copy to "$HOME/.xscreensaver" for XScreenSaver defaults
 * cloudformation/1pxy/1pxy.json         CloudFormation: 1pxy example
 * cloudformation/1pxy/Makefile
 * cloudformation/1pxy/submit.bash
 * cloudformation/multi-stacks/Makefile  CloudFormation: multi-stacks example
 * cloudformation/multi-stacks/main_stack.json
 * cloudformation/multi-stacks/pxy_stack.json
 * cloudformation/multi-stacks/sg_stack.json
 * cloudformation/multi-stacks/submit.bash
 * cookiecutter/Makefile                 Makefile for building examples
 * cookiecutter/docker/cookiecutter.json
 * cookiecutter/docker/{{cookiecutter.project_name}}/Dockerfile
 * cookiecutter/docker/{{cookiecutter.project_name}}/Makefile
 * docker/Makefile                       Makefile for building all images
 * docker/bin/bash2ash
 * docker/bin/create-rootfs.bash
 * docker/bin/docker-load.bash           Load docker images
 * docker/bin/docker-pull-save.bash      Pull Docker images and save to tar.xz archives
 * docker/bin/docker-save.bash           Save Docker images to tar.xz archives
 * docker/almalinux-8/Dockerfile
 * docker/almalinux-8/Makefile           almalinux:8 based linux
 * docker/almalinux-8/bash/Dockerfile
 * docker/almalinux-8/bash/Makefile      almalinux:8 based BASH login
 * docker/almalinux-8/dev/Dockerfile
 * docker/almalinux-8/dev/Makefile       alamlinux:8 based GCC dev shell
 * docker/almalinux-9/Dockerfile
 * docker/almalinux-9/Makefile           almalinux:9 based linux
 * docker/almalinux-9/bash/Dockerfile
 * docker/almalinux-9/bash/Makefile      almalinux:9 based BASH login
 * docker/almalinux-9/dev/Dockerfile
 * docker/almalinux-9/dev/Makefile       alamlinux:9 based GCC dev shell
 * docker/alpine-3.16/Makefile
 * docker/alpine-3.16/Dockerfile         alpine:3.16 based linux
 * docker/alpine-3.16/bash/Makefile
 * docker/alpine-3.16/bash/Dockerfile    alpine:3.16 based BASH login
 * docker/alpine-3.16/dev/Makefile
 * docker/alpine-3.16/dev/Dockerfile     alpine:3.16 based GCC dev shell
 * docker/alpine-3.17/Dockerfile
 * docker/alpine-3.17/Makefile           alpine:3.17 based linux
 * docker/alpine-3.17/bash/Dockerfile
 * docker/alpine-3.17/bash/Makefile      alpine:3.17 based BASH login
 * docker/alpine-3.17/dev/Dockerfile
 * docker/alpine-3.17/dev/Makefile       alpine:3.17 based GCC dev shell
 * docker/i386-alpine-3.17/Makefile
 * docker/i386-alpine-3.17/Dockerfile    i386/alpine:3.17 based linux
 * docker/i386-alpine-3.17/bash/Makefile
 * docker/i386-alpine-3.17/bash/Dockerfile  i386/alpine:3.17 based BASH login
 * docker/i386-alpine-3.17/dev/Makefile
 * docker/i386-alpine-3.17/dev/Dockerfile  i386/alpine:3.17 based GCC dev shell
 * docker/busybox-1.32/Dockerfile
 * docker/busybox-1.32/Makefile          busybox:1.33 based linux
 * docker/busybox-1.32/bash/Dockerfile
 * docker/busybox-1.32/bash/Makefile     busybox:1.33 based BASH login
 * docker/centos-7/Dockerfile
 * docker/centos-7/Makefile              centos:7 based linux
 * docker/centos-7/bash/Dockerfile
 * docker/centos-7/bash/Makefile         centos:7 based BASH login
 * docker/centos-7/dev/Dockerfile
 * docker/centos-7/dev/Makefile          centos:7 based GCC dev shell
 * docker/debian-10/Dockerfile
 * docker/debian-10/Makefile             debian:10-slim based linux
 * docker/debian-10/bash/Dockerfile
 * docker/debian-10/bash/Makefile        debian:10-slim based BASH login
 * docker/debian-10/dev/Dockerfile
 * docker/debian-10/dev/Makefile         debian:10-slim based GCC dev shell
 * docker/debian-11/Dockerfile
 * docker/debian-11/Makefile             debian:11-slim based linux
 * docker/debian-11/bash/Dockerfile
 * docker/debian-11/bash/Makefile        debian:11-slim based BASH login
 * docker/debian-11/docker/Dockerfile
 * docker/debian-11/docker/Makefile      debian:11-slim based DOCKER shell
 * docker/debian-11/xfce/Dockerfile
 * docker/debian-11/xfce/Makefile        debian:11-slim based XFCE environment
 * docker/debian-11/xfce/files/allow-owner
 * docker/debian-11/xfce/files/docker-init
 * docker/debian-11/xfce/files/xstartup
 * docker/i386-debian-11/Dockerfile
 * docker/i386-debian-11/Makefile        i386/debian:11-slim based linux
 * docker/i386-debian-11/bash/Dockerfile
 * docker/i386-debian-11/bash/Makefile   i386/debian:11-slim based BASH login
 * docker/i386-debian-11/dev/Dockerfile
 * docker/i386-debian-11/dev/Makefile    i386/debian:11-slim based GCC dev shell
 * docker/golang-1.19/Dockerfile
 * docker/golang-1.19/Makefile           golang:1.19-alpine based compiler app
 * docker/httpd-2.4/Dockerfile
 * docker/httpd-2.4/Makefile             httpd:2.4-alpine (Apache) based web server
 * docker/httpd-2.4/files/httpd.conf
 * docker/httpd-2.4/public-html/index.html
 * docker/httpd-2.4/public-html/testlcd.js
 * docker/httpd-2.4/public-html/testlcd.xhtml
 * docker/nginx-1.18/Dockerfile
 * docker/nginx-1.18/Makefile            nginx:1.18-alpine based reverse proxy server
 * docker/nginx-1.18/files/nginx-proxy.conf
 * docker/python-3.10/Dockerfile
 * docker/python-3.10/Makefile           python:3.10-slim-bullseye based Python app
 * docker/python-3.10/bash/Dockerfile
 * docker/python-3.10/bash/Makefile      python:3.10-slim-bullseye based BASH login
 * docker/python-3.10/dev/Dockerfile
 * docker/python-3.10/dev/Makefile       python:3.10-slim-bullseye based dev shell
 * docker/python-3.10/devpi/Dockerfile
 * docker/python-3.10/devpi/Makefile     python:3.10-slim-bullseye based devpi server app
 * docker/python-3.10/full/Dockerfile
 * docker/python-3.10/full/Makefile      python:3.10-slim-bullseye based shell with full packages
 * docker/registry-2.6/Dockerfile
 * docker/registry-2.6/Makefile          registry:2.6 based Docker Registry server app
 * docker/registry-2.6/files/config.yaml
 * docker/scratch/Dockerfile
 * docker/scratch/Makefile               scratch image for jail breaking (docker-sudo)
 * docker/ubuntu-18.04/Makefile
 * docker/ubuntu-18.04/Dockerfile        ubuntu:18.04 based linux
 * docker/ubuntu-18.04/bash/Makefile
 * docker/ubuntu-18.04/bash/Dockerfile   ubuntu:18.04 based BASH login
 * docker/ubuntu-18.04/dev/Makefile
 * docker/ubuntu-18.04/dev/Dockerfile    ubuntu:18.04 based GCC dev shell
 * docker/ubuntu-20.04/Dockerfile
 * docker/ubuntu-20.04/Makefile          ubuntu:20.04 based linux
 * docker/ubuntu-20.04/bash/Dockerfile
 * docker/ubuntu-20.04/bash/Makefile     ubuntu:20.04 based BASH login
 * docker/ubuntu-20.04/dev/Dockerfile
 * docker/ubuntu-20.04/dev/Makefile      ubuntu:20.04 based GCC dev shell
 * docker/ubuntu-22.04/Makefile
 * docker/ubuntu-22.04/Dockerfile        ubuntu:22.04 based linux
 * docker/ubuntu-22.04/bash/Makefile
 * docker/ubuntu-22.04/bash/Dockerfile   ubuntu:22.04 based BASH login
 * docker/ubuntu-22.04/dev/Makefile
 * docker/ubuntu-22.04/dev/Dockerfile    ubuntu:22.04 based GCC dev shell
 * etc/python-minimum-requirements.txt   Minimum requirements requrid by "*_mod.py" modules.
 * etc/python-packages.bash              Install/check Python packages requirements
 * etc/python-requirements.txt           Default requirements file for Python
 * etc/python-requirements_2.7.txt       Additional requirements for Python 2.7
 * etc/python-requirements_3.5.txt       Additional requirements for Python 3.5
 * etc/python-requirements_3.6.txt       Additional requirements for Python 3.6
 * etc/python-requirements_3.7.txt       Additional requirements for Python 3.7
 * etc/python-requirements_3.8.txt       Additional requirements for Python 3.8
 * etc/python-requirements_3.9.txt       Additional requirements for Python 3.9
 * etc/python-requirements_3.10mac.txt   Additional requirements for Python 3.10 on Mac
 * etc/python-requirements_3.11.txt      Additional requirements for Python 3.11
 * etc/setbin                            Hybrid Bourne/C-shell script for sh/ksh/bash/csh/tcsh initialization
 * etc/setbin.bat                        Windows Command prompt initialization
 * etc/setbin.ps1                        Windows Power shell initialization
 * kubernetes/Makefile
 * kubernetes/bin/kube-connect.bash      Connect to Kubernetes ingress/service port
 * kubernetes/bin/kube-save.bash         Save Kubernetes control plane docker images
 * kubernetes/monitor-host/Makefile      Kubernetes: host monitoring (drtuxwang/debian-bash:stable)
 * kubernetes/monitor-host/monitor-host-daemonset.yaml
 * kubernetes/nginx-proxy-fwd/Makefile   NGINX http/https proxy forwarding example
 * kubernetes/nginx-proxy-fwd/nginx-proxy-fwd.conf
 * kubernetes/nginx-proxy-fwd/nginx-proxy-fwd.yaml
 * kubernetes/nginx-proxy-fwd/proxy-kube-local.crt
 * kubernetes/nginx-proxy-fwd/proxy-kube-local.key
 * kubernetes/test-box/Makefile          Kubernetes: Test Box (drtuxwang/debian-bash:stable)
 * kubernetes/test-box/test-box.yaml
 * kubernetes/test-server/Makefile       Kubernetes: examples (drtuxwang/debian-bash:stable)
 * kubernetes/test-server/test-server-daemonset.yaml
 * kubernetes/test-server/test-server-deployment.yaml
 * kubernetes/test-server/test-server-headless-service.yaml
 * kubernetes/test-server/test-server-ingress.yaml
 * kubernetes/test-server/test-server-pod.yaml
 * kubernetes/test-server/test-server-replicationcontroller.yaml
 * kubernetes/test-server/test-server-secret-tls.yaml
 * kubernetes/test-server/test-server-service.yaml
 * kubernetes/test0server/test-server-statefulset.yaml
 * kubernetes/socat-fwd/Makefile         SOCAT forwarding example
 * kubernetes/socat-fwd/socat-fwd.yaml
 * kubernetes/test-cronjob/Makefile      Kubernetes: cronjob example (drtuxwang/busybox-bash:stable)
 * kubernetes/test-cronjob/batch-crontab.yaml
 * kubernetes/test-storage/Makefile      Kubernetes: Persistent Volume example
 * kubernetes/test-storage/server-pv.yaml
 * kubernetes/test-storage/server-statefulset.yaml
 * helm/Makefile
 * helm/bin/helm-save.bash               Save Helm release docker images
 * helm/cassandra/Makefile               Helm Chart: bitnami/cassandra 10.3.2 (app-3.11.13)
 * helm/cassandra/values.yaml
 * helm/etcd/Makefile                    Helm Chart: bitnami/etcd 8.10.2 (app-3.4.24)
 * helm/etcd/values.yaml
 * helm/grafana/Makefile                 Helm Chart: bitnami/grafana 8.2.33 (app-8.5.10)
 * helm/grafana/values.yaml
 * helm/jenkins/Makefile                 Helm Chart: bitnami/jenkins 12.1.2 (app-2.387.3)
 * helm/jenkins/values.yaml
 * helm/kafka/Makefile                   Helm Chart: bitnami/kafka 21.4.6 (app-2.8.1)
 * helm/kafka/test-connect.bash
 * helm/kafka/values.yaml
 * helm/mongodb/Makefile                 Helm Chart: bitnami/mongodb 13.14.2 (app-4.4.15)
 * helm/mongodb/values.yaml
 * helm/nexus/Makefile                   Helm Chart: oteemo/sonatype-nexus 5.4.1 (app-3.27.0)
 * helm/nexus/values.yaml
 * helm/nginx/Makefile                   Helm Chart: bitnami/nginx 14.2.2 (app-1.18.0)
 * helm/nginx/values.yaml
 * helm/ops-server/ops-server/templates/box-deployment.yaml
 * helm/ops-server/values.yaml
 * helm/oracle-xe/Makefile               Helm Chart: Oracle XE test (datagrip/oracle:11.2)
 * helm/oracle-xe/oracle-xe/Chart.yaml
 * helm/oracle-xe/oracle-xe/templates/_helpers.tpl
 * helm/oracle-xe/oracle-xe/templates/box-headless-service.yaml
 * helm/oracle-xe/oracle-xe/templates/box-service.yaml
 * helm/oracle-xe/oracle-xe/templates/box-statefulset.yaml
 * helm/oracle-xe/values.yaml
 * helm/postgresql/Makefile              Helm Chart: bitnami/postgresql 12.4.3 (app-11.18.0)
 * helm/postgresql/values.yaml
 * helm/prometheus/Makefile              Helm Chart: prometheus-community/prometheus 22.4.1 (app-2.37.6)
 * helm/prometheus/values.yaml
 * helm/pushgateway/Makefile             Helm Chart: prometheus-community/prometheus-pushgateway 2.1.6 (app-1.3.1)
 * helm/pushgateway/values.yaml
 * helm/rabbitmq/Makefile                Helm Chart: bitnami/rabbitmq 11.14.5 (app-3.8.35)
 * helm/rabbitmq/values.yaml
 * helm/test-box/Makefile                Helm Chart: drtuxwang/test-box (drtuxwang/debian-bash:stable)
 * helm/test-box/drtuxwang/test-box/Chart.yaml
 * helm/test_box/drtuxwang/text-box/templates/_helpers.tpl
 * helm/test-server/Makefile             Helm Chart: drtuxwang/test-server (drtuxwang/debian-bash:stable)
 * helm/test-server/drtuxwang/test-server/Chart.yaml
 * helm/test-server/drtuxwang/test-server/requirements.lock
 * helm/test-server/drtuxwang/test-server/requirements.yaml
 * helm/test-server/drtuxwang/test-server/templates/_helpers.tpl
 * helm/test-server/drtuxwang/test-server/templates/box-headless-service.yaml
 * helm/test-server/drtuxwang/test-server/templates/box-ingress.yaml
 * helm/test-server/drtuxwang/test-server/templates/box-secret-tls.yaml
 * helm/test-server/drtuxwang/test-server/templates/box-service.yaml
 * helm/test-server/drtuxwang/test-server/templates/box-statefulset.yaml
 * helm/test-server/values.yaml
 * helm/xfce-server/Makefile            Helm Chart: drtuxwang/xfce-server (drtuxwang/debian-xfce:stable)
 * helm/xfce-server/values.yaml
 * helm/xfce-server/drtuxwang/xfce-server/Chart.yaml
 * helm/xfce-server/drtuxwang/xfce-server/requirements.lock
 * helm/xfce-server/drtuxwang/xfce-server/requirements.yaml
 * helm/xfce-server/drtuxwang/xfce-server/templates/_helpers.tpl
 * helm/xfce-server/xfce-server/templates/box-headless-service.yaml
 * helm/xfce-server/xfce-server/templates/box-service.yaml
 * helm/xfce-server/xfce-server/templates/box-statefulset.yaml
 * python/simple-cython/Makefile         Simple Cython example
 * python/simple-cython/cython_example.pyx
 * python/simple-cython/run.py
 * python/simple-flask/Makefile          Simple Flask demo
 * python/simple-flask/simple_flask.py
 * python/simple-flask/templates/hello.html
 * python/simple-package/Makefile        Simple Egg & WHL package
 * python/simple-package/run.py
 * python/simple-package/setup.py
 * python/simple-package/hello/__init__.py
 * python/simple-package/hello/message.py
 * python/simple-tornado/Makefile        Tornado examples
 * python/simple-tornado/tornado_client.py
 * python/simple-tornado/tornado_server.py
 * terraform-aws/1pxy/aws_config.tf      Terraform AWS: 1pxy example
 * terraform-aws/1pxy/aws_resources.tf
 * terraform-aws/1pxy/pxy_resources.tf
 * terraform-aws/1pxy/pxy_variables.tf
 * terraform-aws/pxy-as/aws_config.tf    Terraform AWS: pxy-as example
 * terraform-aws/pxy-as/aws_resources.tf
 * terraform-aws/pxy-as/pxy_resources.tf
 * terraform-aws/pxy-as/pxy_variables.tf
 * wipe/COMPILE
 * wipe/Makefile
 * wipe/wipe.c
```
