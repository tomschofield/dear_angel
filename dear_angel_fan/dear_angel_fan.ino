//writes to relay switching on leaf blowing fan on any serial message
int inbyt=0;
int pin = 6;

void setup(){
  //start serial and set the pin mode
  Serial.begin(9600);
  pinMode(pin, OUTPUT);
}

void loop(){
  //if we have a new message then write into our global
  while (Serial.available() > 0) {
     inbyt = (int)Serial.read();
     Serial.println(inbyt);
     
  }
  //if the global (inbyt) is not the default (0) then write to the pin
  if(inbyt!=0){
   digitalWrite(pin, HIGH);
   delay((inbyt-48)*1000);
   digitalWrite(pin, LOW);
   //set the global back to default
   inbyt=0;
  }
}
