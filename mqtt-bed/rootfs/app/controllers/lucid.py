# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import bluepy.btle as ble
import time
# import threading

class lucidBLEController:
    def __init__(self, addr):
        self.charWriteInProgress = False
        self.addr = addr
        self.commands = {
            #"Flat Preset": "040210000000",
            #"ZeroG Preset": "040200004000",
            #"TV Position": "040200003000",
            #"Quiet Sleep": "040200008000",
            #"Memory 1": "040200001000",
            #"Memory 2": "040200002000",
            #"Underlight": "040200020000",
            "Lift Head": "e6fe16040000000001",
            "Massage Toggle": "e6fe16000100000004",
            #"Lower Head": "040200000002",
            #"Lift Foot": "040200000004",
            #"Lower Foot": "040200000008",
            # Note: Wave cycles "On High", "On Medium", "On Low", "Off"
            #"Wave Massage Cycle": "040280000000",
            # Note: Head and Foot cycles "On Low, "On Medium", "On High", "Off"
            #"Head Massage Cycle": "040200000800",
            #"Foot Massage Cycle": "040200400000",
            #"Massage Off": "040202000000",
            #"Keepalive NOOP": "040200000000",
        }
        # Initialise the adapter and connect to the bed before we start waiting for messages.
        self.connectBed(ble)
        # Start the background polling/keepalive/heartbeat function.
        #thread = threading.Thread(target=self.bluetoothPoller, args=())
        #thread.daemon = True
        #thread.start()

    # There seem to be a lot of conditions that cause the bed to disconnect Bluetooth.
    # Here we use the value of 040200000000, which seems to be a noop.
    # This lets us poll the bed, detect a disconnection and reconnect before the user notices.
    #def bluetoothPoller(self):
    #    while True:
    #        if self.charWriteInProgress is False:
    #            try:
    #                cmd = self.commands.get("Keepalive NOOP", None)
    #                self.device.writeCharacteristic(0x0013, bytes.fromhex(cmd), withResponse=True)
    #                print("Keepalive success!")
    #            except:
    #                print("Keepalive failed! (1/2)")
    #                try:
    #                    # We perform a second keepalive check 0.5 seconds later before reconnecting.
    #                    time.sleep(0.5)
    #                    cmd = self.commands.get("Keepalive NOOP", None)
    #                    self.device.writeCharacteristic(0x0013, bytes.fromhex(cmd), withResponse=True)
    #                    print("Keepalive success!")
    #                except:
    #                    # If both keepalives failed, we reconnect.
    #                    print("Keepalive failed! (2/2)")
    #                    self.connectBed(ble)
    #        else:
    #            # To minimise any chance of contention, we don't heartbeat if a charWrite is in progress.
    #            print("charWrite in progress, heartbeat skipped.")
    #        time.sleep(10)

    # Separate out the bed connection to an infinite loop that can be called on init (or a communications failure).
    def connectBed(self, ble):
        while True:
            try:
                print("Attempting to connect to bed.")
                self.device = ble.Peripheral(deviceAddr=self.addr, addrType='random')
                print("Connected to bed.")
                self.characteristics = self.device.getCharacteristics(uuid='0000ffe9-0000-1000-8000-00805f9b34fb')
                print("characteristics: " + self.characteristics)
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
            print("Unknown Command, ignoring.")
            return
        self.charWriteInProgress = True
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
        self.characteristics.write(bytes.fromhex(cmd), withResponse=False)
        #self.device.writeCharacteristic(0x001a, bytes.fromhex(cmd), withResponse=True)
        print("Command sent successfully.")
        return