# AI Camera to detect fire - Firevolt project

## What is this about?

This project made to learn how cameras works and how AI is made. to try and learn, I decided to try and code a camera that detects fires and send a signal to the user or to another robot.

If the other robot is configured to turn off the fire (Like a firefighter robot), then the camera send a signal to the robot to share the location of the fired. The other robot should have a integrated camera too.

## Preparation of the `boot.py` file

In this file, you can see there a line of code where you required to put your network connection. For that, we opted to use .env files to not share the information between git commits. (which I sadly did with the initialization of this repository)
