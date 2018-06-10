# Energy-saving Smart Home System
An IoT based lighting system using PIR motion sensors to conserve energy and save money to homeowners.

The project focuses on controlling LEDs by using PIR motion based sensors which saves electricity in contrast with the traditional methods of switch or a button. The project works by capturing the real-time data from the raspberry pi which is attached to the sensors - PIR LED RED, PIR LED Blue, PIR Motion sensor and PIR Button or a switch control.
Python script which runs on raspberry pi collects the real time data from the sensors. The collected data is stored in RDS Web Service provided by Amazon AWS. AWS Lambda function is triggered to pull the data from RDS and process the data to calculate the power consumption and cost incurred by the LEDs in the lighting system for the previous day. A notification is sent to the homeowners about the cost incurred by the LEDs for the duration they are ON using Amazon Simple Notification Service (SNS).

Python script - smarthome.py
----------------------------------------------------------------
Python Version - 3
The script contains code to control the lighting system of the home using motion sensor to control LED - 1 and switch to control LED-2
Topics are published to reflect the real time status of the sensors on IBM watson IoT platform
      
Amazon SNS
---------------------------------------------------------------------
Create a free tier user account in AWS console using https://aws.amazon.com/console/
Navigate to Services -> Lambda -> Create Function
Follow the steps from the below link to create a lambda function
https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-create-function.html
      4) Once the function is created upload a zip file sendSMS.zip which has the necessary python files and library packages through Code entry type -> Upload a .zip file.
      5) Choose Runtime - Python 3.6.   	
      5) Save and run the file.
      6) This function could be set to trigger every night at customisable time to send SMS notifications to owners of total cost and savings by each LED for the previous day.      

Amazon RDS
----------------------------------------------------------------
Login into AWS account
Create an RDS instance in Amazon RDS as shown in https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Tutorials.WebServerDB.CreateDBInstance.html.
Created a database named “iotawsdb”.
Created a table named “PowerConsumption” with the columns Room1duration,Room2duration,Room3duration,Room1cost,Room2cost,Room3cost,date (durations as int, cost as flot and date as datetime).
Created another table - “SensorReadings” with the columns LEDStatus_Red, LEDStatus_Green, LEDStatus_Blue, currentTime (Status as int, currentTime as datetime).
