#! /bin/bash

gcc DFS_v3.c stack.c IR.c motor_control.c -lpthread -lwiringPi -g

./a.out
