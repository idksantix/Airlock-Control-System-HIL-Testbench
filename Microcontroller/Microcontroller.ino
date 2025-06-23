#define PRESENCE_FRONT_PIN 36
#define PRESENCE_MIDDLE_PIN 39
#define PRESENCE_BACK_PIN 34
#define GATE_SAFETY_A_PIN 35
#define GATE_SAFETY_B_PIN 32
#define GATE_REQUEST_A_PIN 33
#define GATE_REQUEST_B_PIN 25
#define GATE_MOVING_A_PIN 26
#define GATE_MOVING_B_PIN 27

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

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(PRESENCE_FRONT_PIN,INPUT_PULLUP);
  pinMode(PRESENCE_MIDDLE_PIN,INPUT_PULLUP);
  pinMode(PRESENCE_BACK_PIN,INPUT_PULLUP);
  pinMode(GATE_SAFETY_A_PIN, INPUT_PULLUP);
  pinMode(GATE_SAFETY_B_PIN, INPUT_PULLUP);
        

  pinMode(GATE_REQUEST_A_PIN, OUTPUT);
  pinMode(GATE_REQUEST_B_PIN, OUTPUT);
  pinMode(GATE_MOVING_A_PIN, INPUT_PULLUP);
  pinMode(GATE_MOVING_B_PIN, INPUT_PULLUP);
}
void processPins()
{
  // Read input pins and store in IOpins struct
  ioPins.PRESENCE_FRONT = digitalRead(PRESENCE_FRONT_PIN);
  ioPins.PRESENCE_MIDDLE = digitalRead(PRESENCE_MIDDLE_PIN);
  ioPins.PRESENCE_BACK = digitalRead(PRESENCE_BACK_PIN);
  ioPins.GATE_SAFETY_A = digitalRead(GATE_SAFETY_A_PIN);
  ioPins.GATE_SAFETY_B = digitalRead(GATE_SAFETY_B_PIN);
  ioPins.GATE_MOVING_A = digitalRead(GATE_MOVING_A_PIN);
  ioPins.GATE_MOVING_B = digitalRead(GATE_MOVING_B_PIN);
  
  // Write output pins based on IOpins struct values
  digitalWrite(GATE_REQUEST_A_PIN, ioPins.GATE_REQUEST_A);
  digitalWrite(GATE_REQUEST_B_PIN, ioPins.GATE_REQUEST_B);
}
void executeLogic()
{
  if (ioPins.PRESENCE_FRONT)
    ioPins.GATE_REQUEST_A=true;
  else 
    ioPins.GATE_REQUEST_A=false;
  if (ioPins.PRESENCE_MIDDLE)
    ioPins.GATE_REQUEST_B=true;
  else 
    ioPins.GATE_REQUEST_B=false;
    
}
void loop() {
  // put your main code here, to run repeatedly:
processPins();
executeLogic();
}
