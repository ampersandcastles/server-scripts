import subprocess
import re
import argparse

IPMIHOST = "192.168.1.223"
IPMIUSER = "root"
IPMIPASS = "<password>"

def execute_ipmi_command(command):
    full_command = f"ipmitool -I lanplus -H {IPMIHOST} -U {IPMIUSER} -P \"{IPMIPASS}\" {command}"
    result = subprocess.run(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(result.stdout.decode().strip())
    if result.stderr:
        print(result.stderr.decode().strip())

def power_on():
    print("Powering on the server...")
    execute_ipmi_command("chassis power on")

def power_off():
    print("Powering off the server...")
    execute_ipmi_command("chassis power off")
    print("Enabling dynamic fan control...")
    execute_ipmi_command("raw 0x30 0x30 0x01 0x01")

def set_fan_speed(speed):
    print(f"Setting fan speed to {speed}%...")
    execute_ipmi_command(f"raw 0x30 0x30 0x02 0xff {hex(speed)}")

def enable_dynamic_fan_control():
    print("Enabling dynamic fan control...")
    execute_ipmi_command("raw 0x30 0x30 0x01 0x01")

def disable_dynamic_fan_control():
    print("Disabling dynamic fan control...")
    execute_ipmi_command("raw 0x30 0x30 0x01 0x00")


def get_server_temperature():
    print("Getting server temperature...")
    command = f"ipmitool -I lanplus -H {IPMIHOST} -U {IPMIUSER} -P \"{IPMIPASS}\" sdr type temperature"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    temperature_readings = result.stdout
    temperatures = re.findall(r'\| (\d+) degrees C', temperature_readings)
    temperatures = [int(temp) for temp in temperatures]
    average_temp = sum(temperatures) / len(temperatures) if temperatures else 0
    return average_temp

def adjust_fan_speed_based_on_temp():
    temp = get_server_temperature()
    print(f"Current temperature: {temp} degrees C")
    warning_threshold = 75
    critical_threshold = 90

    # Set fan speed based on temperature ranges
    if temp >= critical_threshold:
        print("Temperature is critical, setting fan speed to 100%.")
        set_fan_speed(100)
    elif temp >= warning_threshold:
        print("Temperature is high, setting fan speed to 80%.")
        set_fan_speed(80)
    elif temp >= 40:
        print("Temperature is moderate, setting fan speed to 60%.")
        set_fan_speed(60)
    elif temp >= 30:
        print("Temperature is low, setting fan speed to 50%.")
        set_fan_speed(50)
    else:
        print("Temperature is very low, setting fan speed to 40%.")
        set_fan_speed(40)

# Argument Parsing
parser = argparse.ArgumentParser(description='Server Management Script')
parser.add_argument('-p', '--power', choices=['on', 'off'], help='Power on or off the server')
parser.add_argument('-f', '--fan', type=int, choices=range(0, 101), metavar="[0-100]", help='Set fan speed percentage')
parser.add_argument('-t', '--temp', action='store_true', help='Adjust fan speed based on temperature')
parser.add_argument('-d', '--dynamic', choices=['on', 'off'], help='Toggle dynamic fan control')

args = parser.parse_args()

# Check for no action
if not any([args.power, args.fan, args.dynamic, args.temp]):
    parser.print_help()
    exit()

# Execute based on arguments
if args.power == 'on':
    power_on()
elif args.power == 'off':
    power_off()
     

if args.fan is not None:
    set_fan_speed(args.fan)

if args.temp:
    adjust_fan_speed_based_on_temp()

if args.dynamic == 'on':
    enable_dynamic_fan_control()
elif args.dynamic == 'off':
    disable_dynamic_fan_control()