// This is very similar to Example 3 - Receive with start- and end-markers
//    in Serial Input Basics   http://forum.arduino.cc/index.php?topic=396450.0

#include <Arduino.h>

const byte numChars = 256;
char receivedChars[numChars];

boolean newData = false;

byte ledPin = 25; // the onboard LED
#define PRESENCE_FRONT_PIN 23
#define PRESENCE_MIDDLE_PIN 22
#define PRESENCE_BACK_PIN 21
#define GATE_SAFETY_A_PIN 19
#define GATE_SAFETY_B_PIN 18
#define GATE_REQUEST_A_PIN 5
#define GATE_REQUEST_B_PIN 4
#define GATE_MOVING_A_PIN 2
#define GATE_MOVING_B_PIN 15

struct IOpins
{
    bool PRESENCE_FRONT=false;
    bool PRESENCE_MIDDLE=false;
    bool PRESENCE_BACK=false;
    bool GATE_SAFETY_A=false;
    bool GATE_SAFETY_B=false;
    bool GATE_REQUEST_A=false;
    bool GATE_REQUEST_B=false;
    bool GATE_MOVING_A=false;
    bool GATE_MOVING_B=false;
};

IOpins ioPins;
//===============

void setup()
{

    Serial.begin(115200);
    
    pinMode(PRESENCE_FRONT_PIN, OUTPUT);
    pinMode(PRESENCE_MIDDLE_PIN, OUTPUT);
    pinMode(PRESENCE_BACK_PIN, OUTPUT);
    pinMode(GATE_SAFETY_A_PIN, OUTPUT);
    pinMode(GATE_SAFETY_B_PIN, OUTPUT);
        

    pinMode(GATE_REQUEST_A_PIN, INPUT_PULLUP);
    pinMode(GATE_REQUEST_B_PIN, INPUT_PULLUP);
    pinMode(GATE_MOVING_A_PIN, OUTPUT);
     pinMode(GATE_MOVING_B_PIN, OUTPUT);
    pinMode(ledPin, OUTPUT);

    digitalWrite(ledPin, HIGH);
    delay(200);
    digitalWrite(ledPin, LOW);
    delay(200);
    digitalWrite(ledPin, HIGH);

    Serial.println("<Arduino is ready>");
}

//===============

void loop()
{
    recvWithStartEndMarkers();
    executeLogic();
    processPins();
}
void executeLogic()
{
    
    if (newData)
    {
        int i = 0;

        
        while (receivedChars[i] != '>' && receivedChars[i] != '\0' )
        {

            // Character-by-character parsing
            char varName[32] = "";
            bool varValue = false; // Variable to store the boolean value
            int nameIndex = 0;
            // Skip the '<' if it's at the beginning
        

            // Parse char by char until we hit ':'
            while (receivedChars[i] != ':' && receivedChars[i] != '\0' && nameIndex < 31)
            {
                varName[nameIndex] = receivedChars[i];
                nameIndex++;
                i++;
            }
            varName[nameIndex] = '\0'; // Null terminate the string

            // Move past the ':' character
            if (receivedChars[i] == ':')
            {
                i++;
                // Parse the next character for the value
                if (receivedChars[i] == '1')
                {
                    varValue = true;
                }
                else if (receivedChars[i] == '0')
                {
                    varValue = false;
                }
                // Set the appropriate struct member based on the key
                if (strcmp(varName, "PRESENCE_FRONT") == 0)
                {
                    ioPins.PRESENCE_FRONT = varValue;
                }
                else if (strcmp(varName, "PRESENCE_MIDDLE") == 0)
                {
                    ioPins.PRESENCE_MIDDLE = varValue;
                }
                else if (strcmp(varName, "PRESENCE_BACK") == 0)
                {
                    ioPins.PRESENCE_BACK = varValue;
                }
                else if (strcmp(varName, "GATE_SAFETY_A") == 0)
                {
                    ioPins.GATE_SAFETY_A = varValue;
                }
                else if (strcmp(varName, "GATE_SAFETY_B") == 0)
                {
                    ioPins.GATE_SAFETY_B = varValue;
                }
                else if (strcmp(varName, "GATE_MOVING_A") == 0)
                {
                    ioPins.GATE_MOVING_A = varValue;
                }
                else if (strcmp(varName, "GATE_MOVING_B") == 0)
                {
                    ioPins.GATE_MOVING_B = varValue;
                }
                i+=2;
            }
        }
        replyToPython();
        newData = false;
    }
    // Get next token
}
void processPins()
{
    
    digitalWrite(PRESENCE_FRONT_PIN, ioPins.PRESENCE_FRONT ? HIGH : LOW);
    digitalWrite(PRESENCE_MIDDLE_PIN, ioPins.PRESENCE_MIDDLE ? HIGH : LOW);
    digitalWrite(PRESENCE_BACK_PIN, ioPins.PRESENCE_BACK ? HIGH : LOW);
    digitalWrite(GATE_SAFETY_A_PIN, ioPins.GATE_SAFETY_A ? HIGH : LOW);
    digitalWrite(GATE_SAFETY_B_PIN, ioPins.GATE_SAFETY_B ? HIGH : LOW);
    
    digitalWrite(GATE_MOVING_B_PIN, ioPins.GATE_MOVING_B ? HIGH : LOW);
    digitalWrite(GATE_MOVING_A_PIN, ioPins.GATE_MOVING_A ? HIGH : LOW);
    ioPins.GATE_REQUEST_A = digitalRead(GATE_REQUEST_A_PIN);
    ioPins.GATE_REQUEST_B = digitalRead(GATE_REQUEST_B_PIN);
}
//===============

void recvWithStartEndMarkers()
{
    static boolean recvInProgress = false;
    static int ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false)
    {
        rc = Serial.read();

        if (recvInProgress == true)
        {
            if (rc != endMarker)
            {
                receivedChars[ndx] = rc;

                ndx++;

            }
            else
            {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker)
        {
            recvInProgress = true;
        }
    }
}

//===============

void replyToPython()
{

    Serial.print("<GATE_REQUEST_A:");
    Serial.print(ioPins.GATE_REQUEST_A);
    Serial.print(",GATE_REQUEST_B:");
    Serial.print(ioPins.GATE_REQUEST_B);
    Serial.println(">");
    // change the state of the LED everytime a reply is sent
}

//===============