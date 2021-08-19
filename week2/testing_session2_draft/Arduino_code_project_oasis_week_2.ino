#define ena 0
#define enb 0
#define lf 0
#define lb 0
#define rf 0
#define rb 0
#define del 50

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
pinMode(ena, OUTPUT);
pinMode(enb, OUTPUT);
pinMode(lf, OUTPUT);
pinMode(lb, OUTPUT);
pinMode(rf, OUTPUT);
pinMode(rb, OUTPUT);
analogWrite(ena, 255);
analogWrite(enb, 255);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available()>0){
    char cg = Serial.read();
if (cg == 'f'){
  digitalWrite(lf, HIGH);
  digitalWrite(lb, LOW);
  digitalWrite(rf, HIGH);
  digitalWrite(rb, LOW);
  delay(del);
    digitalWrite(lf, LOW);
  digitalWrite(lb, LOW);
  digitalWrite(rf, LOW);
  digitalWrite(rb, LOW);
}
if (cg == 'l'){
  digitalWrite(lf, LOW);
  digitalWrite(lb, HIGH);
  digitalWrite(rf, HIGH);
  digitalWrite(rb, LOW);
  delay(del);
    digitalWrite(lf, LOW);
  digitalWrite(lb, LOW);
  digitalWrite(rf, LOW);
  digitalWrite(rb, LOW);
}
if (cg == 'r'){
  digitalWrite(lf, HIGH);
  digitalWrite(lb, LOW);
  digitalWrite(rf, LOW);
  digitalWrite(rb, HIGH);
  delay(del);
    digitalWrite(lf, LOW);
  digitalWrite(lb, LOW);
  digitalWrite(rf, LOW);
  digitalWrite(rb, LOW);
}
if (cg == 's'){
  digitalWrite(lf, LOW);
  digitalWrite(lb, LOW);
  digitalWrite(rf, LOW);
  digitalWrite(rb, LOW);
  delay(del);
}
}
}
