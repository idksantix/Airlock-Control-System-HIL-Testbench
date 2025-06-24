import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import time
import json

class ArduinoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Arduino Control Panel")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Serial connection
        self.ser = None
        self.connected = False
        
        # Data storage
        self.output_states = {
            'PRESENCE_FRONT': False,
            'PRESENCE_MIDDLE': False,
            'PRESENCE_BACK': False,
            'GATE_SAFETY_A': False,
            'GATE_SAFETY_B': False,
            'GATE_MOVING_A': False,
            'GATE_MOVING_B': False
        }
        
        self.input_states = {
            'GATE_REQUEST_A': False,
            'GATE_REQUEST_B': False
        }
        
        # GUI Variables
        self.output_vars = {}
        self.input_labels = {}
        
        self.setup_gui()
        self.start_reading_thread()
        
    def setup_gui(self):
        # Main title
        title_label = tk.Label(self.root, text="Arduino Control Panel", 
                              font=('Arial', 20, 'bold'), 
                              fg='white', bg='#2b2b2b')
        title_label.pack(pady=20)
        
        # Connection frame
        conn_frame = tk.Frame(self.root, bg='#2b2b2b')
        conn_frame.pack(pady=10)
        
        tk.Label(conn_frame, text="COM Port:", 
                font=('Arial', 12), fg='white', bg='#2b2b2b').pack(side=tk.LEFT, padx=5)
        
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(conn_frame, textvariable=self.port_var, 
                                      values=self.get_serial_ports(), width=15)
        self.port_combo.pack(side=tk.LEFT, padx=5)
        
        self.connect_btn = tk.Button(conn_frame, text="Connect", 
                                   command=self.toggle_connection,
                                   bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = tk.Button(conn_frame, text="Refresh Ports", 
                                   command=self.refresh_ports,
                                   bg='#2196F3', fg='white', font=('Arial', 10))
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Disconnected", 
                                   font=('Arial', 12), fg='red', bg='#2b2b2b')
        self.status_label.pack(pady=5)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Outputs frame (left side)
        outputs_frame = tk.LabelFrame(main_frame, text="Outputs (Send to Arduino)", 
                                    font=('Arial', 14, 'bold'), 
                                    fg='white', bg='#2b2b2b', 
                                    labelanchor='n', bd=2, relief='groove')
        outputs_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=10)
        
        # Create output toggles
        for i, (name, state) in enumerate(self.output_states.items()):
            frame = tk.Frame(outputs_frame, bg='#2b2b2b')
            frame.pack(pady=8, padx=10, fill='x')
            
            var = tk.BooleanVar(value=state)
            self.output_vars[name] = var
            
            # Create custom toggle button
            toggle_btn = tk.Button(frame, text=f"{name}: OFF", 
                                 command=lambda n=name: self.toggle_output(n),
                                 bg='#f44336', fg='white', 
                                 font=('Arial', 11, 'bold'),
                                 relief='raised', bd=3)
            toggle_btn.pack(fill='x')
            
            # Store button reference for updating
            setattr(self, f"{name}_btn", toggle_btn)
        
        # Inputs frame (right side)
        inputs_frame = tk.LabelFrame(main_frame, text="Inputs (Receive from Arduino)", 
                                   font=('Arial', 14, 'bold'), 
                                   fg='white', bg='#2b2b2b', 
                                   labelanchor='n', bd=2, relief='groove')
        inputs_frame.pack(side=tk.RIGHT, fill='both', expand=True, padx=10)
        
        # Create input displays
        for name, state in self.input_states.items():
            frame = tk.Frame(inputs_frame, bg='#2b2b2b')
            frame.pack(pady=15, padx=10, fill='x')
            
            label = tk.Label(frame, text=f"{name}: OFF", 
                           font=('Arial', 12, 'bold'), 
                           fg='white', bg='#f44336',
                           relief='raised', bd=3, pady=10)
            label.pack(fill='x')
            self.input_labels[name] = label
        
        # Control buttons frame
        control_frame = tk.Frame(self.root, bg='#2b2b2b')
        control_frame.pack(pady=10)
        
        send_btn = tk.Button(control_frame, text="Send All Outputs", 
                           command=self.send_data,
                           bg='#FF9800', fg='white', 
                           font=('Arial', 12, 'bold'))
        send_btn.pack(side=tk.LEFT, padx=10)
        
        clear_btn = tk.Button(control_frame, text="Clear All Outputs", 
                            command=self.clear_all_outputs,
                            bg='#9C27B0', fg='white', 
                            font=('Arial', 12, 'bold'))
        clear_btn.pack(side=tk.LEFT, padx=10)
    
    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def refresh_ports(self):
        self.port_combo['values'] = self.get_serial_ports()
    
    def toggle_connection(self):
        if not self.connected:
            self.connect_serial()
        else:
            self.disconnect_serial()
    
    def connect_serial(self):
        port = self.port_var.get()
        if not port:
            messagebox.showerror("Error", "Please select a COM port")
            return
        
        try:
            self.ser = serial.Serial(port, 115200, timeout=1)
            time.sleep(2)  # Wait for Arduino to initialize
            self.connected = True
            self.connect_btn.config(text="Disconnect", bg='#f44336')
            self.status_label.config(text=f"Connected to {port}", fg='green')
            messagebox.showinfo("Success", f"Connected to {port}")
        except serial.SerialException as e:
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")
    
    def disconnect_serial(self):
        if self.ser:
            self.ser.close()
            self.ser = None
        self.connected = False
        self.connect_btn.config(text="Connect", bg='#4CAF50')
        self.status_label.config(text="Disconnected", fg='red')
    
    def toggle_output(self, name):
        current_state = self.output_states[name]
        new_state = not current_state
        self.output_states[name] = new_state
        self.output_vars[name].set(new_state)
        
        # Update button appearance
        btn = getattr(self, f"{name}_btn")
        if new_state:
            btn.config(text=f"{name}: ON", bg='#4CAF50')
        else:
            btn.config(text=f"{name}: OFF", bg='#f44336')
        
        # Auto-send when toggled
        self.send_data()
    
    def clear_all_outputs(self):
        for name in self.output_states:
            self.output_states[name] = False
            self.output_vars[name].set(False)
            btn = getattr(self, f"{name}_btn")
            btn.config(text=f"{name}: OFF", bg='#f44336')
        self.send_data()
    
    def send_data(self):
        if not self.connected or not self.ser:
            messagebox.showwarning("Warning", "Not connected to Arduino")
            return
        
        # Format data as expected by Arduino: <VAR1:VALUE,VAR2:VALUE,...>
        data_parts = []
        for name, state in self.output_states.items():
            value = "1" if state else "0"
            data_parts.append(f"{name}:{value}")
        
        message = "<" + ",".join(data_parts) + ">"
        
        try:
            self.ser.write(message.encode())
            print(f"Sent: {message}")
        except serial.SerialException as e:
            messagebox.showerror("Error", f"Failed to send data: {str(e)}")
    
    def read_arduino_data(self):
        if not self.connected or not self.ser:
            return
        
        try:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode().strip()
                if line.startswith('<') and line.endswith('>'):
                    # Parse the received data
                    data = line[1:-1]  # Remove < and >
                    pairs = data.split(',')
                    
                    for pair in pairs:
                        if ':' in pair:
                            name, value = pair.split(':')
                            if name in self.input_states:
                                self.input_states[name] = value == '1'
                                self.update_input_display(name, value == '1')
                    
                    print(f"Received: {line}")
        except serial.SerialException:
            pass
    
    def update_input_display(self, name, state):
        if name in self.input_labels:
            label = self.input_labels[name]
            if state:
                label.config(text=f"{name}: ON", bg='#4CAF50')
            else:
                label.config(text=f"{name}: OFF", bg='#f44336')
    
    def start_reading_thread(self):
        def read_loop():
            while True:
                self.read_arduino_data()
                time.sleep(0.1)  # Read every 100ms
        
        thread = threading.Thread(target=read_loop, daemon=True)
        thread.start()
    
    def on_closing(self):
        self.disconnect_serial()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ArduinoGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop() 