# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import bluepy.btle as ble
import time
import threading

class lucidBLEController:
    def __init__(self, addr):
        self.charWriteInProgress = False
        self.addr = addr
        self.commands = {
            "Flat Preset":        "e6fe160000000800fd",
            "ZeroG Preset":       "e6fe160010000000f5",
            "TV Preset":          "e6fe160040000000c5",
            "Lounge Preset":      "e6fe160020000000e5",
            "Quiet Sleep":        "e6fe16008000000085",
            "Memory 1":           "e6fe16000001000004",
            "Memory 2":           "e6fe16000004000001",
            "Underlight":         "e6fe16000002000003",
            "Lift Head":          "e6fe16010000000004",
            "Lower Head":         "e6fe16020000000003",
            "Lift Foot":          "e6fe16040000000001",
            "Lower Foot":         "e6fe160800000000fd",
            "Massage Toggle":     "e6fe16000100000004",
            # Note: Wave cycles "On High", "On Medium", "On Low", "Off"
            "Wave Massage Cycle": "e6fe160000001000f5",
            # Note: Head and Foot cycles "On Low, "On Medium", "On High", "Off"
            "Head Massage Cycle": "e6fe160008000000fd",
            "Foot Massage Cycle": "e6fe16000400000001",
            "Massage Timer":      "e6fe16000200000003",
            "Keepalive NOOP":     "e6fe16000000000005",
        }
        # Initialise the adapter and connect to the bed before we start waiting for messages.
        self.connectBed(ble)
        # Start the background polling/keepalive/heartbeat function.
        thread = threading.Thread(target=self.bluetoothPoller, args=())
        thread.daemon = True
        thread.start()

    # There seem to be a lot of conditions that cause the bed to disconnect Bluetooth.
    # Here we use the value of 040200000000, which seems to be a noop.
    # This lets us poll the bed, detect a disconnection and reconnect before the user notices.
    def bluetoothPoller(self):
       while True:
           if self.charWriteInProgress is False:
               try:
                   cmd = self.commands.get("Keepalive NOOP", None)
                   self.device.getServiceByUUID(0xffe5).getCharacteristics(0xffe9)[0].write(bytes.fromhex(cmd), withResponse=True)
                   print("Keepalive success!")
               except:
                   print("Keepalive failed! (1/2)")
                   try:
                       # We perform a second keepalive check 0.5 seconds later before reconnecting.
                       time.sleep(0.5)
                       cmd = self.commands.get("Keepalive NOOP", None)
                       self.device.getServiceByUUID(0xffe5).getCharacteristics(0xffe9)[0].write(bytes.fromhex(cmd), withResponse=True)
                       print("Keepalive success!")
                   except:
                       # If both keepalives failed, we reconnect.
                       print("Keepalive failed! (2/2)")
                       self.connectBed(ble)
           else:
               # To minimise any chance of contention, we don't heartbeat if a charWrite is in progress.
               print("charWrite in progress, heartbeat skipped.")
               if time.time() - self.charWriteStart > 30:
                 print("charWrite in progress for 30 seconds, exiting now")
                 sys.exit()

           time.sleep(10)

    # Separate out the bed connection to an infinite loop that can be called on init (or a communications failure).
    def connectBed(self, ble):
        while True:
            try:
                print("Attempting to connect to bed.")
                self.device = ble.Peripheral(deviceAddr=self.addr, addrType='random')
                print("Connected to bed.")
                return
            except:
                pass
            print("Error connecting to bed, retrying in one second.")
            time.sleep(1)

    # Separate out the command handling.
    def sendCommand(self,name):
        cmd = self.commands.get(name, None)
        if cmd is None:
            # print, but otherwise ignore Unknown Commands.
            # print("Unknown Command, ignoring.")
            # return
            cmd = name
        self.charWriteInProgress = True
        self.charWriteStart = time.time()
        try:
            self.charWrite(cmd)
        except:
            print("Error sending command, attempting reconnect.")
            start = time.time()
            self.connectBed(ble)
            end = time.time()
            if ((end - start) < 5):
                try:
                    self.charWrite(self, cmd)
                except:
                    print("Command failed to transmit despite second attempt, dropping command.")
            else:
                print("Bluetooth reconnect took more than five seconds, dropping command.")
        self.charWriteInProgress = False

    # Separate charWrite function.
    def charWrite(self, cmd):
        print("Attempting to transmit command.")
        self.device.getServiceByUUID(0xffe5).getCharacteristics(0xffe9)[0].write(bytes.fromhex(cmd), withResponse=True)
        print("Command sent successfully.")
        return