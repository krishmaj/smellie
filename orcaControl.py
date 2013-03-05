# User functions for checking and controlling the SMELLIE hardware via a TCP/IP connection (simulating ORCA)
# Written by Christopher Jones (17/01/2013)
# Additional changes by Krish Majumdar (05/03/2013)

import sys, time
from socket import *         # portable socket interface and constants

continue_flag = '5189'                          # this is the flag to continue to the next stage of a run
check_connection_flag = '10'                    # this checks if the connection is present
start_initialise_flag = '20'                    # this starts the initialisation stage of a SMELLIE run
sepia_box_no_connection_flag = '30'             # this flag is raised if Sepia is not powered or connected correctly
relay_switch_no_connection_flag  = '40'         # this flag is raised if the Laser Switch is not powered or connected to SNOdrop correctly

# SAFE-STATE ERROR CODES
sepia_wrong_set_intensity_flag = '50'           # this flag is raised if the wrong default intensity is set on Sepia
sepia_wrong_freq_flag = '55'                    # this flag is raised if the wrong default frequency is set on Sepia
sepia_wrong_pulse_mode_flag = '60'              # this flag is raised if the wrong default pulse mode is set on Sepia
relay_switch_wrong_default_flag = '65'          # this flag is raised if the wrong default channel on the Laser Switch is set
setup_run_flag = '70'                           # this flag is to setup the parameters for a SMELLIE run
self_test_fail = '77'                           # this flag indicates that the self-test has failed
relay_switch_set_wrong = '79'                   # this flag indicates that the Laser Switch is set incorrectly
fs_channel_broken = '84'                        # this flag indicates that the Fibre Switch channel is broken or incorrectly set
pulse_number_too_high = '87'                    # this flag indicates the number of pulses sent from the NI box is too high
run_failure_flag = '102'                        # this flag indicates that the run has failed
trigger_frequency_flag = '132'                  # this flag indicates that the trigger frequency for the NI box is incorrectly set
timeout_flag = '123456'                         # this is the timeout flag for all calls to the timeout function


# Initialise the TCP/IP socket with an IP address 
def initialise_socket(ip_address):	
	serverPort = 50007
	sockobj = socket(AF_INET, SOCK_STREAM)     # create a TCP/IP socket object
	sockobj.connect((ip_address, serverPort))  # bind the socket object to the specified server and port number 
 	sockobj.send("")			               # send a blank message to SMELLIE via the socket to check response
	return sockobj	 	


# this function closes the socket and the TCP/IP connection 
def close_socket(sockobj):
	sockobj.close()


#check that SMELLIE/SNOdrop is working and responding to the TCP/IP connection
def check_connection(sockobj):		  
	data = sockobj.recv(1024)
	
	if (data == check_connection_flag):
		print "ORCA Control (Check Connection) - Successful connection made to SMELLIE"
	else:
		print "ORCA Control (Check Connection) - Signal that was received:" + str(data)
		print "ORCA Control (Check Connection) - Expected Signal: " + check_connection_flag 
		sys.exit("ORCA Control (Check Connection) - No connection was made to SMELLIE")	 


# Send command to SMELLIE telling it to begin initialisation 
def initialise(sockobj):
	sockobj.send(start_initialise_flag) 
	print "ORCA Control (Initialise) - Initialisation Command has been sent ... "


# this function checks the status of the laserSwitch 
def check_laserSwitch(sockobj):
	data = sockobj.recv(1024)
	
	if (data == continue_flag):
		print "ORCA Control (Check laserSwitch) - The Laser Switch is working correctly"
	else:
		sys.exit("ORCA Control (Check laserSwitch) - The Laser Switch is not connected correctly to mains power and/or the SNOdrop PC ... re-run this program when the issue is resolved")


def set_ls_channel(ls_channel, sockobj):	
	sockobj.send(ls_channel)
	data = sockobj.recv(1024)

	if (data == continue_flag):
		print "ORCA Control (Set laserSwitch Channel) - Command to set Laser Switch Channel has been sent"
	elif(data == timeout_flag):
		sys.exit("ORCA Control (Set laserSwitch Channel) - SMELLIE has timed out)
	else:
		sys.exit("ORCA Control (Set laserSwitch Channel) - Please re-start SMELLIE and check all connections.  Re-run this program when the issue is resolved")
		
	# wait for confirmation that the Sepia has rebooted (needs to do this since the laserSwitch channel change will have turned Sepia off and on again)
	while 1:
		data = sockobj.recv(1024)
		if data : break

	if (data == continue_flag):
		print "ORCA Control (Set laserSwitch Channel) - Laser Switch channel has been set to: " + ls_channel
	elif (data == timeout_flag):
		sys.exit("ORCA Control (Set laserSwitch Channel) - SMELLIE has timed out")
	else:
		sys.exit("ORCA Control (Set laserSwitch Channel) - The Laser Switch channel has not been set correctly")	


# this function checks the connection status of Sepia
def check_sepia_connection(sockobj):
	data = sockobj.recv(1024)

	if (data == continue_flag):
	    print "ORCA Control (Check Sepia Connection) - Sepia is working correctly"
	else:
		sys.exit("ORCA Control (Check Sepia Connection) - The SEPIA Laser Driver is not connected correctly, or has no power ... re-run this program when the issue is resolved")


def set_laser_parameters(intensity, frequency_mode, sockobj):
	sockobj.send(intensity)
	data = sockobj.recv(1024)
	
	if (data == continue_flag):
		print "ORCA Control (Set Laser Parameters) - Laser Intensity set to: " + intensity + "%" 
		sockobj.send(frequency_mode)
	elif (data == timeout_flag):
		sys.exit("ORCA Control (Set Laser Parameters) - SMELLIE has timed out")
	else:
		sys.exit("ORCA Control (Set Laser Parameters) - The specified laser intensity value has not been seen by ORCA")		
	
	# DO NOT CHANGE THE ORDER OF THESE COMMANDS ... this sets and checks the frequency	
	data = sockobj.recv(1024)	
	if (data == continue_flag):
		print "ORCA Control (Set Laser Parameters) - Laser Frequency set to: External Rising-Edge (6)"		
		return 
	elif (data == timeout_flag):
		sys.exit("ORCA Control (Set Laser Parameters) - SMELLIE has timed out")	
	else:
		sys.exit("ORCA Control (Set Laser Parameters) - The specified laser frequency value has not been seen by ORCA")


def set_fs_channel(fs_channel, sockobj):
	sockobj.send(fs_channel)
	data = sockobj.recv(1024)
	
	if (data == continue_flag):
		print "ORCA Control (Set fibreSwitch Channel) - Fibre Switch channel set to: " + fs_channel
	elif (data == fs_channel_broken):
		sys.exit("ORCA Control (Set fibreSwitch Channel) - The Fibre Switch channel has not been set correctly")
	elif (data == timeout_flag):
		sys.exit("ORCA Control (Set fibreSwitch Channel) - SMELLIE has timed out")
	else:
		sys.exit("ORCA Control (Set fibreSwitch Channel) - Unknown error - please re-start SMELLIE and check all connections.  Re-run this program when the issue is resolved")


def set_ni_pulse_number(number_of_pulses, sockobj):
	sockobj.send(number_of_pulses)
	data = sockobj.recv(1024)
	
	if (data == continue_flag):
		print "ORCA Control (Set NI Pulse Number) - Number of Pulses to be sent to the NI box: " + number_of_pulses
	elif (data == pulse_number_too_high):
		sys.exit("ORCA Control (Set NI Pulse Number) - The number of pulses is greater than 100,000 - this is too high")
	elif (data == timeout_flag):
		sys.exit("ORCA Control (Set NI Pulse Number) - SMELLIE has timed out")
	else:
		sys.exit("ORCA Control (Set NI Pulse Number) - Unknown error - please re-start SMELLIE and check all connections.  Re-run this program when the issue is resolved")


def set_ni_trigger_frequency(trigger_frequency, sockobj):
	sockobj.send(trigger_frequency)
	data = sockobj.recv(1024)
	
	if (data == continue_flag):
		print "ORCA Control (Set NI Trigger Frequency) - Trigger Frequency of the NI box is set to:" + trigger_frequency + " Hz"
	elif (data == trigger_frequency_flag):
		print data 
		sys.exit("ORCA Control (Set NI Trigger Frequency) The NI box's trigger frequency is not correctly set")
	elif (data == timeout_flag):
		sys.exit("ORCA Control (Set NI Trigger Frequency) - SMELLIE has timed out")
	else:
		print data
		sys.exit("ORCA Control (Set NI Trigger Frequency) - Unknown error - please re-start SMELLIE and check all connections.  Re-run this program when the issue is resolved")


def check_safe_states(sockobj):
	data = sockobj.recv(1024)
	
	if (data == continue_flag):
		print "ORCA Control (Check Safe States) - All safe-states are correctly set"
		sockobj.send(setup_run_flag) 
	elif (data == sepia_wrong_set_intensity_flag):
		sys.exit("ORCA Control (Check Safe States) - The Laser Intensity is not set to its safe-state value ... re-run this program when the issue is resolved")
	elif (data == sepia_wrong_freq_flag):
		sys.exit("ORCA Control (Check Safe States) - The Laser Frequency is not set to its safe-state value ... re-run this program when the issue is resolved")
	elif (data == sepia_wrong_pulse_mode_flag):
		sys.exit("ORCA Control (Check Safe States) - The Laser Pulse Mode is not set to its safe-state value ... re-run this program when the issue is resolved")
	elif (data == relay_switch_wrong_default_flag):
		sys.exit("ORCA Control (Check Safe States) - The Laser Switch is not set to its safe-state ... re-run this program when the issue is resolved")
	else:
		sys.exit("ORCA Control (Check Safe States) - Unknown error - please re-start SMELLIE and check all connections.  Re-run this program when the issue is resolved")


# checks the complete self_test
def check_self_test(sockobj):
	data = sockobj.recv(1024)
	
	if (data == continue_flag):
		print "ORCA Control (Check Self Test) - Self-test has been passed"
	elif (data == self_test_fail):
		sys.exit("ORCA Control (Check Self Test) - Self-test has failed")
	elif (data == timeout_flag):
		sys.exit("ORCA Control (Check Self Test) - SMELLIE has timed out")
	else:
		sys.exit("ORCA Control (Check Self Test) - Unknown error - please re-start SMELLIE and check all connections.  Re-run this program when the issue is resolved")


def run_completion(sockobj):
	data = sockobj.recv(1024)
	
	if (data == continue_flag):
		print "ORCA Control (Run Completion) - Run is Complete!"
	elif (data == run_failure_flag):
		sys.exit("ORCA Control (Run Completion) - Run has failed")
	elif (data == timeout_flag):
		sys.exit("ORCA Control (Run Completion) - SMELLIE has timed out")
	else:
		sys.exit("ORCA Control (Run Completion) - Unknown error - please re-start SMELLIE and check all connections.  Re-run this program when the issue is resolved")


##### START OF THE MAIN PROGRAM ####################################################################################################

def main():		
	ip_address = "192.168.0.1" 
	
	sockobj = initialise_socket(ip_address)
	check_connection(sockobj)			
	initialise(sockobj)
	
	check_sepia_connection(sockobj)
	check_laserSwitch(sockobj)
	check_safe_states(sockobj)
	
	intensity = '100'
	frequency_mode = '6'
	ls_channel = '1'
	fs_channel = '1'
	number_of_pulses = '100000'
	trigger_frequency = '10000'
	
	set_ls_channel(ls_channel, sockobj)
	set_laser_parameters(intensity, frequency_mode, sockobj)
	check_self_test(sockobj)
	
	set_fs_channel(fs_channel, sockobj)
	set_ni_pulse_number(number_of_pulses, sockobj)
	set_ni_trigger_frequency(trigger_frequency, sockobj)
	
	run_completion(sockobj)

main()
