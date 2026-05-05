# Orpheo VP — Versteckte Bedienfunktionen (Physische Taste A)

> Aus der offiziellen CCEI-Anleitung `docs/vendor/Notice_orpheo_VP_EN.pdf` v1.0EN.
> Das Geraet hat nur **eine einzige Taste (A)** unter der Pumpe. Alle "versteckten"
> Funktionen sind reine Press-Dauer- bzw. Power-Kombinationen.
>
> Alles hier ist **nur physisch** erreichbar — kein MQTT-Topic, keine App-Option.

## 1. Werksreset

**Loescht:** Kalibrierung, Sollwert, WLAN, Behaeltergroesse, Phone-Pairings, Vigipool-Kopplungen — **UND** die pH+/pH- Modus-Wahl.

1. Geraet am Kippschalter (Seite) **ausschalten**
2. **~10 Sekunden warten**
3. Taste (A) **druecken und gedrueckt halten**
4. Geraet **einschalten** waehrend du die Taste weiter gedrueckt haelst
5. Warten bis die 5 gruenen LEDs (B) **blinken**
6. Taste **loslassen** → Reset durchgefuehrt

Danach: komplette Erst-Einrichtung noetig (pH-Modus, Vigipool-Pairing, WLAN etc.).

## 2. pH+ / pH- Dosierrichtung wechseln

**Wichtig:** Der Modus kann **NUR direkt nach Power-on in der Setup-Phase** gewechselt werden.
Ist das Geraet einmal konfiguriert, braucht es vorher einen Werksreset (siehe oben).

Setup-Phase beim ersten Start nach Reset:
1. Nach dem Einschalten: 5 gruene LEDs (B) blinken **3x** → Setup-Modus aktiv
2. LED (C) zeigt den aktuellen Modus:
   - **WEISS** = pH- (Default, Saeuredosierung). LEDs 6.8 + 7.0 leuchten
   - **CYAN/BLAU** = pH+ (Basendosierung). LEDs 7.4 + 7.6 leuchten
3. **Jeder Klick** auf (A) togglet zwischen den beiden Modi
4. **5 Sekunden nicht druecken** → Modus wird gespeichert, LED (C) blinkt 5s, dann geht es in die Vigipool-Kopplung

O-Ton Manual: *"If you need to change the control mode again, you have to reset the system."*

## 3. Pumpen-Prime (Testlauf, Einwintern, Entlueften)

**Ignoriert den Flow-Interlock!** Laesst die Pumpe trocken bis zu 30 Sekunden laufen.

1. Im normalen Betrieb: Taste (A) druecken und **laenger als 10 Sekunden** halten
2. Nach 10s blinkt die RGB-LED (C) **tuerkis**
3. Pumpe laeuft **so lange (A) gehalten wird**, maximal 30 Sekunden
4. Bei Loslassen der Taste stoppt die Pumpe sofort

O-Ton Manual: *"the pump starts running regardless of the flow detector status for a maximum of 30 seconds, as long as the selection button is kept pressed."*

**Use-case:** Einwintern → Schlauch leer-pumpen; Nachfuellen → Saegmentansaugung testen; Erst-Inbetriebnahme → Luft aus der Leitung druecken.

## 4. Sollwert-Aenderung per Taste (ohne App)

Ist im Normalbetrieb ueber **kurzes** Druecken der Taste (A) erreichbar:
1. Kurzer Tastendruck → die 5 gruenen LEDs wechseln in den Sollwert-Selektionsmodus
2. Weitere kurze Tastendruecke schalten zwischen den vordefinierten Sollwerten durch
3. 5 Sekunden nicht druecken → Wert gespeichert
4. Default-Werte:
   - pH-: 7.2
   - pH+: 7.0

Fuer Feinjustierung (0.05 Schritte) muss die App oder HA verwendet werden.

## Referenz-LED-Matrix (grob)

| LED (C) Farbe | Bedeutung |
|---|---|
| Flackern gruen + Farbwechsel | Start-up |
| Weiss konstant | pH- Modus, normaler Betrieb |
| Cyan/Blau konstant | pH+ Modus, normaler Betrieb |
| Weiss blinkend | Vigipool-Kopplung, wartet auf "central" Device |
| Tuerkis blinkend | Pumpen-Prime aktiv (Taste gedrueckt) |
| Gelb/Orange/Rot | Dosierung laeuft (Abstand zum Sollwert) |
| Gruen pulsierend | Alles im Sollwert |

## Uebersicht: Was geht NICHT per HA?

| Funktion | Per HA? | Workaround |
|---|---|---|
| Werksreset | Nein | Physisch, Power-Cycle + Taste (A) halten |
| pH+/pH- wechseln | Nein | Werksreset + Setup-Phase |
| Pumpen-Prime | Nein | Taste (A) > 10s halten (bypassed Flow-Interlock) |
| Sensor-Kalibrierung | Nein | Nur in der Poolsana/Vigipool-App |
| Sollwert aendern | Ja | `number.<prefix>_ph_sollwert` / `_orp_sollwert` |
| Behaeltergroessen | Ja | `_ph_behaeltergroesse` / `_chlor_behaeltergroesse` |
| Spa/Winter-Modus | Ja | `switch.<prefix>_spa_modus` / `_winter_modus` |
| Max-Tagesdosis | Ja | `_ph_maximaldosis_tag` / `_chlor_maximaldosis_tag` |
| Alle Messwerte | Ja | pH, ORP, Pumpen, Flow, RSSI, Firmware, Fehler |
