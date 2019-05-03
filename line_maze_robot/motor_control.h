#ifndef _MOTOR_H_
#define _MOTOR_H_

#define AIN1 26
#define AIN2 23
#define BIN1 28
#define BIN2 29
#define ENA 22
#define ENB 25

#define MAX 100

extern int PA;
extern int PB;

void init_motor();
void forward();
void stop();
void backward();
void left();
void right();
void setPWMA(int value);
void setPWMB(int value);
void setMotor(int left, int right);
#endif
