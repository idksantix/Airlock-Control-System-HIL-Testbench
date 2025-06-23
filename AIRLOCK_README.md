# Airlock HIL Simulator

Hardware-In-the-Loop (HIL) simulator for testing airlock firmware for ERC 2025 Challenge 2, Subtask 1.

## Overview

This GUI application simulates a rover moving through a three-zone airlock system with two gates. It communicates with an ESP32/Arduino running the airlock firmware via serial communication.

## Features

- **Visual Simulation**: Real-time visualization of airlock zones, gates, and rover
- **Interactive Control**: Move rover using mouse drag or arrow keys
- **Sensor Simulation**: 
  - Presence sensors for each zone (FRONT, MIDDLE, BACK)
  - Gate safety sensors that trigger when rover is near gates
- **Gate Animation**: Smooth gate opening/closing animations
- **Serial Communication**: Bidirectional communication with Arduino/ESP32
- **Safety Logic**: Gates won't close when rover is in safety zone

## System Architecture

### Zones
- **Front Zone**: 408mm (scaled)
- **Middle Zone**: 560mm (scaled)
- **Back Zone**: 186mm (scaled)

### Sensors
1. **Presence Sensors**: 
   - `PRESENCE_FRONT`: Triggered when rover center is in front zone
   - `PRESENCE_MIDDLE`: Triggered when rover center is in middle zone
   - `PRESENCE_BACK`: Triggered when rover center is in back zone

2. **Gate Safety Sensors**:
   - `GATE_SAFETY_A`: Triggered when any part of rover is near Gate A
   - `GATE_SAFETY_B`: Triggered when any part of rover is near Gate B

### Communication Protocol
- **To Arduino**: `<PRESENCE_FRONT:1,PRESENCE_MIDDLE:0,PRESENCE_BACK:0,GATE_SAFETY_A:0,GATE_SAFETY_B:0,GATE_MOVING_A:0,GATE_MOVING_B:0>`
- **From Arduino**: `<GATE_REQUEST_A:1,GATE_REQUEST_B:0>`

## Installation

1. Ensure Python 3.x is installed
2. Install required dependencies:
   ```bash
   pip install pyserial
   ```

## Usage

1. Connect your Arduino/ESP32 with the airlock firmware
2. Run the GUI application:
   ```bash
   python airlock_gui.py
   ```
3. Select the appropriate COM port from the dropdown
4. Click "Connect" to establish serial communication
5. Use mouse or arrow keys to move the rover through the airlock

## Controls

- **Mouse**: Click and drag the rover to move it
- **Arrow Keys**: Use Left/Right arrows for precise movement
- **Gates**: Automatically controlled by Arduino firmware based on sensor states

## Visual Indicators

- **Green**: Active/Open/Safe
- **Red**: Inactive/Closed/Danger
- **Yellow**: Moving/Transitioning
- **Dashed Lines**: Sensor trigger zones

## Testing Scenarios

1. **Basic Transit**: Move rover from front to back through both gates
2. **Safety Test**: Position rover in gate safety zone and observe gate behavior
3. **Bidirectional**: Test movement in both directions
4. **Edge Cases**: Test behavior at zone boundaries

## Troubleshooting

- **Connection Issues**: Ensure correct COM port and Arduino is properly powered
- **Gate Not Responding**: Check Arduino serial monitor for debug messages
- **Sensor Not Triggering**: Verify rover is fully within sensor zone boundaries

## Development Notes

- The application uses threading for smooth animations and serial communication
- Gate animations are frame-rate independent
- Collision detection prevents rover from passing through closed gates
- All sensor states are updated in real-time and sent via serial 