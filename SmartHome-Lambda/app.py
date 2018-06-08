####################################### 
#This function sends SMS notification # 
#to set phone number every night      #
#######################################

import sys
import logging
import pymysql
import datetime
import boto3
from datetime import timedelta
from decimal import *

############################### 
#Establish Database Connection#
###############################

rds_host = "iotawsdb.ckh9zoyhbozr.us-east-1.rds.amazonaws.com"
name = "awsuser"
password = "awspassword"
db_name = "iotawsdb"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#Exception Handling
try:
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
except:
    logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
    sys.exit()

logger.info("SUCCESS: Connection to RDS mysql instance succeeded")


#############################################
#Following function fetches sensor readings #
#from database & calculate power consumption#
# & cost per LED                            #
#############################################

def handler(event, context):
    
    with conn.cursor() as cur:
       
        select_readings = "select LEDStatus_Red,LEDStatus_Blue,LEDStatus_Green,currentTime from SensorReadings where DAY(currentTime) = DAY(CURRENT_DATE - INTERVAL 1 DAY) order by currentTime"
        cur.execute(select_readings)
        total_count = cur.rowcount
        count = total_count
        #count = cur.rowcount
        #print(count)
        result_set = cur.fetchall()

        LED_On_Room1 = 0
        LED_On_Room2 = 0
        LED_On_Room3 = 0
        total_duration_Room1 = 0
        total_duration_Room2 = 0
        total_duration_Room3 = 0
        units_watt = 100 #Can be varied
        for row in result_set: 
          #for room 1
          count = count-1
          if ((row[0] == 1) and (LED_On_Room1 == 0)):
            start_duration_Room1 = row[3]
            LED_On_Room1 = 1
          elif (((row[0] == 0) and (LED_On_Room1 == 1)) or ((count == 0) and (LED_On_Room1 == 1))):
            end_duration_Room1 = row[3]
            duration_diff_Room1 = end_duration_Room1 - start_duration_Room1
            total_duration_Room1 += (duration_diff_Room1 .seconds)
            LED_On_Room1 = 0
          else:
            pass

        count = total_count
        for row in result_set: 
           #for room 2
          count = count-1 
          if ((row[1] == 1) and (LED_On_Room2 == 0)):
            start_duration_Room2 = row[3]
            LED_On_Room2 = 1
          elif (((row[1] == 0) and (LED_On_Room2 == 1))  or ((count == 0) and (LED_On_Room2 == 1))) :
            end_duration_Room2 = row[3]
            duration_diff_Room2 = end_duration_Room2 - start_duration_Room2
            total_duration_Room2 += (duration_diff_Room2.seconds)
            LED_On_Room2 = 0
          else:
            pass
          
        count = total_count
        for row in result_set: 
          count = count-1
	        #for room 3
          if ((row[2] == 1) and (LED_On_Room3 == 0)):
            start_duration_Room3 = row[3]
            LED_On_Room3 = 1
          elif (((row[2] == 0) and (LED_On_Room3 == 1)) or ((count == 0) and (LED_On_Room3 == 1))) :
            end_duration_Room3 = row[3]
            duration_diff_Room3 = end_duration_Room3 - start_duration_Room3
            total_duration_Room3 += (duration_diff_Room3.seconds)
            LED_On_Room3 = 0
          else:
            pass

        # Room1 Power consumption & cost calculations
        total_duration_Room1_inseconds = total_duration_Room1 
        total_duration_Room1 = total_duration_Room1 / 3600
        watt_hours_per_day_Room1 = total_duration_Room1 * units_watt
        kilo_watt_hours_per_day_Room1 = watt_hours_per_day_Room1 / 1000
        cost_per_day_Room1 = kilo_watt_hours_per_day_Room1 * 0.25
       # print((str(cost_per_day_Room1))[0:4])
        
        # Room2 Power consumption & cost calculations
        total_duration_Room2_inseconds = total_duration_Room2
        total_duration_Room2 = total_duration_Room2 / 3600
        watt_hours_per_day_Room2 = total_duration_Room2 * units_watt
        kilo_watt_hours_per_day_Room2 = watt_hours_per_day_Room2 / 1000
        cost_per_day_Room2 = kilo_watt_hours_per_day_Room2 * 0.25
       # print((str(cost_per_day_Room2))[0:4])
        
        # Room3 Power consumption & cost calculations
        total_duration_Room3_inseconds = total_duration_Room3
        total_duration_Room3 = total_duration_Room3 / 3600
        watt_hours_per_day_Room3 = total_duration_Room3 * units_watt
        kilo_watt_hours_per_day_Room3 = watt_hours_per_day_Room3 / 1000
        cost_per_day_Room3 = kilo_watt_hours_per_day_Room3 * 0.25
        
        savings = cost_per_day_Room2 - cost_per_day_Room1
        if(savings < 0):
          savings = 0
          
        cur.execute('insert into PowerConsumption values(%s,%s,%s,%s,%s,%s,%s)',(total_duration_Room1_inseconds,cost_per_day_Room1,total_duration_Room2_inseconds,cost_per_day_Room2,total_duration_Room3_inseconds,cost_per_day_Room3,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
    
    # Sens SMS using SNS service  
    sns = boto3.client('sns')
    number = '+12015656802'
    message1 = "Cost of LED-1 $" + (str(cost_per_day_Room1))[0:4] +"\n\n" + "Cost of LED-2 $" + (str(cost_per_day_Room2))[0:4] + "\n\n" + "Cost Savings for the day $" +  (str(savings))[0:4]
    sns.publish(PhoneNumber = number, Message = message1)
    