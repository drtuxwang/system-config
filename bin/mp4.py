#!/usr/bin/env python3
"""
Encode MP4 video using avconv (libx264/aac).
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import re
import signal

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._parseArgs(args[1:])

        self._audioCodec = "aac"
        self._videoCodec = "libx264"


    def getAudioCodec(self):
        """
        Return audio codec.
        """
        return self._audioCodec


    def getAudioQuality(self):
        """
        Return audio quality.
        """
        return self._args.audioQuality[0]


    def getAudioVolume(self):
        """
        Return audio volume.
        """
        return self._args.audioVolume[0]


    def getFiles(self):
        """
        Return list of files.
        """
        return self._files


    def getFileNew(self):
        """
        Return new file location.
        """
        return self._fileNew


    def getFlags(self):
        """
        Return extra flags
        """
        return self._args.flags


    def getNoskipFlag(self):
        """
        Return noskip flag.
        """
        return self._args.noskipFlag


    def getRunTime(self):
        """
        Return run time.
        """
        return self._args.runTime[0]


    def getStartTime(self):
        """
        Return start time.
        """
        return self._args.startTime[0]


    def getThreads(self):
        """
        Return threads.
        """
        return self._args.threads[0]


    def getVideoCodec(self):
        """
        Return video codec.
        """
        return self._args.videoCodec[0]


    def getVideoCrop(self):
        """
        Return video cropping.
        """
        return self._args.videoCrop[0]


    def getVideoQuality(self):
        """
        Return video quality.
        """
        return self._args.videoQuality[0]


    def getVideoRate(self):
        """
        Return video rate.
        """
        return self._args.videoRate[0]


    def getVideoSize(self):
        """
        Return video size.
        """
        return self._args.videoSize[0]


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Encode MP4 video using avconv (libx264/aac).")

        parser.add_argument("-noskip", dest="noskipFlag", action="store_true",
                            help="Disable skipping of encoding when codecs same.")
        parser.add_argument("-vq", nargs=1, dest="videoQuality", default=[ None ],
                            help="x264 quality (0=loseless, 51=worse). Default is 23.")
        parser.add_argument("-vfps", nargs=1, dest="videoRate",default=[ None ],
                            help="Select frames per second.")
        parser.add_argument("-vcrop", nargs=1, dest="videoCrop",default=[ None ], metavar="w:h:x:y",
                            help="Crop video to W x H with x, y offset from top left.")
        parser.add_argument("-vsize", nargs=1, dest="videoSize", default=[ None ], metavar="x:y",
                            help="Resize video to width:height in pixels.")
        parser.add_argument("-aq", nargs=1, dest="audioQuality", default=[ None ],
                            help="Select audio bitrate in kbps (128kbps default).")
        parser.add_argument("-avol", nargs=1, dest="audioVolume", default=[ None ],
                            help='Select audio volume adjustment in dB (ie "-5", "5").')
        parser.add_argument("-start", nargs=1, dest="startTime", default=[ None ],
                            help="Start encoding at time n seconds.")
        parser.add_argument("-time", nargs=1, dest="runTime", default=[ None ],
                            help="Stop encoding after n seconds.")
        parser.add_argument("-threads", nargs=1, default=[ "2" ],
                            help="Threads are faster but decrease quality. Default is 2.")
        parser.add_argument("-flags", nargs=1, default=[],
                            help='Supply additional flags to avconv.')

        parser.add_argument("files", nargs="+", metavar="file",
                            help='Multimedia file. A target ".mp4" file can '
                                 'be given as the first file.')

        self._args = parser.parse_args(args)

        if self._args.files[0].endswith(".mp4"):
            self._fileNew = self._args.files[0]
            self._files = self._args.files[1:]
            if self._fileNew in self._args.files[1:]:
                raise SystemExit(sys.argv[0] + ": The input and output files must be different.")
        else:
            self._fileNew = ""
            self._files = self._args.files


class Encoder(syslib.Dump):


    def __init__(self, options):
        self._options = options
        self._avconv = syslib.Command("avconv", flags=options.getFlags())
        self._tempfiles = []


    def run(self):
        if self._options.getFileNew():
            print()
            if self._allImages(self._options.getFiles()):
                self._configImages(self._options.getFiles())
                self._avconv.extendArgs([ "-f", "mp4", "-y", self._options.getFileNew() ])
                self._run()
            else:
                if len(self._options.getFiles()) == 1:
                    self._config(self._options.getFiles()[0])
                else:
                    extension = "-tmpfile" + str(os.getpid()) + ".ts"
                    for file in self._options.getFiles():
                        media = self._config(file)
                        if media.hasVideo():
                            self._avconv.extendArgs([ "-bsf:v", "h264_mp4toannexb" ])
                        self._avconv.extendArgs([ "-f", "mpegts", "-y", file + extension ])
                        self._tempfiles.append(file + extension)
                        self._run()
                    self._avconv.setArgs([ "-i", "concat:" + "|".join(self._tempfiles),
                                           "-c", "copy" ])
                    if media.hasAudio():
                        self._avconv.extendArgs([ "-bsf:a", "aac_adtstoasc" ])
                if self._options.getStartTime():
                    self._avconv.extendArgs([ "-ss", self._options.getStartTime() ])
                if self._options.getRunTime():
                    self._avconv.extendArgs([ "-t", self._options.getRunTime() ])
                self._avconv.extendArgs([ "-metadata", "title=", "-f", "mp4", "-y",
                                          self._options.getFileNew() ])
                self._run()
            Media(self._options.getFileNew()).print()
        else:
            for file in self._options.getFiles():
                if not file.endswith(".mp4"):
                    print()
                    if self._allImages([ file ]):
                        self._configImages([ file ])
                    else:
                        self._config(file)
                        if self._options.getStartTime():
                            self._avconv.extendArgs([ "-ss", self._options.getStartTime() ])
                        if self._options.getRunTime():
                            self._avconv.extendArgs([ "-t", self._options.getRunTime() ])
                    fileNew = file.rsplit(".", 1)[0] + ".mp4"
                    self._avconv.extendArgs([ "-f", "mp4", "-y", fileNew ])
                    self._run()
                    Media(fileNew).print()


    def _config(self, file):
        media = Media(file)
        self._avconv.setArgs([ "-i", file ])

        if media.hasVideo():
            if (not media.hasVideoCodec("h264") or self._options.getVideoCrop() or
                    self._options.getVideoRate() or self._options.getVideoQuality() or
                    self._options.getVideoSize() or self._options.getNoskipFlag()):
                self._avconv.extendArgs([ "-c:v", self._options.getVideoCodec(),
                                          "-subq", "10", "-trellis", "2" ])
                if self._options.getVideoQuality():
                    self._avconv.extendArgs([ "-crf:v", self._options.getVideoQuality() ])
                else:
                    self._avconv.extendArgs([ "-crf:v", "23" ])
                if self._options.getVideoRate():
                    self._avconv.extendArgs([ "-r:v", self._options.getVideoRate() ])
                if self._options.getVideoCrop():
                    self._avconv.extendArgs([ "-vf", "crop=" + self._options.getVideoCrop() ])
                if self._options.getVideoSize():
                    self._avconv.extendArgs([ "-vf", "scale=" + self._options.getVideoSize() ])
            else:
                self._avconv.extendArgs([ "-c:v", "copy" ])

        if media.hasAudio:
            if (not media.hasAudioCodec("aac") or self._options.getAudioQuality() or
                    self._options.getAudioVolume() or self._options.getNoskipFlag()):
                self._avconv.extendArgs([ "-c:a", self._options.getAudioCodec() ])
                if self._options.getAudioQuality():
                    self._avconv.extendArgs([ "-b:a", self._options.getAudioQuality() + "K" ])
                else:
                    self._avconv.extendArgs([ "-b:a", "128K" ])
                if self._options.getAudioVolume():
                    self._avconv.extendArgs([ "-af",
                                              "volume=" + self._options.getAudioVolume() + "dB" ])
                self._avconv.extendArgs([ "-strict", "experimental" ]) # Required for "aac" audio
            else:
                self._avconv.extendArgs([ "-c:a", "copy" ])

        if self._options.getStartTime():
            self._avconv.extendArgs([ "-ss", self._options.getStartTime() ])
        if self._options.getRunTime():
            self._avconv.extendArgs([ "-t", self._options.getRunTime() ])
        self._avconv.extendArgs([ "-threads", self._options.getThreads() ] +
                                  self._options.getFlags())
        return media


    def _configImages(self, files):
        convert = syslib.Command("convert")
        extension = "-tmpfile" + str(os.getpid()) + ".png"
        frame = 0
        for file in files:
            frame += 1
            tmpfile = "frame{0:08d}".format(frame) + extension
            self._tempfiles.append(tmpfile)
            convert.setArgs([ file, tmpfile ])
            convert.run()
        if self._options.getVideoRate():
            self._avconv.setArgs([ "-r", self._options.getVideoRate() ])
        else:
            self._avconv.setArgs([ "-r", "2" ])
        self._avconv.extendArgs([ "-i", "frame%8d" + extension, "-c:v",
                                  self._options.getVideoCodec(), "-pix_fmt", "yuv420p" ])
        if self._options.getVideoCrop():
            self._avconv.extendArgs([ "-vf", "crop=" + self._options.getVideoCrop() ])
        if self._options.getVideoSize():
            self._avconv.extendArgs([ "-vf", "scale=" + self._options.getVideoSize() ])
        else:
            convert.setArgs([ "-verbose", tmpfile, "/dev/null" ])
            convert.run(mode="batch")
            try:
                # Must be multiple of 2 in x and y resolutions
                x, y = convert.getOutput()[0].split()[2].split("x")
                self._avconv.extendArgs([ "-vf", "scale=" + str(int(int(x)/2)*2) + ":" +
                                          str(int(int(y)/2)*2) ])
            except (IndexError, ValueError):
                pass
        if self._options.getStartTime():
            self._avconv.extendArgs([ "-ss", self._options.getStartTime() ])
        if self._options.getRunTime():
            self._avconv.extendArgs([ "-t", self._options.getRunTime() ])
        self._avconv.extendArgs([ "-threads", "1" ] + self._options.getFlags())


    def __del__(self):
        for file in self._tempfiles:
            try:
                os.remove(file)
            except OSError:
                pass


    def _allImages(self, files):
        for file in files:
            extension = file.split(".")[-1]
            if extension not in ( "bmp", "gif", "jpg", "jpeg", "png", "tif", "tiff" ):
                return False
        return True


    def _run(self):
        child = self._avconv.run(mode="child", error2output=True)
        line = ""
        ispattern = re.compile("^$| version |^ *(built |configuration:|lib|Metadata:|Duration:|"
                               "compatible_brands:|Stream|concat:|Program|service|lastkeyframe)|"
                               "^(In|Out)put | : |^Press|^Truncating|bitstream (filter|malformed)|"
                               "Buffer queue|buffer underflow|message repeated|^\[|p11-kit:")
        init = False

        while True:
            byte = child.stdout.read(1)
            line += byte.decode("utf-8", "ignore")
            if not byte:
                break
            if byte in ( b"\n", b"\r" ):
                if not ispattern.search(line):
                    sys.stdout.write(line)
                    sys.stdout.flush()
                line = ""
            elif byte == b"\r":
                sys.stdout.write(line)
                line = ""

        if not ispattern.search(line):
            print(line)
        exitcode = child.wait()
        if exitcode:
            sys.exit(exitcode)


class Media(syslib.Dump):


    def __init__(self, file):
        self._file = file
        self._length = "0"
        self._stream = {}
        self._type = "Unknown"
        avprobe = syslib.Command("avprobe", args=[ file ])
        avprobe.run(mode="batch", error2output=True)
        number = 0
        isjunk = re.compile("^ *Stream #[^ ]*: ")
        try:
            for line in avprobe.getOutput():
                if line.strip().startswith("Duration:"):
                    self._length = line.replace(",", "").split()[1]
                elif line.strip().startswith("Stream #0"):
                    self._stream[number] = isjunk.sub("", line)
                    number += 1
                elif line.strip().startswith("Input #"):
                    self._type = line.replace(", from", "").split()[2]
        except IndexError:
            raise SystemExit(sys.argv[0] + ': Invalid "' + file + '" media file.')


    def print(self):
        if self.isvalid():
            print(self._file + "    = Type: ", self._type, "(" + self._length + "),",
                  str(syslib.FileStat(self._file).getSize()) + " bytes")
            for stream, information in self.getStream():
                print(self._file + "[" + str(stream) + "] =", information)


    def isvalid(self):
        return self._type != "Unknown"


    def getDuration(self):
        return self._duration


    def getStream(self):
        for key in sorted(self._stream.keys()):
            yield (key, self._stream[key])


    def getStreamAudio(self):
        for key in sorted(self._stream.keys()):
            if self._stream[key].startswith("Audio: "):
                yield (key, self._stream[key])


    def getType(self):
        return self._type


    def hasAudio(self):
        for key in self._stream.keys():
            if self._stream[key].startswith("Audio: "):
                return True
        return False


    def hasAudioCodec(self, codec):
        for key in self._stream.keys():
            if self._stream[key].startswith("Audio: " + codec):
                return True
        return False


    def hasVideo(self):
        for key in self._stream.keys():
            if self._stream[key].startswith("Video: "):
                return True
        return False


    def hasVideoCodec(self, codec):
        for key in self._stream.keys():
            if self._stream[key].startswith("Video: " + codec):
                return True
        return False


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Encoder(options).run()
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
