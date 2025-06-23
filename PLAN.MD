# Airlock GUI Development Plan

## Overview
Develop a Hardware-In-the-Loop (HIL) GUI application for testing the airlock firmware in Challenge 2, Subtask 1. The GUI will simulate a rover moving through a three-zone airlock system with two gates.

## System Architecture

### Components
1. **Rover Simulation**: Visual representation of Husarion Lynx robot (638mm x 1154mm)
2. **Airlock Zones**:
   - Front Zone (408mm)
   - Middle Zone (560mm) 
   - Back Zone (remaining space)
3. **Gates**:
   - Gate A (between Front and Middle zones)
   - Gate B (between Middle and Back zones)
4. **Sensors**:
   - Presence sensors (PRESENCE_FRONT, PRESENCE_MIDDLE, PRESENCE_BACK)
   - Gate safety sensors (GATE_SAFETY_A, GATE_SAFETY_B)

### Communication Protocol
- Serial communication at 115200 baud
- Format: `<VAR1:VALUE,VAR2:VALUE,...>`
- Send to Arduino: Sensor states
- Receive from Arduino: Gate requests

## Development Steps

### Phase 1: GUI Layout
1. Create main window with airlock visualization
2. Draw three zones with clear boundaries
3. Add gate representations at zone boundaries
4. Create rover sprite that can move with mouse/keyboard
5. Add sensor trigger zones (clearly labeled)

### Phase 2: Rover Control
1. Implement mouse drag control for rover
2. Add keyboard control (arrow keys)
3. Implement collision detection with walls
4. Add smooth movement animation

### Phase 3: Sensor Logic
1. Implement presence sensor triggers based on rover position
2. Implement gate safety sensors (triggered when rover near gates)
3. Visual feedback for active sensors (color changes/indicators)

### Phase 4: Serial Communication
1. Establish serial connection (based on arduino_gui.py example)
2. Send sensor states to Arduino
3. Receive gate commands from Arduino
4. Update gate states based on commands

### Phase 5: Gate Animation
1. Implement gate opening/closing animations
2. Add GATE_MOVING status during animation
3. Prevent rover movement through closed gates

### Phase 6: Safety Features
1. Implement gate safety logic (cannot close on rover)
2. Add visual warnings for unsafe conditions
3. Log all operations for debugging

## Technical Specifications

### Dimensions (from airlock diagram)
- Total airlock: 1154mm width
- Front zone: 408mm
- Middle zone: 560mm
- Back zone: ~186mm (calculated)
- Rover size: 638mm x [width based on Lynx specs]

### Sensor Specifications
- Presence sensors: Triggered when rover center is in zone
- Gate safety sensors: Triggered when any part of rover is within gate danger zone
- All sensors send HIGH (1) when triggered, LOW (0) when clear

### Visual Design
- Clear zone boundaries with labels
- Color-coded sensor states (green=clear, red=triggered)
- Gate states (green=open, red=closed, yellow=moving)
- Rover representation with clear orientation

## Testing Requirements
1. Test all sensor combinations
2. Verify gate safety (no closing on rover)
3. Test bi-directional movement through airlock
4. Verify serial communication integrity
5. Test edge cases (rover at boundaries, multiple zone triggers)

## Success Criteria
- Rover can successfully traverse airlock in both directions
- Gates never open simultaneously
- Safety sensors prevent dangerous operations
- Clear visual feedback for all states
- Reliable serial communication with Arduino 