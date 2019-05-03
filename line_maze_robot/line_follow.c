#include "motor_control.h"
#include <wiringPi.h>
#include <stdio.h>
#include "IR.h"

int maximum = 60;
int integral = 0;
int last_proportional = 0;
int proportional = 0;
int derivate = 0;

int flag = 0;
int turning_left = 0;
int turning_right = 0;

int main()
{
	int i;
	init_IR();
	init_motor();
	stop();
	/*
	printf(">>> Calibraing..... ");

	for(i = 0; i < 100; i++){
		printf("%d", i);
		if(i < 25 || i >=75){
			right();
			setPWMA(30);
			setPWMB(30);
		}
		else{
			left();
			setPWMA(30);
			setPWMB(30);
		}
	Calibrate();
	}
	printf("\n>>> Complete the calibration:\n");
	*/
	stop();
	printf("	Calibr. max: %d   |   Calibr. min: %d\n", calibratedMax, calibratedMin);

	printf(">>> Start line following !!!\n");
	forward();

	//while(1){
	for(int k = 0; k < 400; k++){
		readLine();
		int position = last_value;
		
		if(sensor_values[0] > 900 && sensor_values[1] > 900 && sensor_values[2] &&
		   sensor_values[3] > 900 && sensor_values[4] > 900){
			setPWMA(0);
			setPWMA(0);
		}
		else{
			// the p term should be 0 when we are on the line
			proportional = position - 2250;
			
			// compute the d (change) and i (sum) of the position
			derivate = proportional - last_proportional;
			integral += proportional;
			
			// remember the last position
			last_proportional = proportional;

			int power_diff = proportional/10 + derivate;//  integral/10000 + derivate;
			
			if(sensor_values[0] < 300 && sensor_values[2] < 300){
				flag = 1;
				turning_left = 1;
				printf("-------- left start 1 -------\n"); 
			}
			if((sensor_values[0] > 300 && sensor_values[2] < 300) && flag == 1){
				flag = 2;
				printf("-------- left start 2 -------\n"); 
			}
			if((sensor_values[0] < 300 && sensor_values[2] < 300) && flag == 2 
					&& turning_left == 1){
				flag = 3;
				printf("------- left finish 1 -------\n");
			}
			if((sensor_values[0] > 300 && sensor_values[2] < 300) && flag == 3
					&& turning_left == 1){
				flag = 0;
				turning_left = 0;
				printf("------- left 4 finish 2-------\n");
			}
			if((sensor_values[4] < 300 && sensor_values[2] < 300) && flag == 2 
					&& turning_left == 1){
				flag = 3;
				printf("------- left -> right 1-------\n");
			}
			if((sensor_values[4] > 300 && sensor_values[2] < 300) && flag == 3
					&& turning_left == 1){
				flag = 2;
				turning_left = 0;
				turning_right = 1;
				printf("------- left -> right 2 -------\n");
			}
		
			
			if(sensor_values[4] < 300 && sensor_values[2] < 300){
				flag = 1;
				turning_right = 1;
				printf("------- right start 1 -------\n");
			}
			if((sensor_values[4] > 300 && sensor_values[2] < 300) && flag == 1){
				flag = 2;
				printf("------- right start 2 -------\n");
			}
			if((sensor_values[4] < 300 && sensor_values[2] < 300) && flag == 2
					&& turning_right == 1){
				flag = 3;
				printf("------- right finish 1 -------\n");
			}
			if((sensor_values[4] > 300 && sensor_values[2] < 300) && flag == 3
					&& turning_right == 1){
				flag = 0;
				turning_right = 0;
				printf("------- right finish 2 -------\n");
			}
			if((sensor_values[0] < 300 && sensor_values[2] < 300) && flag == 2 
					&& turning_right == 1){
				flag = 3;
				printf("------- right -> left 1 -------\n");
			}
			if((sensor_values[0] > 300 && sensor_values[2] < 300) && flag == 3
					&& turning_right == 1){
				flag = 2;
				turning_right = 0;
				turning_left = 1;
				printf("------ right -> left 2 -------\n");
			}

			if(power_diff > maximum)
				power_diff = maximum;
			if(power_diff < -maximum)
				power_diff = -maximum;
		/*		
			if(-50 < proportional && proportional < 50){
				power_diff /= 1.5;
				maximum = 70;
			}else{
				//power_diff *= 1.3;
				maximum = 60;
			}
		*/	
			printf("(%d) >> P: %d (%d), I: %d, D: %d >> vel: %d >> %d %d %d %d %d %d\n", position, proportional, maximum, derivate, integral, power_diff,
					sensor_values[0], sensor_values[1], sensor_values[2], sensor_values[3], sensor_values[4]);

			if(power_diff < 0){
				setPWMA(maximum + power_diff);
				setPWMB(maximum);

			}
			else{
				setPWMA(maximum);
				setPWMB(maximum - power_diff);
			}
		}
	}
	stop();

	return 0;
}
