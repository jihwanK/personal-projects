#include "IR.h"
#include <wiringPi.h>
#include <softPwm.h>
#include <stdio.h>
#include <pthread.h>
#include <time.h>

const int numSensors = 5;
int sensor_values[5] = {0, 0, 0, 0, 0};
int calibratedMin[5] = {0, 0, 0, 0, 0};
int calibratedMax[5] = {1023, 1023, 1023, 1023, 1023};
int last_value = 0;


void init_IR(void){
	wiringPiSetup();
	pinMode(CLK, OUTPUT);
	pinMode(ADDR, OUTPUT);
	pinMode(CS, OUTPUT);
	pinMode(DOUT, INPUT);
	pullUpDnControl(DOUT, PUD_UP);
}

void AnalogRead(void){
	int i, j;
	int value[6] = {0, };
	
	for(j = 0; j < numSensors + 1; j++){
		digitalWrite(CS, LOW);

		for(i = 0; i < 4; i++){
			// sent 4-bt Address
			if(((j) >> (3 - i)) & 0x01 )
				digitalWrite(ADDR, HIGH);
			else
				digitalWrite(ADDR, LOW);
			delayMicroseconds(1);	
			// read MSB 4-bit data
			value[j] <<= 1;
			if(digitalRead(DOUT))
				value[j] |= 0x01;
			
			digitalWrite(CLK, HIGH);
			delayMicroseconds(3);	
			digitalWrite(CLK, LOW);
		} 

		for(i = 0; i < 6; i++){
			// read LSB 8-bit data
			value[j] <<= 1;
			if(digitalRead(DOUT)){
				value[j] |= 0x01;
			}
			digitalWrite(CLK, HIGH);
			delayMicroseconds(3);	
			digitalWrite(CLK, LOW);
		} 
		delay(1);
		digitalWrite(CS, HIGH);
	} 

	for(i = 0; i < numSensors ; i++){
		sensor_values[i] = value[i + 1];
	}

	return;
}

void Calibrate(void){
	int i, j;
	int max_sensor_values[5], min_sensor_values[5];
	for(i = 0 ; i <5; i++){
		max_sensor_values[i] = 0;
		min_sensor_values[i] = 0;
	}

	for(j = 0 ; j < 10 ; j++){
		AnalogRead();

		for(i = 0; i < 5; i++){
			// set the max we found THIS time
			if((j == 0) || max_sensor_values[i] < sensor_values[i])
				max_sensor_values[i] = sensor_values[i];
		
			// set the min we found THIS time
			if((j == 0) || min_sensor_values[i] > sensor_values[i])
				min_sensor_values[i] = sensor_values[i];
		} 
	} 

	for(i = 0; i < numSensors; i++){
		if(min_sensor_values[i] > calibratedMin[i])
			calibratedMin[i] = min_sensor_values[i];
		if(max_sensor_values[i] < calibratedMax[i])
			calibratedMax[i] = max_sensor_values[i];
	}
	return;
}  


void ReadCalibrated(void){

	int i, j;
	int value = 0;
	int denominator = 1;
	// read the needed values

	AnalogRead();

	for( i = 0 ; i < numSensors ; i++){
		denominator = calibratedMax[i] - calibratedMin[i];	

		if( denominator != 0 ){
			value = (sensor_values[i] - calibratedMin[i])*1000/denominator;
		}
		if( value < 0 )
			value = 0;
		else if( value > 1000 )
			value = 1000;

		sensor_values[i] = value;
	} 

	return;
} 

void readLine(void){

	int i;

	int avg = 0;
	int sum = 0;
	int on_line = 0;
	int value = 0;

	ReadCalibrated();

	for( i = 0 ; i < numSensors ; i++){
		value = sensor_values[i];

		value = 1000 - value;
		// keep track of whether we see the line at all
		if( value > 200 )
			on_line = 1;

		// only average in values that are above a noise threshold
		if( value > 50 ){
			avg += value*(i*1000); // weighted total
			sum += value; // for denominator
		} 

		if( on_line != 1 ){
			// If it last read to the left center, return 0;
			if( last_value < (numSensors - 1)*1000/2 ){
				last_value = 0;
			} 
			else
				last_value = (numSensors - 1)*1000;
			

		} // on_line if END
		else
			last_value = avg/sum;		
	}
} 

/*
int main(void){

	init_IR();

	while(1){
		AnalogRead();
		printf("%d, %d, %d, %d, %d\n", sensor_values[0], sensor_values[1],
				sensor_values[2], sensor_values[3],	sensor_values[4]);
		delay(500);
	}

}
*/

