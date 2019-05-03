#include <wiringPi.h>
#include <stdio.h>
#include <softPwm.h>
#include <signal.h>
#include <stdlib.h>
#include <unistd.h>

#include "stack.h"
#include "motor_control.h"
#include "IR.h"
#include <pthread.h>

int LEFT = 1;
int STRAIGHT = 2;
int RIGHT = 3;

int N_LEFT = (-1);
int N_STRAIGHT = (-2);
int N_RIGHT = (-3);

int flag = 0;

int maximum = 10;
int integral = 0;
int last_proportional = 0;
int proportional = 0;
int derivate = 0;

int binary_sensors[5];

pthread_t dynamic_state;

int state = 0;  
// 0 : moving
// 1: ㅓ
// 2: ㅏ
// 3: ㅜ
// 4: +
// 5: ㄱ
// 6: r
// 7: dead end
// 8: goal

Stack stack;
Stack result;
void turn_left(void);
void turn_right(void);
void calibrate_line(void);
void go_forward();
void delay_forward();
int move();
void dfs(int);

void turn_left() {
    printf("turn left \n");
	//forward();
    while(1) {
        setMotor(-15, 15);
        if (binary_sensors[2] == 0) break;
    }
	while(1) {
		setMotor(-15, 15);
        if (binary_sensors[2] == 1 && (binary_sensors[0] == 0 && binary_sensors[1] == 0 && binary_sensors[3] == 0 && binary_sensors[4] == 0)) break;
		// if (state == 0) break;
	}
	stop();
}

void turn_right() {
    printf("turn right \n");
	//forward();
    while(1) {
        setMotor(15, -15);
        if (binary_sensors[2] == 0) break;
    }
	while(1) {
		setMotor(15, -15);
        if (binary_sensors[2] == 1 && (binary_sensors[0] == 0 && binary_sensors[1] == 0 && binary_sensors[3] == 0 && binary_sensors[4] == 0)) break;
		// if (state == 0) break;
	}
	stop();
}

void go_forward() {
	while(1) {	
		if (state != 0) break;
		setMotor(-10, -10);
        move();
	}
}

void delay_forward(int value) {
    forward();
    setMotor(-10, -10);
    usleep(value);
    stop();
}



int move() {
	int position = last_value;

	// the p term should be 0 when we are on the line
	proportional = position - 1800;

	// compute the d (change) and i (sum) of the position
	derivate = proportional - last_proportional;
	integral += proportional;

	// remember the last position
	last_proportional = proportional;

	int power_diff = proportional/10 + derivate;//  integral/10000 + derivate;

	if(power_diff > maximum)
		power_diff = maximum;
	if(power_diff < -maximum)
		power_diff = -maximum;

	//	printf("(%d) >> P: %d, I: %d, D: %d >> vel: %d\n", position, proportional, derivate, integral, power_diff);

	if(power_diff < 0) {
		setPWMA(maximum + power_diff);
		setPWMB(maximum);
	}
	else {
		setPWMA(maximum);
		setPWMB(maximum - power_diff);
	}
    // printf("\\%d %d\\\n", PA, PB);
	return 0;
}

void print_node(int c) {
	printf("%d -- ", c);
}

void dfs(int dir) {
	int prev_state;
	
	print_stack(&stack, print_node); 
	if (dir == LEFT || dir == N_LEFT) {
		turn_left();
	} else if (dir == RIGHT || dir == N_RIGHT) {
		turn_right();  
	}

	go_forward();
    stop();
    delay_forward(20000);
    sleep(1);
    prev_state = state;
    delay_forward(650000);
	sleep(1);

	if (prev_state == 3) {
		printf("prev_state : 3 \n");
        printf("state : %d\n", state);
		// stop();
		// delay_forward();
        if(binary_sensors[0] == 1 && binary_sensors[1] == 1 && binary_sensors[2] == 1 && binary_sensors[3] == 1 && binary_sensors[4] == 1){
            prev_state = 8;
        }else{

        
            if (state == 0 || binary_sensors[1] == 1 || binary_sensors[3] == 1) {
                prev_state = 4;
            } else if (state == 7) {
                prev_state = 3;
            }
        }
	} else if (prev_state == 5) {
		printf("prev_state :  5 \n");
        
        printf("state : %d\n", state);
		// stop();
		// delay_forward();

		if (state == 0) {
			prev_state = 1;
            printf("%d %d\n", state, prev_state);
		}
	} else if (prev_state == 6) {
		printf("prev_state :  6 \n");
        
        printf("state : %d\n", state);
		// stop();
		// delay_forward();

		if (state == 0) {
			prev_state = 2;
		}
	} else if (prev_state == 0) {
		if (state == 7) {
			prev_state = 7;
		}
        // stop();
		// delay_forward();
	}

	if (prev_state == 1) { // 1: ㅓ
		printf("ㅓ \n");
		push(&stack, N_LEFT);
        stop();
		dfs(N_LEFT);
        stop();
		dfs(STRAIGHT);
	} else if (prev_state == 2) { // 2: ㅏ
		printf("ㅏ \n");
		push(&stack, N_RIGHT);
        stop();
		dfs(N_RIGHT);
        stop();
		dfs(STRAIGHT);
	} else if (prev_state == 3) { // 3: ㅜ
        printf("%d, %d\n", state, sensor_values[2]);
		printf("ㅜ \n");
		push(&stack, N_LEFT);
        stop();
		dfs(N_LEFT);
		push(&stack, N_RIGHT);
		stop();
        dfs(N_RIGHT);
	} else if (prev_state == 4) { // 4: +
		printf("+ \n");
		push(&stack, N_LEFT);
		stop();
        dfs(N_LEFT);
		push(&stack, N_RIGHT);
		stop();
        dfs(N_RIGHT);
		stop();
        dfs(STRAIGHT);
	} else if (prev_state == 5) { // 5: ㄱ
		printf("ㄱ \n");
		push(&stack, LEFT);
		stop();
        dfs(LEFT);
	} else if (prev_state == 6) { // 6: r
		printf("r \n");
		push(&stack, RIGHT);
		stop();
        dfs(RIGHT);
	} else if (prev_state == 7) { // 7: dead end
		printf("dead end \n");
		int cur_dir;

		turn_right();

		while(1) {
			go_forward();
            stop();

            delay_forward(20000);
            sleep(1);
            // prev_state = state;
            delay_forward(650000);
            sleep(1);

			if(stack.size == 0){
				printf("Empty Stack\n");
				return;
			}
            
			pop(&stack, &cur_dir);
            printf("====[POP]====\n");
            printf("Size : %d\n", stack.size);
            print_stack(&stack, print_node); 
			if (cur_dir < 0) {
				if (cur_dir == N_LEFT) {
                    printf("N_left\n");
                    ////////////////////////////////////////////////////////////////////////////////
					turn_left(); 
                    ////////////////////////////////////////////////////////////////////////////////
					return;
				} else if (cur_dir == N_RIGHT) {
                    printf("N_right\n");
                    ////////////////////////////////////////////////////////////////////////////////
					turn_right();
                    ////////////////////////////////////////////////////////////////////////////////
					return;
				}
                
			} else {
				if (cur_dir == LEFT) {
					turn_right();
				} else if (cur_dir == RIGHT) {
					turn_left();
				} 
			}
		}
	} else if (prev_state == 8) { // 8: goal
        printf("====================== \n");
        printf("====== THE END ======= \n");
        printf("====================== \n");
		return ;
	}

	return ;
}


void dream() {
	int tmp;
  int cur_dir;
	
	while(stack.size != 0) {
		pop(&stack, &tmp);
		push(&result, tmp);
	}

    while(1) {
        go_forward();
        stop();

        delay_forward(20000);
        sleep(1);
        delay_forward(650000);
        sleep(1);

        if(result.size == 0){
            printf("Empty Stack\n");
            return;
        }
        
        pop(&result, &cur_dir);

        printf("====[POP]====\n");
        printf("Size : %d\n", result.size);

        print_stack(&result, print_node); 

        if (cur_dir < 0) {
            if (cur_dir == N_LEFT) {
                printf("N_left\n");
                turn_left();
            } else if (cur_dir == N_RIGHT) {
                printf("N_right\n");
                turn_right();
            }
        } else {
            if (cur_dir == LEFT) {
                turn_left();
            } else if (cur_dir == RIGHT) {
                turn_right();
            } 
        }
    }
}


void convert_into_b_sensor () {
	for (int i = 0; i < 5; i++) {
		if (sensor_values[i] < 400) {
			binary_sensors[i] = 1;
		} else {
			binary_sensors[i] = 0;
		}
	}
}

void print_sensor() {
	for (int i = 0; i < 5; i++) {
		printf("%d ", sensor_values[i]);
	}
	printf("\n");
}

void print_b_sensor() {
	for (int i = 0; i < 5; i++) {
		printf("%d ", binary_sensors[i]);
	}
	printf("\n");
}

void *update_state(void* data) {
	pthread_detach(pthread_self());
	int left, right, straight;

	while(1) {
		readLine();
		convert_into_b_sensor();

		// printf("state: %d \n", state);

		// convert into state
		left = binary_sensors[0];
		right = binary_sensors[4];
		straight = binary_sensors[1] | binary_sensors[2] | binary_sensors[3];
		if (left == 1 && right == 0 && binary_sensors[2] == 1) {
			if(state == 3)
				continue;
			state = 5;
		} else if (left == 0 && right == 1 && binary_sensors[2] == 1) {
			if(state == 3)
				continue;
			state = 6;
		} else if (left == 0 && right == 0 && (binary_sensors[2] && !(binary_sensors[1] && binary_sensors[3]))) {
			state = 0;
		} //else if (left == 1 && right == 1 && straight == 1) {
        else if (((binary_sensors[0] | binary_sensors[1]) & (binary_sensors[3] | binary_sensors[4])) & binary_sensors[2]){
			state = 3;
		} else if (left == 0 && right == 0 & straight == 0) {
			state = 7;
		}

		usleep(50000);
	}
}

int main() {
	state = 0;
	init_IR();
	init_motor();

	pthread_create(&dynamic_state, NULL, update_state, NULL);

	init_stack(&stack);
	init_stack(&result);
	
	//dfs(STRAIGHT);
  printf("End of DFS\n");


	push(&result, RIGHT);
	push(&result, N_LEFT);
	push(&result, LEFT);
	push(&result, RIGHT);
	push(&result, N_RIGHT);
	push(&result, N_LEFT);
	push(&result, RIGHT);
	push(&result, N_LEFT);
	push(&result, N_RIGHT);
  push(&result, LEFT);

	
	dream();
	
	destroy_stack(&stack);
  destroy_stack(&result);


	return 0;
}
