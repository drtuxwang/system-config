#!/usr/bin/env bash

VERSION=$(uname -r | cut -f1-2 -d. | awk '{printf("%s\n", $1*10)}')
DIR=${0%/config/*}/pool/software

install() {
    ARCHIVE=$(ls -1t ""$1"" | head -1)
    echo "Installing \"$ARCHIVE\" archive..." | sed -e "s/\//\\\\/g"
    c:/software/bin/7z.bat x -oc:/software -y "$ARCHIVE"
}

echo
install "$DIR/system-config_*_generic.7z"
echo
install "$DIR/vim_*_win*x86.7z"

if [ $VERSION -ge 60 ]
then
    echo "@echo off" > "$TMP/winsetup.bat"
    case $VERSION in
    60)
        cat << EOF >> "$TMP/winsetup.bat"
schtasks.exe /delete /tn "\Microsoft\Windows\Customer Experience Improvement Program\Consolidator" /f
schtasks.exe /delete /tn "\Microsoft\Windows\Defrag\ScheduledDefrag" /f
schtasks.exe /delete /tn "\Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector" /f
schtasks.exe /delete /tn "\Microsoft\Windows Defender\MP Scheduled Scan" /f
EOF
        ;;
    61)
        cat << EOF >> "$TMP/winsetup.bat"
schtasks.exe /delete /tn "\Microsoft\Windows\Customer Experience Improvement Program\Consolidator" /f
schtasks.exe /delete /tn "\Microsoft\Windows\Customer Experience Improvement Program\KernelCeipTask" /f
schtasks.exe /delete /tn "\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip" /f
schtasks.exe /delete /tn "\Microsoft\Windows\Defrag\ScheduledDefrag" /f
schtasks.exe /delete /tn "\Microsoft\Windows\Diagnosis\Scheduled" /f
schtasks.exe /delete /tn "\Microsoft\Windows\Power Efficiency Diagnostics\AnalyzeSystem" /f
schtasks.exe /delete /tn "\Microsoft\Windows\RAC\RacTask" /f
schtasks.exe /delete /tn "\Microsoft\Windows\Registry\RegIdleBackup" /f
schtasks.exe /delete /tn "\Microsoft\Windows\Time Synchronization\SynchronizeTime" /f
schtasks.exe /delete /tn "\Microsoft\Windows\WindowsBackup\ConfigNotification" /f
schtasks.exe /delete /tn "\Microsoft\Windows Defender\MP Scheduled Scan" /f
EOF
        ;;
    63)
        cat << EOF >> "$TMP/winsetup.bat"
schtasks.exe /delete /tn "\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser" /f
schtasks.exe /delete /tn "\Microsoft\Windows\Customer Experience Improvement Program\Consolidator" /f
schtasks.exe /delete /tn "\Microsoft\Windows\Defrag\ScheduledDefrag" /f
schtasks.exe /delete /tn "\Microsoft\Windows\PerfTrack\BackgroundConfigSurveyor" /f
schtasks.exe /delete /tn "\Microsoft\Windows\RAC\RacTask" /f
schtasks.exe /delete /tn "\Microsoft\Windows\TaskScheduler\Regular Maintenance" /f
schtasks.exe /delete /tn "\Microsoft\Windows\WS\WSRefreshBannedAppsListTask" /f
EOF
        ;;
    100)
        cat << EOF >> "$TMP/winsetup.bat"
schtasks.exe /delete /tn "\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser" /f
schtasks.exe /delete /tn "\Microsoft\Windows\Data Integrity Scan\Data Integrity Scan" /f
schtasks.exe /delete /tn "\Microsoft\Windows\Customer Experience Improvement Program\Consolidator" /f
schtasks.exe /delete /tn "\Microsoft\Windows\Defrag\ScheduledDefrag" /f
schtasks.exe /delete /tn "\Microsoft\Windows\Device Information\Device" /f
schtasks.exe /delete /tn "\Microsoft\Windows\Flighting\OneSettings\RefreshCache" /f
schtasks.exe /delete /tn "\Microsoft\Windows\InstallService\ScanForUpdates" /f
schtasks.exe /delete /tn "\Microsoft\Windows\UNP\RunUpdateNotificationMgr" /f
schtasks.exe /delete /tn "\Microsoft\Windows\Windows Error Reporting\QueueReporting" /f
schtasks.exe /delete /tn "\Microsoft\Windows\WindowsUpdate\Scheduled Start" /f
EOF
        ;;
    esac
    [ $VERSION -ge 61 ] && tzutil /s "GMT Standard Time"
    [ $VERSION -ge 100 ] && echo y | powershell Set-WinUserLanguageList -LanguageList en-GB

    echo
    echo "Running \"$TMP/winsetup.bat\"..."
    echo "pause" >> "$TMP/winsetup.bat"
    powershell.exe -command start-process "$TMP/winsetup.bat" -verb runas

    if [ $VERSION -ge 61 ]
    then
        echo
        if [ $VERSION -lt 100 ]
        then
            echo "Running \"$DIR/vc-redist_14.0.23026_win51x86.exe\"..."
            "$DIR/vc-redist_14.0.23026_win51x86.exe"
        fi
        install "$DIR/python_3.*_win*x86.7z"
    fi

    if [ $VERSION -ge 100 ]
    then
        echo
        echo "Running \"netplwiz\" to remove \"Users must enter user and password\"..."
        if [ -f "c:/Program Files/Oracle/VirtualBox Guest Additions/VBoxGuest.inf" ]
        then
            echo "  (VM password is \"Passw0rd!\")"
        fi
        cmd /r netplwiz
    fi
fi

##if [ "$PROCESSOR_ARCHITECTURE" = AMD64 -o "$PROCESSOR_ARCHITEW6432" = AMD64 ]
##then
##    INSTALLER=$(ls -1t "$DIR"/virtualbox-additions_*_win6451x86.7z | head -1)
##else
##    INSTALLER=$(ls -1t "$DIR"/virtualbox-additions_*_win51x86.7z | head -1)
##fi
##echo "Running \"$INSTALLER\" installer..." | sed -e "s/\//\\\\/g"
##cmd /r "$INSTALLER"

if [ "${0%/*}/../scripts/index-system" ]
then
    cd h:/
    ${0%/*}/../scripts/index-system
fi
