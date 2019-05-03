#include <softPwm.h>
#include <wiringPi.h>
#include "motor_control.h"

int PA = 50;
int PB = 50;

void init_motor(){
	wiringPiSetup();

	pinMode(AIN1, OUTPUT);
	pinMode(AIN2, OUTPUT);
	pinMode(BIN1, OUTPUT);
	pinMode(BIN2, OUTPUT);
	pinMode(ENA, OUTPUT);
	pinMode(ENB, OUTPUT);

	softPwmCreate(ENA, 0, MAX);
	softPwmCreate(ENB, 0, MAX);	
}

void forward(){
	softPwmWrite(ENA, PA);
	softPwmWrite(ENB, PB);

	digitalWrite(AIN1, LOW);	
	digitalWrite(AIN2, HIGH);
	digitalWrite(BIN1, LOW);
	digitalWrite(BIN2, HIGH);
}

void stop(){
	softPwmWrite(ENA, 0);
	softPwmWrite(ENB, 0);

	digitalWrite(AIN1, LOW);	
	digitalWrite(AIN2, LOW);
	digitalWrite(BIN1, LOW);
	digitalWrite(BIN2, LOW);
}

void backward(){
	softPwmWrite(ENA, PA);
	softPwmWrite(ENB, PB);

	digitalWrite(AIN1, HIGH);	
	digitalWrite(AIN2, LOW);
	digitalWrite(BIN1, HIGH);
	digitalWrite(BIN2, LOW);
}

void left(){
	softPwmWrite(ENA, 30);
	softPwmWrite(ENB, 30);

	digitalWrite(AIN1, HIGH);	
	digitalWrite(AIN2, LOW);
	digitalWrite(BIN1, LOW);
	digitalWrite(BIN2, HIGH);
}

void right(){
	softPwmWrite(ENA, 30);
	softPwmWrite(ENB, 30);

	digitalWrite(AIN1, LOW);	
	digitalWrite(AIN2, HIGH);
	digitalWrite(BIN1, HIGH);
	digitalWrite(BIN2, LOW);
}

void setPWMA(int value){
	PA = value;
	softPwmWrite(ENA, PA);
}

void setPWMB(int value){
	PB = value;
	softPwmWrite(ENB, PB);
}

void setMotor(int left, int right){
	if( (right >=0) && (right <=100) ) {
		digitalWrite(AIN1,HIGH);
		digitalWrite(AIN2,LOW);
		softPwmWrite(ENA,right);
	}
	else if( (right <0) && (right >= -100) ){
		digitalWrite(AIN1,LOW);
		digitalWrite(AIN2,HIGH);
		softPwmWrite(ENA,0-right);
	}

	if( (left >=0) && (left <=100) ) {
		digitalWrite(BIN1,HIGH);
		digitalWrite(BIN2,LOW);
		softPwmWrite(ENB,left);
	}
	else if( (left <0) && (left >= -100) ){
		digitalWrite(BIN1,LOW);
		digitalWrite(BIN2,HIGH);
		softPwmWrite(ENB,0-left);
	}
}


/*
   int main(){
   init_motor();
   forward();
   while(1){
   delay(1);
   }
   return 0;	
   }
 */
