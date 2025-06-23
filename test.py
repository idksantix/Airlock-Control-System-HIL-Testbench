import serial
import time
import sys

startMarker = '<'
endMarker = '>'
dataStarted = False
dataBuf = ""
messageComplete = False
TEST_MODE = False  # Set to True to run without Arduino

# Pin state management
class PinManager:
    def __init__(self):
        # Output pins (controllable)
        self.output_pins = {
            'PRESENCE_FRONT': False,
            'PRESENCE_MIDDLE': False,
            'PRESENCE_BACK': False,
            'GATE_SAFETY_A': False,
            'GATE_SAFETY_B': False,
            'GATE_MOVING_A': False,
            'GATE_MOVING_B': False
        }
        
        # Input pins (read-only, from Arduino)
        self.input_pins = {
            'GATE_REQUEST_A': False,
            'GATE_REQUEST_B': False
        }
    
    def set_pin(self, pin_name, value):
        """Set the state of an output pin"""
        if pin_name in self.output_pins:
            self.output_pins[pin_name] = bool(value)
            print(f"Set {pin_name} to {value}")
            return True
        else:
            print(f"Pin {pin_name} is not controllable")
            return False
    
    def get_pin(self, pin_name):
        """Get the state of any pin"""
        if pin_name in self.output_pins:
            return self.output_pins[pin_name]
        elif pin_name in self.input_pins:
            return self.input_pins[pin_name]
        else:
            print(f"Unknown pin: {pin_name}")
            return None
    
    def update_input_pins(self, pin_data):
        """Update input pin states from Arduino response"""
        for pin_name, value in pin_data.items():
            if pin_name in self.input_pins:
                self.input_pins[pin_name] = value
    
    def create_command_string(self):
        """Create the command string to send to Arduino"""
        cmd_parts = []
        for pin_name, value in self.output_pins.items():
            cmd_parts.append(f"{pin_name}:{1 if value else 0}")
        return "<" + ",".join(cmd_parts) + ">"
    
    def print_status(self):
        """Print current status of all pins"""
        print("\n--- PIN STATUS ---")
        print("Output Pins (Controllable):")
        for pin_name, value in self.output_pins.items():
            status = "HIGH" if value else "LOW"
            print(f"  {pin_name}: {status}")
        
        print("Input Pins (Read from Arduino):")
        for pin_name, value in self.input_pins.items():
            status = "HIGH" if value else "LOW"
            print(f"  {pin_name}: {status}")
        print("------------------\n")

# Global pin manager
pin_manager = PinManager()

#========================
#========================
    # the functions

def setupSerial(baudRate, serialPortName):
    
    global  serialPort
    
    serialPort = serial.Serial(port= serialPortName, baudrate = baudRate, timeout=0, rtscts=True)

    print("Serial port " + serialPortName + " opened  Baudrate " + str(baudRate))

    waitForArduino()

#========================

def sendToArduino(stringToSend):
    
        # this adds the start- and end-markers before sending
    global startMarker, endMarker, serialPort
    
    stringWithMarkers = (startMarker)
    stringWithMarkers += stringToSend
    stringWithMarkers += (endMarker)

    serialPort.write(stringWithMarkers.encode('utf-8')) # encode needed for Python3

#==================

def sendPinCommand():
    """Send current pin states to Arduino"""
    command = pin_manager.create_command_string()
    print(f"Sending: {command}")
    sendToArduino(command[1:-1])  # Remove the < > markers since sendToArduino adds them

#==================

def recvLikeArduino():

    global startMarker, endMarker, serialPort, dataStarted, dataBuf, messageComplete

    if serialPort.inWaiting() > 0 and messageComplete == False:
        x = serialPort.read().decode("utf-8") # decode needed for Python3
        
        if dataStarted == True:
            if x != endMarker:
                dataBuf = dataBuf + x
            else:
                dataStarted = False
                messageComplete = True
        elif x == startMarker:
            dataBuf = ''
            dataStarted = True
    
    if (messageComplete == True):
        messageComplete = False
        return dataBuf
    else:
        return "XXX" 

#==================

def parseArduinoResponse(response):
    """Parse Arduino response and update input pin states"""
    if response == "XXX" or not response:
        return
    
    print(f"Arduino reply: {response}")
    
    # Parse the response format: GATE_REQUEST_A:0,GATE_REQUEST_B:1
    pin_data = {}
    pairs = response.split(',')
    
    for pair in pairs:
        if ':' in pair:
            pin_name, value_str = pair.split(':')
            pin_name = pin_name.strip()
            try:
                value = bool(int(value_str.strip()))
                pin_data[pin_name] = value
            except ValueError:
                print(f"Could not parse value for {pin_name}: {value_str}")
    
    # Update input pins
    pin_manager.update_input_pins(pin_data)

#==================

def waitForArduino():

    # wait until the Arduino sends 'Arduino is ready' - allows time for Arduino reset
    # it also ensures that any bytes left over from a previous message are discarded
    
    print("Waiting for Arduino to reset")
     
    msg = ""
    timeout_counter = 0
    max_timeout = 100  # 10 seconds timeout
    
    while msg.find("Arduino is ready") == -1:
        msg = recvLikeArduino()
        if not (msg == 'XXX'): 
            print(f"Received: {msg}")
        
        timeout_counter += 1
        if timeout_counter > max_timeout:
            print("Timeout waiting for Arduino. Continuing anyway...")
            break
        time.sleep(0.1)

#==================

def print_commands():
    """Print available commands"""
    print("\n--- AVAILABLE COMMANDS ---")
    print("Commands:")
    print("  set <pin_name> <0|1>  - Set pin state (e.g., 'set GATE_MOVING_A 1')")
    print("  status                - Show current pin status")
    print("  help                  - Show this help")
    print("  quit                  - Exit program")
    print("\nControllable pins:")
    for pin_name in pin_manager.output_pins.keys():
        print(f"  {pin_name}")
    print("-------------------------\n")

#==================

def handle_user_input():
    """Handle user commands for pin control"""
    try:
        import msvcrt
        if msvcrt.kbhit():
            command = input("\nEnter command (or 'help' for options): ").strip().lower()
            
            if command == 'quit':
                return False
            elif command == 'help':
                print_commands()
            elif command == 'status':
                pin_manager.print_status()
            elif command.startswith('set '):
                parts = command.split()
                if len(parts) == 3:
                    pin_name = parts[1].upper()
                    try:
                        value = int(parts[2])
                        if pin_manager.set_pin(pin_name, value):
                            sendPinCommand()
                    except ValueError:
                        print("Value must be 0 or 1")
                else:
                    print("Usage: set <pin_name> <0|1>")
            else:
                print("Unknown command. Type 'help' for available commands.")
    except ImportError:
        # msvcrt not available on non-Windows systems
        pass
    except EOFError:
        # Handle Ctrl+C or EOF
        return False
    
    return True

#====================
#====================
    # the program

print("Arduino Pin Controller")
print("Type 'help' for available commands")
print("Add '--test' argument to run in test mode without Arduino")

# Check for test mode
if len(sys.argv) > 1 and sys.argv[1] == '--test':
    TEST_MODE = True
    print("Running in TEST MODE - no Arduino connection")

if not TEST_MODE:
    # Try to find and connect to Arduino automatically
    def find_arduino_port():
        """Try to find Arduino on available COM ports"""
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        
        print("Available COM ports:")
        for port in ports:
            print(f"  {port.device} - {port.description}")
        
        # Look for common Arduino identifiers
        arduino_ports = []
        for port in ports:
            if any(keyword in port.description.upper() for keyword in ['CH340', 'ARDUINO', 'USB-SERIAL', 'FTDI']):
                arduino_ports.append(port.device)
        
        if arduino_ports:
            print(f"Potential Arduino port(s): {arduino_ports}")
            return arduino_ports[0]  # Return first potential Arduino port
        elif ports:
            print(f"No Arduino found, trying first available port: {ports[0].device}")
            return ports[0].device
        else:
            print("No COM ports found!")
            return None

    # Try to connect to Arduino
    arduino_port = find_arduino_port()
    if arduino_port:
        try:
            setupSerial(115200, arduino_port)
            print(f"Successfully connected to {arduino_port}")
        except Exception as e:
            print(f"Failed to connect to {arduino_port}: {e}")
            print("Please check your Arduino connection and try again.")
            print("Or run with '--test' flag to test without Arduino")
            exit(1)
    else:
        print("No COM ports available. Please connect your Arduino and try again.")
        print("Or run with '--test' flag to test without Arduino")
        exit(1)
else:
    print("Skipping Arduino connection in test mode")

count = 0
prevTime = time.time()

try:
    print("\nStarting main loop...")
    print("Press Ctrl+C to exit")
    pin_manager.print_status()
    
    while True:
        if not TEST_MODE:
            # Check for Arduino reply
            arduinoReply = recvLikeArduino()
            if not (arduinoReply == 'XXX'):
                parseArduinoResponse(arduinoReply)
        
        # Send pin states at intervals
        if time.time() - prevTime > 2.0:  # Increased interval to 2 seconds
            if not TEST_MODE:
                sendPinCommand()
            else:
                print(f"[TEST MODE] Would send: {pin_manager.create_command_string()}")
            
            prevTime = time.time()
            count += 1
            
            # Show status every 10 messages
            if count % 5 == 0:  # Reduced to every 5 for testing
                pin_manager.print_status()
        
        # Handle user input (Windows only)
        if not handle_user_input():
            break
            
        # Small delay to prevent excessive CPU usage
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nProgram interrupted by user")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    if 'serialPort' in globals() and not TEST_MODE:
        serialPort.close()
        print("Serial port closed")