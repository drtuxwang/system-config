# Zhong Hua Speak 6.2.0

## 2009-2023 By Dr Colin Kong (https://github.com/drtuxwang/system-config)

# Introduction

This is a FREE Chinese Open Source text-to-speech software. It speak 普通話 (Putonghua) and
粵語 (Cantonese). It uses real voice samples to build speech.

It can also speak English (British), Deutsche (German), Español (Spanish), Française (French),
Utaliana (Italian) using third party TTS software:
* pico2wave - Pico TTS (libttspico-utils on Debian/Ubuntu)
* espeak-ng - Espeak-NG TTS


The following files are supplied:
<pre>
en_list    English Latin letters A-Z
zh.json    Zhonghua (普通話, Putonghua) compiled dictionary
zh_list    Zhonghua (普通話, Putonghua) dictionary (from Ekho 8.6)
zh_listx   Zhonghua (普通話, Putonghua) dictionary (from Ekho 9.0)
zh_listck  Zhonghua (普通話, Putonghua) numbers 0-9 (Dr Colin Kong)
zh_dir     Zhonghua (普通話, Putonghua) voice samples (jyutping-wong-44100-v9), A-Z (alphabet-wong-44100)
zhy.json   Zhonghua Yue (粵語, Cantonese) compiled dictionary
zhy_list   Zhonghua Yue (粵語, Cantonese) dictionary (from Ekho 8.6)
zhy_listck Zhonghua Yue (粵語, Cantonese) numbers 0-9 and phrase fixes (Dr Colin Kong)
zhy_dir    Zhonghua Yue (粵語, Cantonese) voice samples (pinyin-yali-44100-v10), A-Z (alphabet-wong-44100)
</pre>

All voice samples were re-encoded into MP3 using "ffmpeg" at 32kb/s


The supported audio players are:
* vlc
* ffplay (ffmpeg)
* avplay (libav-tools)

# Changes

## Since 6.2.0 (2023-09-23)
* 78) Update Python start wrapper scripts.
* 77) Updated Putonghua dictionary (Ekho 9.0).

## Since 6.1.2 (2023-01-24)
* 76) Now requirements Python 3.7 or later.
* 75) Defaulting to UTF-8 files on all systems.

## Since 6.1.1 (2023-01-01)
* 74) Python style fixes.

## Since 6.1.0 (2022-12-28)
* 73) Switch from "os.path" to "pathlib.Path".

## Since 6.0.4 (2022-11-20)
* 72) Fix Python 3.11 linting.

## Since 6.0.3 (2022-06-20)
* 71) Python clean up.

## Since 6.0.2 (2021-11-14)
* 70) Switch from "tar.xz" to ".7z" compression.

## Since 6.0.1 (2021-11-11)
* 69) Fix README.md markdown formatting.

## Since 6.0.0 (2021-11-07)
* 68) Switch to Python 3.6 f-strings.
* 67) Drop "ogg123" media player support.
* 66) Switched to MP3 32kb/s voice samples for smaller size.
* 65) Updated to "pinyin-yali-44100-v10" voice samples.

## Since 5.2.2 (2021-10-16)
* 64) Fix Python 3.6 issues with type annotations.

## Since 5.2.1 (2021-10-06)
* 63) Pylint fixes for UTF-8 file opening.

## Since 5.2.0 (2021-05-08)
* 62) Updated Putonghua/Cantonese dictionary (Ekho 8.6).
* 61) Add Python type checking.
* 60) Now requires Python 3.6 or later.

## Since 5.1.0 (2021-01-03)
* 59) Re-format 00README.txt as README.md Markdown documentation.
* 58) Use "espeak-ng" as backup to pico2wave.
* 57) Fix ogg123 being used for pico2wave.

## Since 5.0.0 (2021-01-02)
* 56) Add Jyutping button to "zhspeak.tcl" toolbar.
* 55) Re-designed "zhspeak.tcl" toolbar with 普通話, 拼音, 粵語 and 粵拼 labels.
* 54) Drop support for Russian and Serbian as Pico TTS does not support them.
* 53) Add support for Pico TTS (old Android TTS) to handle western languages for
      higher quality speech.

## Since 4.5.3 (2020-12-25)
* 52) Update Putonghua dictionary (Ekho 8.5).

## Since 4.5.3 (2020-12-25)
* 51) Pylint fixes for exception handling.

## Since 4.5.1 (2020-07-22)
* 50) Remove 靚相, 影相 and 朝頭早 fixes as they are merged into zhy_List.
* 49) Fixed 00README.txt update.

## Since 4.5.0 (2020-07-21)
* 48) Updated Putonghua/Cantonese dictionary (Ekho 8.3).
* 47) Add full UTF-8 support for JSON cache.
* 46) Now requires Python 3.5 or later.

## Since 4.4.2 (2020-01-19)
* 45) Prevent vlc commandline player looping when repeat selected in GUI.

## Since 4.4.1 (2020-01-04)
* 44) Pylint 2.4.4 fixes.

## Since 4.4.0 (2019-12-15)
* 43) Change Zhspeak default to vlc player.

## Since 4.3.0 (2019-12-01)
* 42) Updated Putonghua/Cantonese dictionary (Ekho 8.0).

## Since 4.2.0 (2019-08-18)
* 41) Switch from "espeak" to "espeak-ng" for non Chinese speech.

## Since 4.1.0 (2018-09-30)
* 40) Fixes for latest Python linting.

## Since 4.0.0 (2016-08-27)
* 39) Pylint fixes.

* 38) Optimized max block calculation and read JSON files at run time (3-5X faster)
* 37) Compiled Cantonese dictionaries to "zhspaek-data/zhy.json" file.
* 36) Compiled Putonghua dictionaries to "zhspaek-data/zh.json" file.
* 35) Now requires Python 3.2 or later.
* 34) Replaced "syslib2.py" with new "command_mod.py" and "subtask_mod.py" modules.
* 33) Change max column to 79 in Python code.
* 32) Removed no longer needed version 3.0 check.
* 31) Updated "command_mod.py", "subtask_mod.py" & "task_mod.py" modules.
* 30) Fixed multiple "-xclip" run problem.
* 29) Fixed "-xclip" clipboard speech for binding function keys.

## Since 3.0.7 (2015-10-31)
* 28) Updated voice copyright messages from Ekho 6.3.2.
* 27) Now "ffplay" player from FFmpeg searched before "avplay" from Libav-tools.
* 26) Added full PEP8 compatibility with 100 character line lengths.

## Since 3.0.5 (2015-06-25)
* 25) Lots of Python 3 style updates.
* 24) Renamed "pyloader.py" to "pyld.py". This Python module substitution for debugging.
* 23) Renamed "system.py" to "syslib2.py". This supports Python 2.7 and 3.x.

## Since 3.0.1 (2014-11-18)
* 22) Updated "system.py".

## Since 3.0.0 (2014-10-22)
* 21) The "zhspeak.tcl" GUI now uses  RGB colours instead of named colours to work better with
      multiple Linux distributions.
* 20) All Python classes now have proper data encapsulation and inherit from "system.Dump" class
      for object data dumping (debugging).
* 19) The "zhspeak.py" is now started by "pyloader.py" and so can be compiled to Python byte-code.
* 18) The "syslib.py" (API 1.0) library has been renamed "system.py" and updated (API 3.0).
* 17) Updated all source code to use more horizontal and vertical spacing to aid read-ability.
* 16) Updated "zhy_list" Cantonese dictionary (Ekho 6.0).

## Since 2.5.3-1 (2013-12-21)
* 15) Fixed Python traceback when printing player error.

## Since 2.5.3 (2013-10-26)
* 14) Fixed Python 2.7 by replacing "Español" with "Espanol" in on-line help.

## Since 2.5.2 (2013-10-14)
* 13) Updated pause every 100 words for long phrases without punctuation. The "ffplay"
      and "avplay" players cannot handle very long lists of ogg files.
* 12) Updated pause for punctuation marks like in "123,456".

## Since 2.5.1 (2013-10-13)
* 11) Updated "zhy_listck".

## Since 2.5.0 (2013-10-12)
* 10) Display 'Cannot find "ogg123" (vorbis-tools), "ffplay" (ffmpeg) or "avplay" (libav).'
      when no Oggplayer is found.
* 9)  Added "ffplay" (FFMPEG) and "avplay" (LIBAV) player support for ogg gapless playing.
* 8)  Removed "mplayer" support.

## Since 2.4.1-1 (2013-06-29)
* 7)  Updated "zhy_listck" Cantonese phrase fixes.
* 6)  Updated "zhspeak.py" Python code.

## Since 2.4.1 (2013-05-20)
* 5)  Renamed "zh_listn" to "zh_listck".
* 4)  Merged "zhy_listn" into "zhy_listck".

## Since 2.4.0 (2013-05-19)
* 3)  Added "zhy_listck" Cantonese phrase fixes (Dr Colin Kong).
* 2)  Updated "syslib.py" Python System Interaction Library.
* 1)  Updated "zhy_list" Cantonese dictionary (Ekho 5.4).
