# Setup Proxmox to use GPU passthrough

## On the proxmox host:

### 1. Get the GPU ID

```bash
lspci -v
# search for gpu
# in our case: 21:00.0
lspci -n -s 21:00
>   21:00.0 0300: 10de:1e84 (rev a1)
    21:00.1 0403: 10de:10f8 (rev a1)
    21:00.2 0c03: 10de:1ad8 (rev a1)
    21:00.3 0c80: 10de:1ad9 (rev a1)
```

Note these IDs (10de:1e84, 10de:10f8, 10de:1ad8, 10de:1ad9) for the next steps.

### 2. Add to grub

TODO: Replace the IDs with the ones from the previous step

```bash
nano /etc/default/grub
> GRUB_CMDLINE_LINUX_DEFAULT="quiet splash amd_iommu=on kvm.ignore_msrs=1 vfio-pci.ids=10de:1e84,10de:10f8,10de:1ad8,10de:1ad9"
update-grub
```

### 3. Add to modules

```bash
nano /etc/modules
>   vfio
    vfio_iommu_type1
    vfio_pci
    vfio_virqfd
echo "options vfio_iommu_type1 allow_unsafe_interrupts=1" > /etc/modprobe.d/iommu_unsafe_interrupts.conf
echo "options kvm ignore_msrs=1" > /etc/modprobe.d/kvm.conf
```

### 4. Blacklist drivers

This is to prevent the host from using the GPU

```bash
echo "blacklist radeon" >> /etc/modprobe.d/blacklist.conf
echo "blacklist nouveau" >> /etc/modprobe.d/blacklist.conf
echo "blacklist nvidia" >> /etc/modprobe.d/blacklist.conf
echo "options vfio-pci ids=10de:1e84,10de:10f8,10de:1ad8,10de:1ad9 disable_vga=1"> /etc/modprobe.d/vfio.conf
update-initramfs -u

reboot
```

## On the proxmox guest:

### VM configuration:

Use Bios = OVMF (UEFI)
CPU type = host

### 1. Install the nvidia driver

```bash
sudo apt update
sudo apt install linux-headers-$(uname -r)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')
wget https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt -y install cuda-drivers
apt-get install qemu-guest-agent

sudo reboot now
```

### 2. Install docker

```bash
sudo apt update
curl -sSL https://get.docker.com | sh

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list \
  && \
    sudo apt-get update

sudo apt install nvidia-container-runtime -y
which nvidia-container-runtime-hook
sudo systemctl restart docker

sudo docker run -it --rm --gpus all ubuntu nvidia-smi # test
```
