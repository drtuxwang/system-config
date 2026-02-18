#!/usr/bin/env python3
"""
Show local IPv4 network neighbours
"""

import dataclasses
import ipaddress
import json
import signal
import sys
from pathlib import Path
from typing import Union

from command_mod import Command
from subtask_mod import Daemon, Batch


@dataclasses.dataclass(order=True)
class Address:
    """
    Address class
    """
    ipaddr: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]
    hwaddress: str
    device: str
    identity: str = '-'
    hostname: str = '-'

    def set_hostname(self, hostname: str) -> None:
        """
        Set hostname
        """
        self.hostname = hostname


class LocalNetwork:
    """
    LocalNetwork class
    """

    def __init__(self) -> None:
        self._addresses: dict = {}

    @staticmethod
    def scan() -> None:
        """
        Quick scan of all IPs in small subnets (ie 192.168.1.0/24)
        """
        ip = Command('ip', args=['addr'], errors='ignore')
        nmap = Command('nmap', args=['-sn'], errors='ignore')
        if ip.is_found() and nmap.is_found():
            task = Batch(ip.get_cmdline())
            task.run(pattern=r'inet \d.* .*global')
            for line in task.get_output():
                subnet = line.split()[1]
                if int(subnet.rsplit('/', 1)[-1]) <= 26:  # 1024
                    Daemon(nmap.get_cmdline() + [subnet]).run()

    def _browse(self) -> None:
        avahi_browse = Command('avahi-browse', args=['-artp'], errors='ignore')
        if avahi_browse.is_found():
            task = Batch(avahi_browse.get_cmdline())
            task.run(pattern=r'^=.*IPv4')
            for line in task.get_output():
                cols = line.split(';')
                ipaddr = ipaddress.ip_address(cols[7])
                ipnum = int(ipaddr)
                self._addresses[ipnum] = Address(
                    ipaddr,
                    cols[3].replace('\\058', ':')[-21:-4],
                    cols[1],
                    hostname=cols[6],
                )

    def _read_arp(self) -> None:
        arp = Command('arp', pathextra=['/sbin'], errors='stop')
        task = Batch(arp.get_cmdline())
        task.run(pattern=':..:..:..:..:')
        for line in task.get_output():
            cols = line.split()
            ipaddr = ipaddress.ip_address(cols[0])
            ipnum = int(ipaddr)
            if ipnum not in self._addresses:
                self._addresses[ipnum] = Address(
                    ipaddr,
                    cols[2],
                    cols[4],
                )

    def _read_json(self) -> None:
        path = Path(Path.home(), '.config', 'netls.json')
        if not path.is_file():
            path.write_text(json.dumps({"netls": {"identity": {
                "xx:xx:xx:xx:xx:xx": "???",
                "yy:yy:yy:yy:yy:yy": "???",
                "zz:zz:zz:zz:zz:zz": "???"
            }}}, indent=4))

        try:
            data = json.loads(path.read_text(errors='replace'))
            mappings = data['netls']['identity']
        except json.decoder.JSONDecodeError:
            print(f'Warning: ignoring corrupt "{path}" file', file=sys.stderr)
        else:
            for v in self._addresses.values():
                if v.hwaddress in mappings:
                    v.identity = mappings[v.hwaddress]

    def resolve(self) -> None:
        """
        Resolve IP address to hardware address and mDNS/DNS-SD hostnames
        """
        self._browse()
        self._read_arp()
        self._read_json()

    def show(self) -> None:
        """
        Show enhanced ARP table
        """
        print(
            "Address          HWaddress          Iface   Identity        "
            "Hostname"
        )
        for _, v in sorted(self._addresses.items()):
            print(
                f"{v.ipaddr:15s}  {v.hwaddress:17s}  {v.device[:8]:7s} "
                f"{v.identity[:15]:15s} {v.hostname[:20]:20s}"
            )


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        network = LocalNetwork()
        network.scan()
        network.resolve()
        network.show()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
