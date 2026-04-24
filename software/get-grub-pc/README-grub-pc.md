## GRUB PC 2.12

* BIOS boot loader for MBR/GPT partition booting from Debian 13
* Grub PC 2.06 needed to boot older Linux kernels (ie Debian 4-5)

1) Mount boot partition to /mnt/boot
2) Copy Run "grub-pc.bash" to "/mnt/boot"
3) Run "/mnt/boot/grub-pc.bash" to install MBR boot sector & stage 2 files
3) Edit "/mnt/boot/grub/grub.cfg" as required.
