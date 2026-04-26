## GRUB PC 2.12

* BIOS boot loader for MBR/GPT partition booting from Debian 13
* Grub PC 2.06 needed to boot older Linux kernels (ie Debian 4-5)

1) Mount "/mnt/boot".
2) Run "grub-pc/install-grub-pc.bash /mnt/boot" to install MBR boot sector & stage 2 files.
3) Edit "/mnt/boot/grub/grub.cfg" as required.
