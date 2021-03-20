## 1996-2021 By Dr Colin Kong

These are production scripts and configuration files that I use and share. Originally the scripts
were started Bourne shell scripts started during my University days and continuously enhanced over
the years. Now most of the scripts are written in Python 3.
---
```
 * Jenkinsfile            Jenkins pipeline configuration file
 * codefresh.yaml         Codefresh pipeline configuration file
 * Makefile               Makefile for testing
 * bin/command\_mod.py     Python command line handling module
 * bin/config\_mod.py      Python config module for handling "config\_mod.yaml)
 * bin/config\_mod.yaml    Configuration file apps, bindings & parameters
 * bin/debug\_mod.py       Python debugging tools module
 * bin/desktop\_mod.py     Python X-windows desktop module
 * bin/file\_mod.py        Python file handling utility module
 * bin/logging\_mod.py     Python logging handling module
 * bin/network\_mod.py     Python network handling utility module
 * bin/power\_mod.py       Python power handling module
 * bin/subtask\_mod.py     Python sub task handling module
 * bin/task\_mod.py        Python task handling utility module
 * bin/python             Python startup (allowing non systems port)
 * bin/python.bat
 * bin/python2
 * bin/python2.bat
 * bin/python2.7
 * bin/python2.7.bat
 * bin/python3
 * bin/python3.bat
 * bin/python3.5
 * bin/python3.5.bat
 * bin/python3.6
 * bin/python3.6.bat
 * bin/python3.7
 * bin/python3.7.bat
 * bin/python3.8
 * bin/python3.9
 * bin/2to3               Python 3.x script wrappers (allowing non systems port)
 * bin/2to3.bat
 * bin/2to3-3.5
 * bin/2to3-3.5.bat
 * bin/ansible
 * bin/ansible-playbook
 * bin/ansible-vault
 * bin/aws
 * bin/aws.bat
 * bin/cookiecutter
 * bin/cookiecutter.bat
 * bin/cython
 * bin/cython.bat
 * bin/cythonize
 * bin/cythonize.bat
 * bin/devpi
 * bin/devpi.bat
 * bin/django-admin
 * bin/django-admin.bat
 * bin/docker-compose
 * bin/docker-compose.bat
 * bin/flask
 * bin/flask.bat
 * bin/fly
 * bin/fly.py
 * bin/glances
 * bin/gtts-cli
 * bin/ipdb3
 * bin/ipdb3.bat
 * bin/ipython
 * bin/ipython.bat
 * bin/ipython3
 * bin/ipython3.bat
 * bin/jenkins-jobs
 * bin/jenkins-jobs.bat
 * bin/markdown
 * bin/markdown.py
 * bin/markdown\_py
 * bin/markdown\_py.bat
 * bin/mid3iconv
 * bin/mid3iconv.bat
 * bin/mid3v2
 * bin/mid3v2.bat
 * bin/nexus3
 * bin/pep8
 * bin/pep8.bat
 * bin/pip
 * bin/pip.bat
 * bin/pip3
 * bin/pip3.bat
 * bin/pip3.5
 * bin/pip3.5.bat
 * bin/pycodestyle
 * bin/pycodestyle.bat
 * bin/pydoc3
 * bin/pydoc3.bat
 * bin/pydoc3.5
 * bin/pydoc3.5.bat
 * bin/pyflakes
 * bin/pyflakes.bat
 * bin/pylint
 * bin/pylint.bat
 * bin/pytest
 * bin/pytest.bat
 * bin/tox
 * bin/tox.bat
 * bin/uncompyle6
 * bin/uncompyle6.bat
 * bin/virtualenv
 * bin/virtualenv.bat
 * bin/youtube-dl
 * bin/youtube-dl.bat
 * bin/7z                 Make a compressed archive in 7z format
 * bin/7z.bat             (uses p7zip)
 * bin/7za
 * bin/p7zip.py
 * bin/aftp               Automatic connection to FTP server anonymously
 * bin/aftp.py
 * bin/aplay              Play MP3/OGG/WAV audio files in directory
 * bin/aplay.py           (uses vlc)
 * bin/aria2c             aria2c wrapper (allowing non systems port)
 * bin/aria2c.py          (bandwidth 512KB limit default using "trickle", "$HOME/.config/tickle.json)
 * bin/audacity           audacity wrapper (allowing non systems port)
 * bin/audacity.bat
 * bin/audacity.py
 * bin/avi                Encode AVI video using avconv (libxvid/libmp3lame)
 * bin/avi.py
 * bin/battery            Linux battery status utility
 * bin/battery.py
 * bin/bell               Play bell.ogg sound
 * bin/bell.ogg           (uses cvlc or ogg123)
 * bin/bell.py
 * bin/bson               Convert BSON/JSON/YAML to BSON
 * bin/bson.bat
 * bin/bson\_.py
 * bin/breaktimer         Break reminder timer
 * bin/breaktimer.py      (10 min default)
 * bin/bz2                Compress a file in BZIP2 format (allowing non systems port)
 * bin/bz2\_.py
 * bin/calendar           Displays month or year calendar
 * bin/calendar.bat
 * bin/calendar\_.py
 * bin/cdspeed            Set CD/DVD drive speed
 * bin/cdspeed.py         ("$HOME/.config/cdspeed.json")
 * bin/chkconfig          Check BSON/JSON/YAML configuration files for errors
 * bin/chkconfig.bat
 * bin/chkconfig.py
 * bin/chkpath            Check PATH and return correct settings
 * bin/chkpath.bat
 * bin/chkpath.py
 * bin/chksequence        Check for missing sequence in numbered files
 * bin/chksequence.bat
 * bin/chksequence.py
 * bin/chrome             chrome wrapper (allowing non systems port)
 * bin/chrome-proxy
 * bin/chrome-proxy.bat
 * bin/chrome.bat
 * bin/chrome.py
 * bin/chromium           chromium wapper (allowing non systems port)
 * bin/chromium.bat
 * bin/chromium.py
 * bin/chroot             chroot wrapper (allowing non systems port)
 * bin/chroot.py          (creates /shared mount automatically)
 * bin/clam               Run ClamAV anti-virus scanner
 * bin/clam.bat
 * bin/clam.py
 * bin/cluster            Run command on a subnet in parallel
 * bin/cluster.py
 * bin/deb                Debian package management tools
 * bin/deb.py             (support offline repository searching and update checks
 * bin/debchkdir
 * bin/debchkdir.py
 * bin/debchkinstall
 * bin/debchkinstall.py
 * bin/debchkupdate
 * bin/debchkupdate.py
 * bin/debdistfind
 * bin/debdistfind.py
 * bin/debdistget
 * bin/debdistget.py
 * bin/debdistgrep
 * bin/debdistgrep.py
 * bin/debdistinfo
 * bin/debdistinfo.py
 * bin/dep                dep wrapper (for golang)
 * bin/dep.py
 * bin/dockerreg          Docker Registry tool
 * bin/dockerreg.bat
 * bin/dockerreg.py
 * bin/docker-sandbox     Starts Docker sandbox environment
 * bin/docker-sudo        Starts Docker sudo app
 * bin/dpkg               dpkg wrapper (force system Python)
 * bin/dpkg.py
 * bin/eclipse            eclipse wrapper (allowing non systems port)
 * bin/eclipse.py
 * bin/espeak             espeak wrapper (allowing non systems port)
 * bin/espeak.py
 * bin/et                 ET Wolf wrapper (allowing non systems port)
 * bin/et.py
 * bin/et.tcl
 * bin/etl                ET Legacy wrapper (allowing non systems port)
 * bin/etl.py
 * bin/evince             evince wrapper (allowing non systems port)
 * bin/evince.bat
 * bin/evince.py
 * bin/extfbfl            Extract Facebook friends list from saved HTML file
 * bin/extfbfl.bat
 * bin/extfbfl.py
 * bin/extjs              Extracts Javascript from a HTML file
 * bin/extjs.bat
 * bin/extjs.py
 * bin/exturl             Extracts http references from a HTML file
 * bin/exturl.bat
 * bin/exturl.py
 * bin/fcat               Concatenate files and print on the standard output
 * bin/fcat.bat           (similar to cat)
 * bin/fcat.py
 * bin/fchop              Chop up a file into chunks
 * bin/fchop.bat
 * bin/fchop.py
 * bin/fcount             Count number of lines and maximum columns used in file
 * bin/fcount.bat
 * bin/fcount.py
 * bin/fcp                Copy files and directories
 * bin/fcp.bat            (Preserving time stamps)
 * bin/fcp.py
 * bin/fcpall             Copy a file to multiple target files
 * bin/fcpall.bat
 * bin/fcpall.py
 * bin/fcpclip            Copy file from clipboard location
 * bin/fcpclip.py
 * bin/fcplink            Replace symbolic link to files with copies
 * bin/fcplink.py
 * bin/fdiff              Show summary of differences between two directories recursively
 * bin/fdiff.bat
 * bin/fdiff.py
 * bin/fdu                Show file disk usage
 * bin/fdu.bat            (like du but same values independent of file system including Windows)
 * bin/fdu.py
 * bin/ffile              Determine file type
 * bin/ffile.bat
 * bin/ffile.py
 * bin/ffind              Find file or directory
 * bin/ffind.bat          (uses regular expression)
 * bin/ffind.py
 * bin/ffind0             Find zero sized files
 * bin/ffind0.bat
 * bin/ffind0.py
 * bin/ffix               Remove horrible characters in filename
 * bin/ffix.bat           (like spaces etc)
 * bin/ffix.py
 * bin/ffmpeg             ffmpeg wrapper (allowing non systems port)
 * bin/ffmpeg.py
 * bin/ffplay             ffplay wrapper (allowing non systems port)
 * bin/ffplay.py
 * bin/ffprobe            ffprobe wrapper (allowing non systems port)
 * bin/ffprobe.py
 * bin/fget               Download http/https/ftp/file URLs
 * bin/fget.bat
 * bin/fget.py
 * bin/fgrep.bat          Print lines matching a pattern
 * bin/fgrep.py           (Windows only)
 * bin/fhead              Output the first n lines of a file
 * bin/fhead.bat          (like head)
 * bin/fhead.py
 * bin/firefox            firefox wrapper (allowing non systems port)
 * bin/firefox.bat        (supports "-copy", "-no-remote" and "-reset" enhancements)
 * bin/firefox.py
 * bin/fixwav             Normalize volume of wave files (-16.0dB rms mean volume)
 * bin/fixwav.py          (uses normalize-audio)
 * bin/flashgot-term      Firefox Flashgot terminal startup script
 * bin/flink              Recursively link all files
 * bin/flink.py
 * bin/fls                Show full list of files
 * bin/fls.bat
 * bin/fls.py
 * bin/fmkdir             Create a single lower case directory
 * bin/fmkdir.bat
 * bin/fmkdir.py
 * bin/fmod               Set file access mode
 * bin/fmod.bat
 * bin/fmod.py
 * bin/fmv                Move or rename files
 * bin/fmv.bat
 * bin/fmv.py
 * bin/fpar2              Calculate PAR2 parity checksum and repair tool.
 * bin/fpar2.bat
 * bin/fpar2.py
 * bin/fpeek              Dump the first and last few bytes of a binary file
 * bin/fpeek.bat
 * bin/fpeek.py
 * bin/fprint             Sends text/images/postscript/PDF to printer
 * bin/fprint.py
 * bin/frm                Remove files or directories
 * bin/frm.bat
 * bin/frm.py
 * bin/frn                Rename file/directory by replacing some characters
 * bin/frn.bat
 * bin/frn.py
 * bin/fsame              Show files with same MD5 checksums
 * bin/fsame.bat
 * bin/fsame.py
 * bin/fshare             File sharing utility (currently dropbox only)
 * bin/fshare.bat
 * bin/fshare.py
 * bin/fsort              Unicode sort lines of a file
 * bin/fsort.bat
 * bin/fsort.py
 * bin/fstat              Display file status
 * bin/fstat.bat
 * bin/fstat.py
 * bin/fstrings           Print the strings of printable characters in files
 * bin/fstrings.bat       (like strings)
 * bin/fstrings.py
 * bin/fsub               Substitute patterns on lines in files
 * bin/fsub.bat           (uses regular expression to match text)
 * bin/fsub.py
 * bin/fsum               Calculate checksum using MD5, file size and file modification time
 * bin/fsum.bat           (can produce ".fsum" files)
 * bin/fsum.py
 * bin/ftail              Output the last n lines of a file
 * bin/ftail.bat          (like tail)
 * bin/ftail.py
 * bin/ftodos             Converts file to "\r\n" newline format
 * bin/ftodos.bat
 * bin/ftodos.py
 * bin/ftolower           Convert filename to lowercase
 * bin/ftolower.bat
 * bin/ftolower.py
 * bin/ftomac             Converts file to "\r" newline format
 * bin/ftomac.bat
 * bin/ftomac.py
 * bin/ftouch             Modify access times of all files in directory recursively
 * bin/ftouch.bat
 * bin/ftouch.py
 * bin/ftounix            Converts file to "\n" newline format
 * bin/ftounix.bat
 * bin/ftounix.py
 * bin/ftoupper           Convert filename to uppercase
 * bin/ftoupper.bat
 * bin/ftoupper.py
 * bin/ftp ftp wrapper    (allowing non systems port)
 * bin/ftp.py
 * bin/fwatch             Watch file system events
 * bin/fwatch.py          (uses inotifywait)
 * bin/fwhich             Locate a program file
 * bin/fwhich.bat
 * bin/fwhich.py
 * bin/fwrapper           Create wrapper to run script/executable
 * bin/fwrapper.py
 * bin/fzero              Zero device or create zero file
 * bin/fzero.bat
 * bin/fzero.py
 * bin/gcc                GNU compiler wrappers (allowing non systems port)
 * bin/gcc.bat
 * bin/gcc.py
 * bin/g++
 * bin/g++.bat
 * bin/gxx\_.py
 * bin/gfortran
 * bin/gfortran.bat
 * bin/gfortran.py
 * bin/gedit              gedit wrapper (allowing non systems port)
 * bin/gedit.py
 * bin/gem                Wrapper to select "umask 022"
 * bin/gem.py
 * bin/getip              Get the IP number of hosts
 * bin/getip.bat
 * bin/getip.py
 * bin/geturl             Multi-threaded download accelerator
 * bin/geturl.py          (use aria2c)
 * bin/gimp               gimp wrapper (allowing non systems port)
 * bin/gimp.bat
 * bin/gimp.py
 * bin/git                git wrapper (allowing non systems port)
 * bin/git.bat
 * bin/git\_.py
 * bin/git-bash.bat       git bash shell for Windows
 * bin/gitk               gitk wrapper (allowing non systems port)
 * bin/gitk.bat
 * bin/gitk.py
 * bin/git-lfs            git large file storage plugin
 * bin/git\_lfs.py
 * bin/git-time           git original author time plugin
 * bin/git\_time.py
 * bin/gnomine            gnome-mines/gnomine wrapper (allowing non systems port)
 * bin/gnomine.py         (can pick using old gnomines name)
 * bin/go                 Go wrapper (golang)
 * bin/go.py
 * bin/google             Google search engine submission
 * bin/google.py
 * bin/gpg                gpg wrapper (allowing non systems port)
 * bin/gpg.py             (contains enhanced functions "gpg -h")
 * bin/gqview             gqview wrapper (allowing non systems port)
 * bin/gqview.bat         (uses gqview)
 * bin/gqview.py          (uses geeqie)
 * bin/graph              Generate multiple graph files with X/Y plots (uses gnuplot)
 * bin/graph.py
 * bin/gz                 Compress a file in GZIP format (allowing non systems port)
 * bin/gz.py
 * bin/halt               Fast shutdown using "/proc/sysrq-trigger"
 * bin/hardinfo           hardinfo wrapper (allowing non systems port)
 * bin/hardinfo.py
 * bin/helm               helm wrapper (for Kubernetes)
 * bin/helm.py
 * bin/htmlformat         HTML file re-formatter
 * bin/htmlformat.bat
 * bin/htmlformat.py
 * bin/httpd              Start a simple Python HTTP server
 * bin/httpd.bat
 * bin/httpd.py
 * bin/index              Produce "index.fsum" file and "..fsum" cache files
 * bin/index.bat
 * bin/index.py
 * bin/inkscape           inkscape wrapper (allowing non systems port)
 * bin/inkscape.py
 * bin/isitup             Checks whether a host is up
 * bin/isitup.bat
 * bin/isitup.py
 * bin/iso                Make a portable CD/DVD archive in ISO9660 format
 * bin/iso.py
 * bin/iterm              iTerm2 (allowing non systems port)
 * bin/iterm.py
 * bin/jar                jar wrapper (allowing non systems port)
 * bin/jar.py             (Java jar archiver)
 * bin/java               java wrapper (allowing non systems port)
 * bin/java.py            (Java run time)
 * bin/javac              javac wrapper (allowing non systems port)
 * bin/javac.py           (Java compiler)
 * bin/jpeg2ps            jpeg2ps wrapper (allowing non systems port)
 * bin/jpeg2ps.py
 * bin/jsformat           Javascript file re-formatter
 * bin/jsformat.bat
 * bin/jsformat.py
 * bin/json               Convert BSON/JSON/YAML to JSON
 * bin/json.bat
 * bin/json\_.py
 * bin/jsonformat         JSON file re-formatter
 * bin/jsonformat.bat
 * bin/jsonformat.py
 * bin/jython             Jython wrapper
 * bin/jython.py
 * bin/k3s                K3S light weight Kubernetes distribution
 * bin/k3s.py
 * bin/keymap.tcl         TCL/TK widget for setting keymaps
 * bin/kmodsign           Wrapper for Kernel's sign-file command
 * bin/kmodsign.py
 * bin/kubectl            kubectl wrapper (allowing non systems port)
 * bin/kubectl.bat
 * bin/kubectl.py
 * bin/kubeseal           kubeseal wrapper (allowing non systems port)
 * bin/kubeseal.py
 * bin/markdown           Markdown wrapper (for markdown_py)
 * bin/markdown.bat
 * bin/md5                Calculate MD5 checksums of files
 * bin/md5.bat
 * bin/md5.py
 * bin/md5cd              Calculate MD5 checksums for CD/DVD data disk
 * bin/md5cd.py
 * bin/meld               Meld wrapper (allowing non systems port)
 * bin/meld.bat
 * bin/meld.py
 * bin/menu               TCL/TK menu system
 * bin/menu.py            (this can be used independent of GNOME/KDE/XFCE menu system)
 * bin/menu.tcl.jinja2
 * bin/menu.yaml
 * bin/mget               M3U8 streaming video downloader
 * bin/mget.py
 * bin/mirror             Copy all files/directory inside a directory into mirror directory
 * bin/mirror.bat
 * bin/mirror.py
 * bin/mkcd               Make data/audio/video CD/DVD using CD/DVD writer
 * bin/mkcd.py            (uses wodim, icedax, cdrdao)
 * bin/mkpasswd           Create Create secure random password.
 * bin/mkpasswd.bat
 * bin/mkpasswd.py
 * bin/mksshkeys          Create SSH keys and setup access to remote systems
 * bin/mksshkeys.py
 * bin/mousepad           mousepad wrapper (allowing non systems port)
 * bin/mousepad.py        (XFCE editor)
 * bin/mp3                Encode MP3 audio using avconv (libmp3lame)
 * bin/mp3.py
 * bin/mp4                Encode MP4 video using avconv (libx264/aac)
 * bin/mp4.py
 * bin/mvn                mvn wrapper (allowing non systems port)
 * bin/mvn.py
 * bin/myqdel             MyQS personal batch system for each user
 * bin/myqdel.py
 * bin/myqexec
 * bin/myqexec.py
 * bin/myqsd
 * bin/myqsd.py
 * bin/myqstat
 * bin/myqstat.py
 * bin/myqsub
 * bin/myqsub.py
 * bin/nautilus           nautilus wrapper (allowing non systems port)
 * bin/nautilus.py
 * bin/netnice            Run a command with limited network bandwidth (uses trickle)
 * bin/netnice.py
 * bin/normalize          normalize wrapper (allowing non systems port)
 * bin/normalize.py
 * bin/ntpdate            Run daemon to update time once every 24 hours
 * bin/ntpdate.py
 * bin/ocr                Convert image file to text using OCR (uses tesseract)
 * bin/ocr.py
 * bin/offline            Run a command without network access
 * bin/offline.py
 * bin/ogg                Encode OGG audio using avconv (libvorbis)
 * bin/ogg.py
 * bin/open               Open files using hardwired application mapping
 * bin/open.py
 * bin/otool              otool wrapper (allowing non systems port)
 * bin/otool.py
 * bin/padman             World Of Padman (allowing non systems port)
 * bin/padman.py
 * bin/par2               par2 wrapper (allowing non systems port)
 * bin/par2.bat
 * bin/par2.py
 * bin/pause              Pause until user presses ENTER/RETURN key
 * bin/pause.bat
 * bin/pause.py
 * bin/pbsetup            pbsetup wrapper (allowing non systems port)
 * bin/pbsetup.py         (Punk Buster)
 * bin/pcheck             Check JPEG picture files
 * bin/pcheck.py
 * bin/pcunix.bat         Start PCUNIX on Windows
 * bin/pdf                Create PDF file from text/images/postscript/PDF files
 * bin/pdf.py
 * bin/pget               Picture downloader for Instagram website
 * bin/pget.py
 * bin/pidgin             Pidgin wrapper (allowing non systems port)
 * bin/pidgin.bat
 * bin/pidgin.py
 * bin/play               Play multimedia file/URL
 * bin/play.py            (uses vlc and ffprobe)
 * bin/phtml              Generate XHTML files to view pictures
 * bin/phtml.bat
 * bin/phtml.py
 * bin/plink              Create links to JPEG files
 * bin/plink.py
 * bin/pmeg               Resize large picture images to mega-pixels limit
 * bin/pmeg.py            (uses convert from ImageMagick)
 * bin/pnum               Renumber picture files into a numerical series
 * bin/pnum.bat
 * bin/pnum.py
 * bin/pop                Send popup message to display
 * bin/pop.jar            (uses Java)
 * bin/pop.py
 * bin/procexp            Windows procexp wrapper (allowing non systems port)
 * bin/procexp.bat
 * bin/procexp.py
 * bin/psame              Show picture files with same finger print
 * bin/psame.bat
 * bin/psame.py
 * bin/psum               Calculate checksum using imagehash, file size and file modification time
 * bin/psum.bat
 * bin/psum.py
 * bin/pyc                Compile Python source file to PYC file
 * bin/pyc.bat
 * bin/pyc.py
 * bin/pyld.sh            Python loading module for sh/ksh/bash wrapper scripts
 * bin/pyld.py            Load Python main program as module (must have Main class)
 * bin/test\_pyld.py       Unit testing suite for "pyld.py"
 * bin/pyprof             Profile Python 3.x program
 * bin/pyprof.bat
 * bin/pyprof.py
 * bin/pyz                Make a Python3 ZIP Application in PYZ format
 * bin/pyz.py
 * bin/qmail              Qwikmail, commandline E-mailer
 * bin/qmail.py
 * bin/random             Generate random integer from range.
 * bin/random.bat
 * bin/random\_.py
 * bin/readcd             Copy CD/DVD data as a portable ISO/BIN image file
 * bin/readcd.py
 * bin/robo3t             robo3t wrapper (allowing non systems port)
 * bin/robo3t.py
 * bin/ripcd              Rip CD audio tracks as WAVE sound files
 * bin/ripcd.py
 * bin/ripdvd             Rip Video DVD title to file
 * bin/ripdvd.py
 * bin/rpm                rpm wrapper (allowing non systems port)
 * bin/rpm.py
 * bin/run                Run a command immune to terminal hangups
 * bin/run.py
 * bin/say                Speak words using Google TTS engine
 * bin/say.py             (uses espeak)
 * bin/scp.bat            Windows scp wrapper (uses PuTTY)
 * bin/sdd                Securely backup/restore partitions using SSH protocol
 * bin/sdd.py
 * bin/sequence           Generate sequences with optional commas
 * bin/sequence.bat
 * bin/sequence.py
 * bin/sftp.bat           Windows sftp wrapper (uses PuTTY)
 * bin/shuffle            Print arguments in random order
 * bin/shuffle.bat
 * bin/shuffle.py
 * bin/skype              skype wrapper (allowing non systems port)
 * bin/skype.py
 * bin/smount             Securely mount a file system using SSH protocol
 * bin/smount.py          (uses fuse.sshfs)
 * bin/soffice            soffice wrapper (allowing non systems port)
 * bin/soffice.bat        (LibreOffice)
 * bin/soffice.py
 * bin/sqlplus            Sqlplus wrapper (for Oracle Instant Client)
 * bin/sqlplus.bat
 * bin/sqlplus.py
 * bin/sqlplus64
 * bin/sqlplus64.py
 * bin/sonobuoy           sonobuoy (allowing non systems port)
 * bin/sonobuoy.py
 * bin/ssh.bat            Windows ssh wrapper (uses PuTTY)
 * bin/ssync              Securely synchronize file system using SSH protocol
 * bin/ssync.py           (uses rsync)
 * bin/sudo               Wrapper for "sudo" command
 * bin/sudo.bat
 * bin/sudo.py
 * bin/ssudo
 * bin/ssudo.py
 * bin/sumount            Unmount file system securely mounted with SSH protocol
 * bin/sumount.py
 * bin/svncviewer         Securely connect to VNC server using SSH protocol
 * bin/svncviewer.py
 * bin/sysinfo            System configuration detection tool
 * bin/sysinfo.bat
 * bin/sysinfo.py
 * bin/sysinfo.sh         Old Bourne shell version
 * bin/systemd-analyze    systemd-analyze wrapper (filter buggy firmware/loader timings)
 * bin/systemd\_analyze.py
 * bin/t7z                Make a compressed archive in TAR.&Z format
 * bin/t7z.py
 * bin/tar                Make a compressed archive in TAR format
 * bin/tar.bat
 * bin/tar.py
 * bin/tar\_.py
 * bin/teams              teams wrapper (allowing non systems port)
 * bin/teams.py
 * bin/terraform          terraform wrapper (allowing non systems port)
 * bin/terraform.py
 * bin/tbz                Make a compressed archive in TAR.BZ2
 * bin/tbz.bat
 * bin/tbz.py
 * bin/tgz                Make a compressed archive in TAR.GZ format
 * bin/tgz.bat
 * bin/tgz.py
 * bin/thunderbird        thunderbird wrapper (allowing non systems port)
 * bin/thunderbird.bat
 * bin/thunderbird.py
 * bin/tiller             Tiller wrapper (for Kubernetes)
 * bin/tiller.py
 * bin/tinyproxy          tinyproxy wrapper (allowing non systems port)
 * bin/tinyproxy.py
 * bin/tkill              Kill tasks by process ID or name
 * bin/tkill.bat
 * bin/tkill.py
 * bin/tls                Show full list of files
 * bin/tls.bat
 * bin/tls.py
 * bin/tlz                Make a compressed archive in TAR.LZMA format
 * bin/tlz.py
 * bin/tmux               tmux wrapper (allowing non systems port)
 * bin/tmux.py
 * bin/tocapital          Print arguments wth first letter in upper case
 * bin/tocapital.bat
 * bin/tocapital.py
 * bin/tolower            Print arguments in lower case
 * bin/tolower.bat
 * bin/tolower.py
 * bin/top                top wrapper (allowing non systems port)
 * bin/top.py
 * bin/toupper            Print arguments in upper case
 * bin/toupper.bat
 * bin/toupper.py
 * bin/traceroute         traceroute wrapper (allowing non systems port)
 * bin/traceroute.bat
 * bin/traceroute.py
 * bin/twait              Wait for task to finish then launch command
 * bin/twait.bat
 * bin/twait.py
 * bin/txz                Make a compressed archive in TAR.XZ format
 * bin/txz.py
 * bin/un7z               Unpack a compressed archive in 7Z format
 * bin/un7z.bat
 * bin/un7z.py
 * bin/unace              Unpack a compressed archive in ACE format
 * bin/unace.py
 * bin/unbz2              Uncompress a file in BZIP2 format (allowing non systems port)
 * bin/unbz2.py
 * bin/undeb              Unpack a compressed archive in DEB format
 * bin/undeb.py
 * bin/undmg              Unpack a compressed DMG disk file
 * bin/undmg.py
 * bin/unetbootin         unetbootin wrapper (allowing non systems port)
 * bin/unetbootin.bat
 * bin/unetbootin.py
 * bin/ungpg              Unpack an encrypted archive in gpg (pgp compatible) format
 * bin/ungpg.py
 * bin/ungz               Uncompress a file in GZIP format (allowing non systems port)
 * bin/ungz.py
 * bin/uniso              Unpack a portable CD/DVD archive in ISO9660 format
 * bin/uniso.py
 * bin/unjar              Unpack a compressed JAVA archive in JAR format
 * bin/unjar.py
 * bin/unpdf              Unpack PDF file into series of JPG files
 * bin/unpdf.py
 * bin/unpyc              De-compile PYC file to Python source file
 * bin/unpyc.bat
 * bin/unpyc.py
 * bin/unrar              Unpack a compressed archive in RAR format
 * bin/unrar.py
 * bin/unrpm              Unpack a compressed archive in RPM format
 * bin/unrpm.py
 * bin/unsqlite           Unpack a sqlite database file
 * bin/unsqlite.py
 * bin/unt7z              Unpack a compressed archive in TAR.7Z format
 * bin/unt7z.py
 * bin/untar              Unpack a compressed archive in
 * bin/untar.bat          TAR/TAR.GZ/TAR.BZ2/TAR.LZMA/TAR.XZ/TAR.7Z/TGZ/TBZ/TLZ/TXZ format.
 * bin/untar.py
 * bin/untar\_.py
 * bin/untbz              Unpack a compressed archive in TAR.BZ2 format
 * bin/untbz.bat
 * bin/untbz.py
 * bin/untgz              Unpack a compressed archive in TAR.GZ format.
 * bin/untgz.bat
 * bin/untgz.py
 * bin/untlz              Unpack a compressed archive in TAR.LZMA format.
 * bin/untlz.py
 * bin/untxz              Unpack a compressed archive in TAR.XZ format
 * bin/untxz.py
 * bin/unwine             Shuts down WINE and all Windows applications
 * bin/unwine.py
 * bin/unxz               Uncompress a file in XZ format (allowing non systems port)
 * bin/unxz.py
 * bin/unzip              unzip wrapper (allowing non systems port)
 * bin/unzip.py
 * bin/urldecode          Decode URL query strings.
 * bin/urldecode.py
 * bin/ut                 Urban Terror (allowing non systems port))
 * bin/ut.py
 * bin/vbox               VirtualBox virtual machine manager
 * bin/vbox.py            (uses VBoxManage)
 * bin/vget               Streaming video downloader (Youtube, m3u8 and compatible websites)
 * bin/vget.py
 * bin/vi                 vi wrapper (allowing non systems port)
 * bin/vi.bat
 * bin/vim                vim wrapper (allowing non systems port)
 * bin/vim.bat
 * bin/vi.py
 * bin/view               View files using hardwired application mapping
 * bin/view.py
 * bin/vlc                vlc wrapper (allowing non systems port)
 * bin/vlc.bat
 * bin/vlc.py
 * bin/vmware             VMware Player launcher
 * bin/vmware.py
 * bin/vncpasswd          vncpasswd wrapper (allowing non systems port)
 * bin/vncpasswd.py
 * bin/vncserver          vncserver wrapper (allowing non systems port)
 * bin/vncserver.py
 * bin/vncviewer          vncviewer wrapper (allowing non systems port)
 * bin/vncviewer.bat
 * bin/vncviewer.py
 * bin/vplay              Play AVI/FLV/MP4 video files in directory.
 * bin/vplay.py           (uses vlc)
 * bin/warsow             Warsow (allowing non systems port)
 * bin/warsow.py
 * bin/wav                Encode WAV audio using avconv (pcm_s16le).
 * bin/wav.py
 * bin/wget               wget wrapper (allowing non systems port)
 * bin/wget.py            (bandwidth 512KB limit default using "trickle", "$HOME/.config/trickle.json)
 * bin/wine               wine wrapper (allowing non systems port)
 * bin/wine.py
 * bin/wine64             wine64 wrapper (allowing non systems port)
 * bin/wine64.py
 * bin/cmd
 * bin/weather            Current weather search
 * bin/weather.bat
 * bin/weather.py
 * bin/wipe               wipe wrapper (allowing non systems port)
 * bin/wipe.py            (wipe is C disk wiper)
 * bin/xcalc              Start GNOME/KDE/XFCE calculator
 * bin/xcalc.py
 * bin/xdesktop           Start GNOME/KDE/XFCE file manager
 * bin/xdesktop.py
 * bin/xdiff              Graphical file comparison and merge tool
 * bin/xdiff.bat          (uses meld)
 * bin/xdiff.py
 * bin/xfreerdp.tcl       XFreeRDP TCL/TK panel
 * bin/xedit              Start GNOME/KDE/XFCE graphical editor
 * bin/xedit.py
 * bin/xlight             Desktop screen backlight utility
 * bin/xlight.py
 * bin/xlock              Start GNOME/KDE/XFCE screen lock
 * bin/xlock.py
 * bin/xlogout            Shutdown X-windows
 * bin/xlogout.py
 * bin/xmail              Start E-mail in web browser
 * bin/xmail.py
 * bin/xmixer             Start GNOME/KDE/XFCE audio mixer
 * bin/xmixer.py
 * bin/xmlcheck           Check XML file for errors
 * bin/xmlcheck.bat
 * bin/xmlcheck.py
 * bin/xmlformat          XML file re-formatter
 * bin/xmlformat.bat
 * bin/xmlformat.py
 * bin/xournal            PDF annotator
 * bin/xournal.bat
 * bin/xournal.py
 * bin/xreset             Reset to default screen resolution
 * bin/xreset.py
 * bin/xrun               Run command in new terminal session
 * bin/xrun.py
 * bin/xrun.tcl
 * bin/xsnapshot          Start GNOME/KDE/XFCE screen snapshot
 * bin/xsnapshot.py
 * bin/xsudo              Run sudo command in new terminal session
 * bin/xsudo.py
 * bin/xterm              Start GNOME/KDE/XFCE/Invisible terminal session
 * bin/xterm.py
 * bin/xvolume            Desktop audio volume utility (uses pacmd)
 * bin/xvolume.py
 * bin/xweb               Start web browser
 * bin/xweb.py
 * bin/xz                 Compress a file in XZ format (allowing non systems port)
 * bin/xz.py
 * bin/yaml               Convert BSON/JSON/YAML to YAML
 * bin/yaml.bat
 * bin/yaml\_.py
 * bin/yping              Ping a host until a connection is made
 * bin/yping.bat
 * bin/yping.py
 * bin/zhspeak            Zhong Hua Speak, Chinese TTS software
 * bin/zhspeak.py
 * bin/zhspeak.tcl
 * bin/zip                zip wrapper (allowing non systems port)
 * bin/zip.py
 * bin/zoom               zoom wrapper (allowing non systems port)
 * bin/zoom.py
 * bin/cdinst.bat         Windows command prompt batch file or changing directory
 * bin/cdsrc.bat
 * bin/cdtest.bat
 * bin/mkinst.bat
 * bin/mksrc.bat
 * bin/mktest.bat
 * bin/scd.bat
 * config/Xresources                     Copy to "$HOME/.Xresources" to set xterm resources
 * config/accels                         Copy to "$HOME/.config/geeqie" for keyboard shortcuts
 * config/adblock.txt                    Adblock filter list
 * config/autoexec.sh                    Copy to "$HOME/.config/autoexec.sh" & add to desktop auto startup
 * config/autoexec-opt.sh                Copy to "$HOME/.config/autoexec-opt.sh" for optional settings
 * config/com.googlecode.iterm2.plist    Copy to "$HOME/Library/Preference" for iTerm2 on Mac
 * config/config                         Copy to "$HOME/.ssh/config"
 * config/geeqierc.xml                   Copy to "$HOME/.config/geeqie" for configuration
 * config/genmon-7.rc                    Copy to "$HOME/.config/xfce4/panel/genmon-7.rc" for XFCE Weather
 * config/gitconfig                      Copy to "$HOME/.gitconfig" and edit
 * config/htoprc                         Copy to "$HOME/.config/htoprc"
 * config/login                          Copy to "$HOME/.login" for csh/tcsh shells (translated ".profile")
 * config/mimeapps.list                  Copy to "$HOME/.local/share/applications" for Mime definitions
 * config/minttyrc                       Copy to "$HOME/.minttyrc" for MSYS2 terminal
 * config/tmux.conf                      Copy to "$HOME/.tmux.conf" fro TMUX terminal
 * config/profile                        Copy to "$HOME/.profile" for ksh/ash/bash shells settings
 * config/profile-opt                    Copy to "$HOME/.profile-optl" for optional ksh/bash shells settings
 * config/rc.local                       Copy to "/etc/rc.local" for system startup commands
 * config/rc.local-opt                   Copy to "/etc/rc.local-opt" for optional system startup commands
 * config/terminalrc                     Copy to "$HOME/.config/xfce4/terminal" for XFCE terminal
 * config/vimrc                          Copy to "$HOME/.vimrc" for VIM defaults
 * config/userapp-gqview.desktop         Copy to "$HOME/.local/share/applications" for Geeqie
 * config/userapp-soffice.desktop        Copy to "$HOME/.local/share/applications" for LibreOffice
 * config/userapp-vlc.desktop            Copy to "$HOME/.local/share/applications" for VLC
 * config/winsetup.bat                   Configure Windows VirtualBox VMs
 * config/winsetupo.sh
 * config/xscreensaver                   Copy to "$HOME/.xscreensaver" for XScreenSaver defaults
 * etc/install-python-requirements.sh    Python pip installer (installs minimum requirements)
 * etc/python-requirements.txt           Python default pip requirements file
 * etc/python-requirements\_2.7.txt       Python 2.7 pip requirements file
 * etc/python-requirements\_3.5.txt       Python 3.5 pip requirements file
 * etc/python-requirements\_3.6.txt       Python 3.6 pip requirements file
 * etc/python-requirements\_3.9.txt       Python 3.9 pip requirements file
 * etc/setbin                            Hybrid Bourne/C-shell script for sh/ksh/bash/csh/tcsh initialization
 * etc/setbin.bat                        Windows Command prompt initialization
 * etc/setbin.ps1                        Windows Power shell initialization
 * ansible/Makefile                      Ansible local hosts playbook
 * ansible/ansible.cfg
 * ansible/inventory/group\_vars/all
 * ansible/inventory/group\_vars/local-hosts
 * ansible/inventory/local-hosts
 * ansible/roles/system-config/tasks/etc-files.yml
 * ansible/roles/system-config/tasks/main.yml
 * ansible/roles/system-config/tasks/root-home.yml
 * ansible/roles/user-config/tasks/main.yml
 * ansible/roles/user-config/tasks/mimeapps-config.yml
 * ansible/roles/user-config/tasks/ssh-config.yml
 * ansible/roles/user-config/tasks/user-home.yml
 * ansible/roles/user-config/vars/main.yml
 * ansible/setup-local.yml
 * cloudformation/1pxy/1pxy.json         CloudFormation: 1pxy example
 * cloudformation/1pxy/Makefile
 * cloudformation/1pxy/submit.sh
 * cloudformation/multi-stacks/Makefile  CloudFormation: multi-stacks example
 * cloudformation/multi-stacks/main\_stack.json
 * cloudformation/multi-stacks/pxy\_stack.json
 * cloudformation/multi-stacks/sg\_stack.json
 * cloudformation/multi-stacks/submit.sh
 * cookiecutter/Makefile                 Makefile for building examples
 * cookiecutter/docker/cookiecutter.json
 * cookiecutter/docker/{{cookiecutter.project\_name}}/Dockerfile
 * cookiecutter/docker/{{cookiecutter.project\_name}}/Makefile
 * docker/Makefile                       Makefile for building all images
 * docker/bin/bash2ash
 * docker/bin/create-python-requirements
 * docker/bin/create-root-tar
 * docker/bin/docker-load                Load docker images
 * docker/bin/docker-save                Save docker images
 * docker/alpine-3.11/Dockerfile
 * docker/alpine-3.11/Makefile           alpine:3.11 based linux
 * docker/alpine-3.11/bash/Dockerfile
 * docker/alpine-3.11/bash/Makefile      alpine:3.11 based BASH login
 * docker/alpine-3.11/dev/Dockerfile
 * docker/alpine-3.11/dev/Makefile       alpine:3.11 based linux
 * docker/alpine-3.12/Makefile
 * docker/alpine-3.12/Dockerfile         alpine:3.12 based linux
 * docker/alpine-3.12/bash/Makefile
 * docker/alpine-3.12/bash/Dockerfile    alpine:3.12 based BASH login
 * docker/alpine-3.12/dev/Makefile
 * docker/alpine-3.12/dev/Dockerfile     alpine:3.12 based GCC dev shell
 * docker/i386-alpine-3.12/Makefile
 * docker/i386-alpine-3.12/Dockerfile    i386/alpine:3.12 based linux
 * docker/i386-alpine-3.12/bash/Makefile
 * docker/i386-alpine-3.12/bash/Dockerfile  i386/alpine:3.12 based BASH login
 * docker/i386-alpine-3.12/dev/Makefile
 * docker/i386-alpine-3.12/dev/Dockerfile  i386/alpine:3.12 based GCC dev shell
 * docker/amazonlinux-2/Dockerfile
 * docker/amazonlinux-2/Makefile         amazonlinux:2 based linux
 * docker/amazonlinux-2/bash/Dockerfile
 * docker/amazonlinux-2/bash/Makefile    amazonlinux:2 based BASH login
 * docker/amazonlinux-2/dev/Dockerfile
 * docker/amazonlinux-2/dev/Makefile     amazonlinux:2 based GCC dev shell
 * docker/busybox-1.31/Dockerfile
 * docker/busybox-1.31/Makefile          busybox:1.31 based linux
 * docker/busybox-1.31/bash/Dockerfile
 * docker/busybox-1.31/bash/Makefile     busybox:1.31 based BASH login
 * docker/centos-7/Dockerfile
 * docker/centos-7/Makefile              centos:7 based linux
 * docker/centos-7/bash/Dockerfile
 * docker/centos-7/bash/Makefile         centos:7 based BASH login
 * docker/centos-7/dev/Dockerfile
 * docker/centos-7/dev/Makefile          centos:7 based GCC dev shell
 * docker/centos-8/Dockerfile
 * docker/centos-8/Makefile              centos:8 based linux
 * docker/centos-8/bash/Dockerfile
 * docker/centos-8/bash/Makefile         centos:8 based BASH login
 * docker/centos-8/dev/Dockerfile
 * docker/centos-8/dev/Makefile          centos:8 based GCC dev shell
 * docker/clearlinux-latest/Dockerfile
 * docker/clearlinux-latest/Makefile     clearlinux:latest based linux
 * docker/clearlinux-latest/bash/Makefile  clearlinux:latest based BASH login
 * docker/clearlinux-latest/bash/Dockerfile
 * docker/clearlinux-latest/dev/Makefile  clearlinux:latest based CLANG dev shell
 * docker/clearlinux-latest/dev/Dockerfile
 * docker/debian-9-slim/Dockerfile
 * docker/debian-9-slim/Makefile         debian:9-slim based linux
 * docker/debian-9-slim/bash/Dockerfile
 * docker/debian-9-slim/bash/Makefile    debian:9-slim based BASH login
 * docker/debian-9-slim/dev/Dockerfile
 * docker/debian-9-slim/dev/Makefile     debian:9-slim based GCC dev shell
 * docker/debian-10-slim/Dockerfile
 * docker/debian-10-slim/Makefile        debian:10-slim based linux
 * docker/debian-10-slim/bash/Dockerfile
 * docker/debian-10-slim/bash/Makefile   debian:10-slim based BASH login
 * docker/debian-10-slim/dev/Dockerfile
 * docker/debian-10-slim/dev/Makefile    debian:10-slim based GCC dev shell
 * docker/debian-10-slim/xfce/Dockerfile
 * docker/debian-10-slim/xfce/Makefile    debian:10-slim based XFCE environment
 * docker/debian-10-slim/xfce/files/docker-init
 * docker/debian-10-slim/xfce/files/xstartup
 * docker/i386-debian-10-slim/Dockerfile
 * docker/i386-debian-10-slim/Makefile    i386/debian:10-slim based linux
 * docker/i386-debian-10-slim/bash/Dockerfile
 * docker/i386-debian-10-slim/bash/Makefile  i386/debian:10-slim based BASH login
 * docker/i386-debian-10-slim/dev/Dockerfile
 * docker/i386-debian-10-slim/dev/Makefile  i386/debian:10-slim based GCC dev shell
 * docker/docker-19.03/Dockerfile
 * docker/docker-19.03/Makefile          docker:19.03 (alpine) based docker shell
 * docker/golang-1.14-alpine/Dockerfile
 * docker/golang-1.14-alpine/Makefile    golang:1.14-alpine based compiler app
 * docker/nginx-1.16-alpine/Dockerfile
 * docker/nginx-1.16-alpine/Makefile     nginx:1.16-alpine based revere proxy server
 * docker/nginx-1.16-alpine/files/nginx-proxy.conf  Proxy pass examples
 * docker/oraclelinux-7-slim/Dockerfile
 * docker/oraclelinux-7-slim/Makefile    oraclelinux:7-slim based linux
 * docker/oraclelinux-7-slim/bash/Dockerfile
 * docker/oraclelinux-7-slim/bash/Makefile  oraclelinux:7-slim based BASH login
 * docker/oraclelinux-7-slim/dev/Dockerfile
 * docker/oraclelinux-7-slim/dev/Makefile  oraclelinux:7-slim based GCC dev shell
 * docker/oraclelinux-8-slim/Dockerfile
 * docker/oraclelinux-8-slim/Makefile    oraclelinux:8-slim based linux
 * docker/oraclelinux-8-slim/bash/Dockerfile
 * docker/oraclelinux-8-slim/bash/Makefile  oraclelinux:8-slim based BASH login
 * docker/oraclelinux-8-slim/dev/Dockerfile
 * docker/oraclelinux-8-slim/dev/Makefile  oraclelinux:8-slim based GCC dev shel
 * docker/python-3.7-slim-buster/Dockerfile
 * docker/python-3.7-slim-buster/Makefile  python:3.7-slim-buster based Python app
 * docker/python-3.7-slim-buster/bash/Dockerfile
 * docker/python-3.7-slim-buster/bash/Makefile  python:3.7-slim-buster based BASH login
 * docker/python-3.7-slim-buster/dev/Dockerfile
 * docker/python-3.7-slim-buster/dev/Makefile  python:3.7-slim-buster based dev shell
 * docker/python-3.7-slim-buster/devpi/Dockerfile
 * docker/python-3.7-slim-buster/devpi/Makefile  python:3.7-slim-buster based devpi server app
 * docker/registry-2.6/Dockerfile
 * docker/registry-2.6/Makefile          registry:2.6 based Docker Registry server app
 * docker/registry-2.6/files/config.yml
 * docker/sudo/Dockerfile
 * docker/sudo/Makefile                  sudo scratch image for jail breaking app
 * docker/ubuntu-16.04/Makefile
 * docker/ubuntu-16.04/Dockerfile        ubuntu:16.04 based linux
 * docker/ubuntu-16.04/bash/Makefile
 * docker/ubuntu-16.04/bash/Dockerfile   ubuntu:16.04 based BASH login
 * docker/ubuntu-16.04/dev/Makefile
 * docker/ubuntu-16.04/dev/Dockerfile    ubuntu:16.04 based GCC dev shell
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
 * kubernetes/Makefile
 * kubernetes/bin/kube-connect           Connect to Kubernetes ingress/service port
 * kubernetes/bin/kube-save              Save Kubernetes control plane docker images
 * kubernetes/monitor-host/Makefile      Kubernetes: host monitoring (drtuxwang/debian-bash:stable)
 * kubernetes/monitor-host/monitor-host-daemonset.yaml
 * kubernetes/test-crontab/Makefile      Kubernetes: crontab example (drtuxwang/busybox-bash:stable)
 * kubernetes/test-crontab/batch-crontab.yaml
 * kubernetes/test-servers/Makefile      Kubernetes: examples (drtuxwang/debian-bash:stable)
 * kubernetes/test-servers/server-pod.yaml
 * kubernetes/test-servers/servers-daemonset.yaml
 * kubernetes/test-servers/servers-deployment.yaml
 * kubernetes/test-servers/servers-headless-service.yaml
 * kubernetes/test-servers/servers-ingress.yaml
 * kubernetes/test-servers/servers-replicationcontroller.yaml
 * kubernetes/test-servers/servers-secret-tls.yaml
 * kubernetes/test-servers/servers-service.yaml
 * kubernetes/test-servers/servers-statefulset.yaml
 * helm/Makefile
 * helm/bin/helm-save                    Save Helm release docker images
 * helm/chartmuseum/Makefile             Helm Chart: stable/chartmuseum 2.14.2 (app-0.12.0)
 * helm/chartmuseum/values.yaml
 * helm/concourse/Makefile               Helm Chart: concourse/concourse 14.5.5 (app-6.7.5)
 * helm/concourse/concourse-secrets.yaml
 * helm/concourse/values.yaml
 * helm/etcd/Makefile                    Helm Chart: bitnami/etcd 4.11.1 (app-3.4.13)
 * helm/etcd/values.yaml
 * helm/grafana/Makefile                 Helm Chart: bitnami/grafana 3.4.5 (app-7.2.2)
 * helm/grafana/values.yaml
 * helm/jenkins/Makefile                 Helm Chart: bitnami/jenkins 5.0.28 (app-2.249.3)
 * helm/jenkins/values.yaml
 * helm/kafka/Makefile                   Helm Chart: bitnami/kafka 11.7.2 (app-2.5.0)
 * helm/kafka/connect-test.sh
 * helm/kafka/values.yml
 * helm/ingress-controller/Makefile      Helm Chart: ingress-nginx/ingress-nginx 2.12.1 (app-0.34.1)
 * helm/ingress-controller/values.yaml
 * helm/mongodb/Makefile                 Helm Chart: bitnami/mongodb 8.3.2 (app-4.2.9)
 * helm/mongodb/values.yml
 * helm/nexus/Makefile                   Helm Chart: oteemo/sonatype-nexus 4.1.2 (app-3.27.0)
 * helm/nexus/values.yaml
 * helm/nginx/Makefile                   Helm Chart: bitnami/nginx 8.5.5 (app-1.16.1)
 * helm/nginx/values.yaml
 * helm/ops-server/Makefile              Helm Chart: drtuxwang/ops-server (drtuxwang/debian-bash:stable)
 * helm/ops-server/drtuxwang/ops-server/Chart.yaml
 * helm/ops-server/drtuxwang/ops-server/templates/\_helpers.tpl
 * helm/ops-server/ops-server/templates/box-deployment.yaml
 * helm/ops-server/values.yaml
 * helm/oracle-xe/Makefile               Helm Chart: Oracle XE test (datagrip/oracle:11.2)
 * helm/oracle-xe/oracle-xe/Chart.yaml
 * helm/oracle-xe/oracle-xe/templates/\_helpers.tpl
 * helm/oracle-xe/oracle-xe/templates/box-headless-service.yaml
 * helm/oracle-xe/oracle-xe/templates/box-service.yaml
 * helm/oracle-xe/oracle-xe/templates/box-statefulset.yaml
 * helm/oracle-xe/values.yaml
 * helm/prometheus/Makefile              Helm Chart: prometheus-community/prometheus 11.14.1 (app-2.20.1)
 * helm/prometheus/values.yaml
 * helm/pushgateway/Makefile             Helm Chart: prometheus-community/prometheus-pushgateway 1.4.2 (app-1.2.0)
 * helm/pushgateway/values.yaml
 * helm/rabbitmq/Makefile                Helm Chart: bitnami/rabbitmq 6.8.3 (app-3.7.19)
 * helm/rabbitmq/values.yaml
 * helm/test-server/Makefile             Helm Chart: drtuxwang/test-server (drtuxwang/debian-bash:stable)
 * helm/test-server/drtuxwang/test-server/Chart.yaml
 * helm/test-server/drtuxwang/test-server/requirements.lock
 * helm/test-server/drtuxwang/test-server/requirements.yaml
 * helm/test-server/drtuxwang/test-server/templates/\_helpers.tpl
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
 * helm/xfce-server/drtuxwang/xfce-server/templates/\_helpers.tpl
 * helm/xfce-server/xfce-server/templates/box-headless-service.yaml
 * helm/xfce-server/xfce-server/templates/box-service.yaml
 * helm/xfce-server/xfce-server/templates/box-statefulset.yaml
 * python/simple-cython/Makefile         Simple Cython example
 * python/simple-cython/cython\_example.pyx
 * python/simple-cython/run.py
 * python/simple-flask/Makefile          Simple Flask demo
 * python/simple-flask/simple\_flask.py
 * python/simple-flask/templates/hello.html
 * python/simple-package/Makefile        Simple Egg & WHL package
 * python/simple-package/run.py
 * python/simple-package/setup.py
 * python/simple-package/hello/\_\_init\_\_.py
 * python/simple-package/hello/message.py
 * python/simple-tornado/Makefile        Tornado examples
 * python/simple-tornado/tornado\_client.py
 * python/simple-tornado/tornado\_server.py
 * terraform-aws/1pxy/aws\_config.tf      Terraform AWS: 1pxy example
 * terraform-aws/1pxy/aws\_resources.tf
 * terraform-aws/1pxy/pxy\_resources.tf
 * terraform-aws/1pxy/pxy\_variables.tf
 * terraform-aws/pxy-as/aws\_config.tf    Terraform AWS: pxy-as example
 * terraform-aws/pxy-as/aws\_resources.tf
 * terraform-aws/pxy-as/pxy\_resources.tf
 * terraform-aws/pxy-as/pxy\_variables.tf
```
