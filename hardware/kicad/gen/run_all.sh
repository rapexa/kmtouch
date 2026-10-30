set -e
K=/workspace/kmtouch/hardware/kicad; cd $K
python3 gen/gen_sch.py
kc python3 $K/gen/build_pcb.py 2>&1 | grep -v Warn || true
sudo chown -R box:box .; python3 gen/patch_pro.py >/dev/null
kc python3 $K/gen/route.py dsn 2>&1 | grep -v Warn || true
cd gen; timeout 760 xvfb-run -a /opt/kc/fr/jdk-21.0.13+9-jre/bin/java -jar /opt/kc/fr/fr19.jar -de kmtouch.dsn -do kmtouch.ses -mp ${MP:-100} > fr19.log 2>&1 || true
grep completed fr19.log || true; cd ..
cp kmtouch.kicad_pcb gen/unrouted.kicad_pcb
kc python3 $K/gen/route.py ses 2>&1 | grep -v "Warn\|leak" || true
sudo chown -R box:box .
kc kicad-cli pcb drc -o $K/drc.rpt $K/kmtouch.kicad_pcb 2>&1 | grep Found || true
sudo chown box drc.rpt; grep -E "^\[" drc.rpt | cut -d: -f1 | sort | uniq -c
grep -A2 "unconnected_items" drc.rpt | grep "@" || true
kc python3 $K/gen/finish.py 2>&1 | grep -v "Warn\|leak" || true; sudo chown -R box:box $K
kc python3 $K/gen/setpaths.py 2>&1 | grep -v Warn || true
