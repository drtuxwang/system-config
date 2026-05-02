## GRUB PC 2.06

* BIOS boot loader for legacy MBR/GPT partition booting from Debian 12
* Grub 2.06 does not support newer versions of file systems like ext4 formatted in Debian 13.
* Grub PC 2.12 and later fails to boot older Linux kernels (ie Debian 4-5)

1) Mount "/mnt/boot".
2) Run "install-grub-pc.bash /mnt/boot" to install MBR boot sector & stage 2 files.
3) Edit "/mnt/boot/grub/grub.cfg" as required.
