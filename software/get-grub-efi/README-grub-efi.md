## GRUB EFI 2.12

* UEFI boot loader for GPT partition secure booting from Debian 13

1) Run "dmesg | grep boot" to check secure booted
2) Create 128MB FAT16/FAT32 EFI boot partition (ie "/dev/sda1")
3) Mount boot partiton to /mnt/boot
4) Run "install-grub-efi.bash /mnt/boot" to copy files
5) Edit "/mnt/boot/grub/grub.cfg" (UUID from "sudo /sbin/blkid")

<pre>
EFI/boot/bootx64.efi    SHIM-EFI boot loader (shimx64.efi.signed)
EFI/boot/grubx64.efi    GRUB-EFI boot loader (grubx64.efi.signed)
EFI/boot/mmx64.efi      SHIM-EFI key manager (mmx64.efi.signed)
EFI/debian/grub.cfg     GRUB-EFI 2 boot menu (edit as required)
grub-efi.bash           GRUB-EFI installer
</pre>
