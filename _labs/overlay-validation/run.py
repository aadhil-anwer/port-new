#!/usr/bin/env python3
"""Bounded packet tests in disposable user/network namespaces; no external route."""
import json, os, pathlib, select, socket, struct, subprocess, sys, time

BASE = pathlib.Path(__file__).resolve().parent
if '--isolated' not in sys.argv:
    os.execvp('unshare', ['unshare', '-Urn', sys.executable, str(pathlib.Path(__file__).resolve()), '--isolated', os.readlink('/proc/self/ns/net')])
assert os.readlink('/proc/self/ns/net') != sys.argv[-1], 'Refusing host network namespace'
OUT = BASE / 'results'
OUT.mkdir(exist_ok=True)
log = []
def run(*args, input=None):
    p = subprocess.run(args, input=input, text=True, capture_output=True)
    log.append({'command': list(args), 'stdout': p.stdout, 'stderr': p.stderr})
    if p.returncode:
        raise RuntimeError(f'{args}: {p.stderr}')
    return p.stdout.strip()
def ip(*args): return run('ip', *args)
child = subprocess.Popen(['unshare', '-n', 'sleep', '300'])
try:
    for _ in range(100):
        if os.readlink(f'/proc/{child.pid}/ns/net') != os.readlink('/proc/self/ns/net'): break
        time.sleep(.01)
    else: raise RuntimeError('Child namespace did not initialize')
    def peer(*args): return run('nsenter', '-t', str(child.pid), '-n', *args)
    ip('link', 'add', 'underlay', 'type', 'veth', 'peer', 'name', 'sender')
    ip('link', 'set', 'sender', 'netns', str(child.pid))
    ip('addr', 'add', '192.0.2.1/24', 'dev', 'underlay')
    ip('link', 'set', 'underlay', 'up'); ip('link', 'set', 'lo', 'up')
    peer('ip', 'addr', 'add', '192.0.2.2/24', 'dev', 'sender')
    peer('ip', 'link', 'set', 'sender', 'up'); peer('ip', 'link', 'set', 'lo', 'up')
    ip('link', 'add', 'vx5000', 'type', 'vxlan', 'id', '5000', 'local', '192.0.2.1', 'dev', 'underlay', 'dstport', '4789')
    ip('link', 'set', 'vx5000', 'up')
    ip('link', 'add', 'link', 'underlay', 'name', 'vlan20', 'type', 'vlan', 'id', '20')
    ip('link', 'set', 'vlan20', 'up')
    receivers = {}
    pcaps = {}
    for name in ['underlay', 'vx5000', 'vlan20']:
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3)); s.bind((name, 0)); s.setblocking(False)
        receivers[name] = s
        f = (OUT / (name + '.pcap')).open('wb'); f.write(struct.pack('<IHHIIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)); pcaps[name] = f
    def capture(seconds, marker):
        found = {name: 0 for name in receivers}
        until = time.monotonic() + seconds
        while time.monotonic() < until:
            ready, _, _ = select.select(list(receivers.values()), [], [], max(0, until-time.monotonic()))
            for s in ready:
                data = s.recv(65535); name = next(k for k,v in receivers.items() if v is s)
                now = time.time(); pcaps[name].write(struct.pack('<IIII', int(now), int((now%1)*1e6), len(data), len(data)) + data)
                if marker in data: found[name] += 1
        return found
    tests = []
    def test(name, target, expected, vni=None, tags=None, mac='020000000002'):
        capture(.05, b'__drain__')
        marker = ('LAB-' + name).encode()
        if vni is not None:
            frame = bytes.fromhex('ffffffffffff' + mac + '88b5') + marker
            payload = b'\x08\x00\x00\x00' + vni.to_bytes(3,'big') + b'\x00' + frame
            code = "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.sendto(bytes.fromhex('%s'),('192.0.2.1',4789))" % payload.hex()
        else:
            dst = json.loads(ip('-j','link','show','underlay'))[0]['address'].replace(':','')
            frame = bytes.fromhex(dst + mac) + b''.join(struct.pack('!HH',0x8100,t) for t in tags) + bytes.fromhex('88b5') + marker
            code = "import socket; s=socket.socket(socket.AF_PACKET,socket.SOCK_RAW); s.bind(('sender',0)); s.send(bytes.fromhex('%s'))" % frame.hex()
        peer(sys.executable, '-c', code)
        found = capture(.4, marker)
        fdb = run('bridge','fdb','show','dev','vx5000')
        result = {'test':name,'target':target,'expected_delivery':expected,'observed_packets':found,'passed':bool(found[target]) == expected,'fdb':fdb}
        tests.append(result); print(json.dumps(result), flush=True)
    test('vxlan-configured-vni','vx5000',True,vni=5000)
    assert '02:00:00:00:00:02' in tests[-1]['fdb'], 'Expected dynamic FDB learning'
    test('vxlan-unknown-vni','vx5000',False,vni=5001)
    run('nft','-f','-',input='table inet lab { chain input { type filter hook input priority 0; policy accept; ip saddr 192.0.2.2 udp dport 4789 counter drop; }; }\n')
    test('vxlan-source-blocked','vx5000',False,vni=5000)
    firewall = run('nft','list','table','inet','lab')
    run('nft','delete','table','inet','lab')
    test('vxlan-filter-removed','vx5000',True,vni=5000)
    ip('link','set','vx5000','type','vxlan','nolearning')
    test('vxlan-nolearning','vx5000',True,vni=5000,mac='020000000003')
    assert '02:00:00:00:00:03' not in tests[-1]['fdb'], 'nolearning unexpectedly learned source'
    test('vlan20-tag','vlan20',True,tags=[20])
    test('vlan30-tag','vlan20',False,tags=[30])
    test('vlan0-only','vlan20',False,tags=[0])
    test('vlan-untagged','vlan20',False,tags=[])
    # Initial run unexpectedly delivered 0/20; retained in results-initial.
    # Confirm that observation alongside a wrong-inner-VLAN control.
    test('vlan0-then20','vlan20',True,tags=[0,20])
    test('vlan0-then30','vlan20',False,tags=[0,30])
    metadata = {'kernel':os.uname().release,'iproute2':run('ip','-Version'),'nftables':run('nft','--version'),'date_utc':run('date','-u','+%FT%TZ'),'routes':ip('route'),'vxlan':ip('-d','link','show','vx5000'),'firewall_counter':firewall,'tests':tests}
    (OUT/'results.json').write_text(json.dumps(metadata,indent=2)+'\n')
    if not all(t['passed'] for t in tests): raise RuntimeError('Unexpected observation; inspect results')
finally:
    for f in locals().get('pcaps',{}).values(): f.close()
    (OUT/'commands.json').write_text(json.dumps(log,indent=2)+'\n')
    child.terminate(); child.wait(timeout=5)
