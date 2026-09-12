#!/bin/bash
# vast.ai onstart script for the routeflow experiment box (Freerouting quality programme, 6 Sep 2026). Image ubuntu:24.04, runs as root once
# at container start. Installs KiCad 9.0 from the kicad-9.0-releases PPA (the VM's build), Java 25 (noble-updates; the FULL jre, not -headless: Freerouting 1.9.0 needs a headful AWT toolkit under Xvfb even in command-line mode), Xvfb, numpy; fetches the two
# Freerouting jars and checks them against the VM's sha256; clones the public mirror at the VM's path (the runner then overlays the VM's
# working tree with rsync); writes a no-op service-group script so the profiles need no change. Log /root/setup.log, marker SETUP-DONE or SETUP-FAILED <step>.
exec > /root/setup.log 2>&1; set -x
export DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8
touch /root/.no_auto_tmux
apt-get update && apt-get install -y --no-install-recommends software-properties-common ca-certificates curl git python3 python3-numpy python3.12-venv xvfb openjdk-25-jre rsync unzip zip procps || { echo "SETUP-FAILED apt"; exit 1; }
add-apt-repository -y ppa:kicad/kicad-9.0-releases && apt-get update && apt-get install -y --no-install-recommends kicad kicad-symbols kicad-footprints || { echo "SETUP-FAILED kicad"; exit 1; }
mkdir -p /root/bin
curl -fsSL -o /root/bin/freerouting-1.9.0.jar https://github.com/freerouting/freerouting/releases/download/v1.9.0/freerouting-1.9.0.jar || { echo "SETUP-FAILED download19"; exit 1; }
curl -fsSL -o /root/bin/freerouting-2.4.1.jar https://github.com/freerouting/freerouting/releases/download/v2.4.1/freerouting-2.4.1.jar || { echo "SETUP-FAILED download24"; exit 1; }
echo "9084a4888937a7f31f857ecc12aa7a37407f51160e4d2892dff9c9bb47ae3102  /root/bin/freerouting-1.9.0.jar" | sha256sum -c - || { echo "SETUP-FAILED sha19"; exit 1; }
echo "251101c3eeac22d7e7dfcf6796603279e5d1000283eb82d8f093780f7afc6aa9  /root/bin/freerouting-2.4.1.jar" | sha256sum -c - || { echo "SETUP-FAILED sha24"; exit 1; }
mkdir -p /root/gitlab/products/meshsat && git clone --depth 1 https://github.com/meshsat/meshsat-fieldkit /root/gitlab/products/meshsat/meshsat-fieldkit || { echo "SETUP-FAILED clone"; exit 1; }
# THE PATCHED JAR, BUILT HERE. `fr_jar.sh` refuses to route on the stock jar unless FR_REQUIRE_MESH=0,
# because the stock jar writes a session only when the whole job ends and a capped run then leaves nothing
# (appendix 32.118: C ran 2 h 08 min and wrote no session while E on the patched jar had one fifteen minutes
# in). Every fresh box therefore refused to route until somebody ran the five manual steps in
# tools/freerouting/README.md (red team round three H2). It is four commands; they belong here.
apt-get install -y openjdk-17-jdk-headless >/dev/null 2>&1 || { echo "SETUP-FAILED jdk17"; exit 1; }
( set -e
  cd /root && rm -rf fr-src
  git clone --depth 1 --branch v1.9.0 https://github.com/freerouting/freerouting.git fr-src
  python3 /root/gitlab/products/meshsat/meshsat-fieldkit/v2/ecad/tools/freerouting/ses_per_pass.py /root/fr-src
  cd /root/fr-src && JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 ./gradlew --no-daemon assemble
  cp build/libs/freerouting-executable.jar /root/bin/freerouting-1.9.0-mesh.jar
) >/root/mesh-jar-build.log 2>&1 || { echo "SETUP-FAILED mesh jar (see /root/mesh-jar-build.log)"; exit 1; }
[ -s /root/bin/freerouting-1.9.0-mesh.jar ] || { echo "SETUP-FAILED mesh jar is empty"; exit 1; }
echo "SETUP: the per-pass jar is built, $(stat -c%s /root/bin/freerouting-1.9.0-mesh.jar) bytes"

printf '#!/bin/sh\n# no service group on the cloud box; routeflow calls this before and after a run\nexit 0\n' > /root/meshsat-services.sh; chmod +x /root/meshsat-services.sh
# The pre-router's corridor search is 13.5x faster compiled (pairsearch.py) and numba cannot go into the KiCad python, so a venv
# that sees the system packages carries both; `pair_preroute.py` re-execs itself under it. Not fatal: without it the tool uses the
# heapq search, which returns the same paths.
python3 -m venv --system-site-packages /root/venv-numba && /root/venv-numba/bin/pip -q install numba && /root/venv-numba/bin/python -c "import numba, pcbnew; print('numba', numba.__version__)" || echo "SETUP-WARN numba (the heapq search will be used)"
kicad-cli version; python3 -c "import pcbnew; print('pcbnew', pcbnew.GetBuildVersion())"; java -version; nproc; free -g | head -2; df -h /root | tail -1
echo SETUP-DONE
