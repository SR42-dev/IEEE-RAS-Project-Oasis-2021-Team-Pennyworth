//MOTOR1 PINS
int ena = 9;
int in1 = 3;
int in2 = 4;
int enb = 10;
int in4 = 5;
int in3 = 6;
#define del 100

void setup() {

  pinMode(ena, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(enb, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
Serial.begin(9600);
 
}

void loop() {
if(Serial.available()>0)
 {
 char a=Serial.read();
 Serial.println(a);
 if (a=='f')
 
 {
  analogWrite(ena, 255);
   analogWrite(enb, 255);
   digitalWrite(in1,HIGH);
  digitalWrite(in2,LOW);
  digitalWrite(in3,HIGH);
  digitalWrite(in4,LOW);

delay(110);
 digitalWrite(in1,LOW);
  digitalWrite(in2,LOW);
  digitalWrite(in3,LOW);
  digitalWrite(in4,LOW);
}


 if (a=='b')
 
 {
  analogWrite(ena, 255);
   analogWrite(enb, 255);
   digitalWrite(in2,HIGH);
  digitalWrite(in1,LOW);
  digitalWrite(in4,HIGH);
  digitalWrite(in3,LOW);

delay(110);
 digitalWrite(in1,LOW);
  digitalWrite(in2,LOW);
  digitalWrite(in3,LOW);
  digitalWrite(in4,LOW);
}
 
  if (a=='l')
 
 {
  analogWrite(ena, 255);
   analogWrite(enb, 255);
   digitalWrite(in1,HIGH);
  digitalWrite(in2,LOW);
  digitalWrite(in3,LOW);
  digitalWrite(in4,LOW);

delay(50);
 digitalWrite(in1,LOW);
  digitalWrite(in2,LOW);
  digitalWrite(in3,LOW);
  digitalWrite(in4,LOW);
}

 if (a=='r')
 
 {
  analogWrite(ena, 255);
   analogWrite(enb, 255);
   digitalWrite(in1,LOW);
  digitalWrite(in2,LOW);
  digitalWrite(in3,HIGH);
  digitalWrite(in4,LOW);

delay(50);
 digitalWrite(in1,LOW);
  digitalWrite(in2,LOW);
  digitalWrite(in3,LOW);
  digitalWrite(in4,LOW);
}


 
 }
}
