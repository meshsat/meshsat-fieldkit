#!/bin/bash
# vast.ai onstart script for the routeflow experiment box (Freerouting quality programme, 6 Sep 2026). Image ubuntu:24.04, runs as root once
# at container start. Installs KiCad 9.0 from the kicad-9.0-releases PPA (the VM's build), Java 25 (noble-updates), Xvfb, numpy; fetches the two
# Freerouting jars and checks them against the VM's sha256; clones the public mirror at the VM's path (the runner then overlays the VM's
# working tree with rsync); writes a no-op service-group script so the profiles need no change. Log /root/setup.log, marker SETUP-DONE or SETUP-FAILED <step>.
exec > /root/setup.log 2>&1; set -x
export DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8
touch /root/.no_auto_tmux
apt-get update && apt-get install -y --no-install-recommends software-properties-common ca-certificates curl git python3 python3-numpy xvfb openjdk-25-jre-headless rsync unzip procps || { echo "SETUP-FAILED apt"; exit 1; }
add-apt-repository -y ppa:kicad/kicad-9.0-releases && apt-get update && apt-get install -y --no-install-recommends kicad || { echo "SETUP-FAILED kicad"; exit 1; }
mkdir -p /root/bin
curl -fsSL -o /root/bin/freerouting-1.9.0.jar https://github.com/freerouting/freerouting/releases/download/v1.9.0/freerouting-1.9.0.jar || { echo "SETUP-FAILED download19"; exit 1; }
curl -fsSL -o /root/bin/freerouting-2.4.1.jar https://github.com/freerouting/freerouting/releases/download/v2.4.1/freerouting-2.4.1.jar || { echo "SETUP-FAILED download24"; exit 1; }
echo "9084a4888937a7f31f857ecc12aa7a37407f51160e4d2892dff9c9bb47ae3102  /root/bin/freerouting-1.9.0.jar" | sha256sum -c - || { echo "SETUP-FAILED sha19"; exit 1; }
echo "251101c3eeac22d7e7dfcf6796603279e5d1000283eb82d8f093780f7afc6aa9  /root/bin/freerouting-2.4.1.jar" | sha256sum -c - || { echo "SETUP-FAILED sha24"; exit 1; }
mkdir -p /root/gitlab/products/meshsat && git clone --depth 1 https://github.com/meshsat/meshsat-fieldkit /root/gitlab/products/meshsat/meshsat-fieldkit || { echo "SETUP-FAILED clone"; exit 1; }
printf '#!/bin/sh\n# no service group on the cloud box; routeflow calls this before and after a run\nexit 0\n' > /root/meshsat-services.sh; chmod +x /root/meshsat-services.sh
kicad-cli version; python3 -c "import pcbnew; print('pcbnew', pcbnew.GetBuildVersion())"; java -version; nproc; free -g | head -2; df -h /root | tail -1
echo SETUP-DONE
