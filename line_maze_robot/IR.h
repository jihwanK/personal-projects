#ifndef _IR_H_
#define _IR_H_

#define CS 21
#define CLK 6
#define ADDR 5
#define DOUT 4

extern const int numSensors;
extern int sensor_values[5];
extern int calibratedMin[5];
extern int calibratedMax[5];
extern int last_value;

void init_IR();
void AnalogRead();
void Calibrate();
void ReadCalibrated();
void readLine();


#endif 
