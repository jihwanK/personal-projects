#!/bin/bash

echo `lsof -ti:7314`
echo "kill 7314 process"
lsof -ti:7314 | xargs kill -9

ssh -L 7314:gold51:7314 -fN jhk1c21@iridis5_a.soton.ac.uk
