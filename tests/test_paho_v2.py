#!/usr/bin/env python3
"""Regressionstest: paho-mqtt Callback-API VERSION2 (Hauptclient).

Laeuft OHNE Home Assistant und ohne pytest, braucht paho-mqtt >= 2.0:

    python3 -W error::DeprecationWarning tests/test_paho_v2.py

Prueft: keine DeprecationWarning bei Client-Instanziierung, V2-Callback-
Signaturen (on_connect/on_disconnect) per Fake-Aufruf UND ueber den echten
paho-Netzwerk-Loop gegen einen Mini-Broker (CONNACK, dann Abbruch).
"""
import importlib.util, pathlib, sys, types, warnings, socket, threading, time, logging
warnings.simplefilter("error", DeprecationWarning)   # jede DeprecationWarning = Fehler
BASE = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "tomtut_pool_dosing_vigipool"
pkg = types.ModuleType("vigi"); pkg.__path__=[str(BASE)]; sys.modules["vigi"]=pkg
def load(n):
    sp=importlib.util.spec_from_file_location(f"vigi.{n}",BASE/f"{n}.py"); m=importlib.util.module_from_spec(sp)
    sys.modules[f"vigi.{n}"]=m; sp.loader.exec_module(m); return m
import paho.mqtt, paho.mqtt.client as mqtt
from paho.mqtt.reasoncodes import ReasonCode
from paho.mqtt.packettypes import PacketTypes
print("paho", paho.mqtt.__version__)
load("const"); mc = load("mqtt_client")
logs=[]
class H(logging.Handler):
    def emit(s,r): logs.append((r.levelname,r.getMessage()))
logging.getLogger("vigi.mqtt_client").addHandler(H()); logging.getLogger("vigi.mqtt_client").setLevel(logging.DEBUG)
ok=0
def check(c,t):
    global ok; print(("PASS " if c else "FAIL ")+t); assert c, t; ok+=1
cl = mc.OrpheoMqttClient(hass=None, host="127.0.0.1", port=1, phileo_id="AABBCCDDEEFF", oxeo_id="112233445566", instance_suffix="x")
check(cl._client._callback_api_version == mqtt.CallbackAPIVersion.VERSION2, "Client-Instanziierung VERSION2 ohne DeprecationWarning")
# Fake-Aufrufe
subs=[]
class FC:
    def subscribe(s,f): subs.append(f)
cl._on_connect(FC(), None, mqtt.ConnectFlags(False), ReasonCode(PacketTypes.CONNACK, identifier=0), None)
check(cl.connected and len(subs)==1 and len(subs[0])==2, "on_connect Erfolg -> connected + 2 Subscribe-Filter")
cl2 = mc.OrpheoMqttClient(None,"127.0.0.1",1,"AABBCCDDEEFF","112233445566")
cl2._on_connect(FC(), None, mqtt.ConnectFlags(False), ReasonCode(PacketTypes.CONNACK, aName="Not authorized"), None)
check(not cl2.connected and any(l[0]=="ERROR" for l in logs), "on_connect Fehler (Not authorized) -> nicht connected, ERROR geloggt")
n=len(logs)
cl._on_disconnect(None,None,mqtt.DisconnectFlags(False),ReasonCode(PacketTypes.DISCONNECT, aName="Unspecified error"),None)
check(not cl.connected and cl.disconnected_since>0 and any(l[0]=="WARNING" for l in logs[n:]), "on_disconnect unerwartet -> WARNING + Zeitstempel")
ts=cl.disconnected_since; n=len(logs)
cl._on_disconnect(None,None,mqtt.DisconnectFlags(False),ReasonCode(PacketTypes.DISCONNECT, aName="Unspecified error"),None)
check(len(logs)==n and cl.disconnected_since==ts, "on_disconnect doppelt -> idempotent (kein 2. WARNING)")
cl._connected=True; n=len(logs)
cl._on_disconnect(None,None,mqtt.DisconnectFlags(False),ReasonCode(PacketTypes.DISCONNECT, identifier=0),None)
check(not cl.connected and not any(l[0]=="WARNING" for l in logs[n:]), "on_disconnect sauber (rc=0) -> kein WARNING")
class M: topic="phileox_AABBCCDDEEFF/x/y/z/reported"; payload=b"1"
cl._on_message(None,None,M()); check(True,"on_message Signatur unveraendert")
# Echter paho-Dispatch: Mini-Broker sendet CONNACK, schliesst dann Socket
srv=socket.socket(); srv.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1); srv.bind(("127.0.0.1",0)); srv.listen(1); port=srv.getsockname()[1]
def broker():
    c,_=srv.accept(); c.recv(1024); c.sendall(bytes([0x20,0x02,0x00,0x00])); time.sleep(0.5); c.close()
threading.Thread(target=broker,daemon=True).start()
subcalls=[]
real = mc.OrpheoMqttClient(None,"127.0.0.1",port,"AABBCCDDEEFF","112233445566")
real._client.subscribe = lambda f,*a,**k: subcalls.append(f) or (0,1)
n=len(logs); real._connect()
t0=time.time()
while not real.connected and time.time()-t0<5: time.sleep(0.05)
check(real.connected and subcalls, "echter paho-Loop: CONNACK -> _on_connect (V2-Signatur) -> subscribe")
t0=time.time()
while real.connected and time.time()-t0<5: time.sleep(0.05)
check(not real.connected and any(l[0]=="WARNING" and "unexpected disconnect" in l[1] for l in logs[n:]), "echter paho-Loop: Verbindungsabbruch -> _on_disconnect (V2) -> WARNING")
print("  Log:", [l for l in logs[n:] if l[0]=="WARNING"])
real._disconnect()
print(f"{ok}/{ok} Checks bestanden, keine DeprecationWarning")
