#!/usr/bin/env python3
"""
Download http/https/ftp/file URLs.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import json
import os
import signal
import socket
import time
import urllib.request

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._parseArgs(args[1:])


    def getUrls(self):
        """
        Return list of urls.
        """
        return self._args.urls


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Download http/https/ftp/file URLs.")

        parser.add_argument("urls", nargs="+", metavar="url", help="http/https/ftp/file URL.")

        self._args = parser.parse_args(args)


class Download(syslib.Dump):


    def __init__(self, options):
        self._chunkSize = 131072
        self._urls = options.getUrls()


    def _checkFile(self, file, size, mtime):
        """
        Check existing file and return True if already downloaded.
        """
        fileStat = syslib.FileStat(file)
        if fileStat.getSize() == size and fileStat.getTime() >= mtime:
            return True
        return False


    def _getFileStat(self, url, conn):
        """
        url  = URL to download
        conn = http.client.HTTPResponse class object

        Returns (filename, size, time) tuple.
        """
        info = conn.info()

        try:
            mtime = time.mktime(time.strptime(
                    info.get("Last-Modified"), "%a, %d %b %Y %H:%M:%S %Z"))
        except TypeError:
            # For directories
            file = "index.html"
            if os.path.isfile(file):
                file = "index-" + str(os.getpid()) + ".html"
            mtime = time.time()
        else:
            file = os.path.basename(url)

        try:
            size = int(info.get("Content-Length"))
        except TypeError:
            size = -1

        return (file, size, mtime)


    def _checkResume(self, file, data):
       """
       Return "resume" or "skip" or "download"
       """
       try:
           with open(file + ".part.json") as ifile:
               jsonData = json.load(ifile)
               host = jsonData["fget"]["lock"]["host"]
               pid = jsonData["fget"]["lock"]["pid"]

               if host == syslib.info.getHostname() and syslib.Task().haspid(pid):
                   return("skip")
               if jsonData["fget"]["data"] == data:
                   return "resume"
       except (IOError, KeyError):
           pass

       return "download"


    def _writeResume(self, file, data):
       jsonData = {
                      "fget": {
                          "lock": {
                              "host": syslib.info.getHostname(),
                              "pid": os.getpid()
                          },
                          "data": data
                      }
                  }

       try:
           with open(file+".part.json", "w", newline="\n") as ofile:
               print(json.dumps(jsonData, indent=4, sort_keys=True), file=ofile)
       except IOError:
           pass


    def _getUrl(self, url):
        print(url)

        try:
            conn = urllib.request.urlopen(url)
            file, size, mtime = self._getFileStat(url, conn)
            if self._checkFile(file, size, mtime):
                print("  => {0:s} [{1:d}/{2:d}]".format(file, size, size))
                return
            tmpfile = file + ".part"

            data = { "size": size, "time": int(mtime) }
            check = self._checkResume(file, data)

            if check == "skip":
                return
            elif "Accept-Ranges" in conn.info().keys() and check == "resume":
                tmpsize = syslib.FileStat(file + ".part").getSize()
                req = urllib.request.Request(url, headers={"Range": "bytes="+str(tmpsize)+"-"})
                conn = urllib.request.urlopen(req)
                mode = "ab"
            else:
                tmpsize = 0
                mode = "wb"

            self._writeResume(file, data)

            try:
                with open(tmpfile, mode) as ofile:
                    while True:
                        chunk = conn.read(self._chunkSize)
                        if not chunk:
                            break
                        tmpsize += len(chunk)
                        ofile.write(chunk)
                        print("\r  => {0:s} [{1:d}/{2:d}]".format(file, tmpsize, size), end="")
            except PermissionError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' + file + '" file.')
            print()

            os.utime(tmpfile, (mtime, mtime))
            try:
                os.rename(tmpfile, file)
                os.remove(tmpfile + ".json")
            except OSError:
                pass

        except urllib.error.URLError as exception:
            reason = exception.reason
            if type(reason) == socket.gaierror:
                raise SystemExit(sys.argv[0] + ": " + reason.args[1] +".")
            elif "Not Found" in reason:
                raise SystemExit(sys.argv[0] + ": 404 Not Found.")
            elif "Permission denied" in reason:
                raise SystemExit(sys.argv[0] + ": 550 Permission denied.")
            else:
                raise SystemExit(sys.argv[0] + ": " + exception.args[0])
        except ValueError as exception:
            raise SystemExit(sys.argv[0] + ": " + exception.args[0])


    def run(self):
        for url in self._urls:
            self._getUrl(url)


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Download(options).run()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)


    def _signals(self):
        if hasattr(signal, "SIGPIPE"):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)


    def _windowsArgv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg) # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == "__main__":
    if "--pydoc" in sys.argv:
        help(__name__)
    else:
        Main()
