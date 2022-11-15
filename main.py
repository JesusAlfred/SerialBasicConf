import serial
from os import listdir
from os.path import isfile, join
import sys
import time
import msvcrt as m
import os

CONF_DIR = "./conf/"
LOG_PAD = './log'
READ_TIMEOUT = 8


def isReady(console):
    console.write(bytes("\r\n", 'utf-8'))
    prompt = read_serial(console)
    while not(prompt[-1] == '>' or prompt[-1] == '#'):
        prompt = read_serial(console)
def wait():
    m.getch()

def getNameOfFiles(mypath):
  onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
  return onlyfiles

def read_serial(console):
    data_bytes = console.inWaiting()
    if data_bytes:
        return str(console.read(data_bytes), 'utf-8')
    else:
        return ""

def check_logged_in(console):
    console.write(bytes("\r\n\r\n", 'utf-8'))
    time.sleep(1)
    prompt = read_serial(console)
    if '>' in prompt or '#' in prompt:
        return True
    else:
        return False

def logout(console):
    print("Saliendo")
    while check_logged_in(console):
        console.write(bytes("exit\r\n",'utf-8'))
        time.sleep(.5)

    print("Ha salido")

def send_command(console, cmd='', mode='none'):
    if mode != 'none':
        console.write(bytes("end\r\n"), 'utf-8')
        read_serial(console)
        console.write(bytes('enable\r\n', 'utf-8'))
        read_serial(console)
        if mode == 'conf':
            console.write(bytes('configure terminal\r\n','utf-8'))
            read_serial(console)

    console.write(bytes(cmd + '\r\n', 'utf-8'))
    return read_serial(console)

def sendCommands(console, commands, name):
    f = open(LOG_PAD + "/" + name + ".log")
    for command in commands:
        if command[0] == '!':
            output = " omitido ------> " + command
        elif command == "":
            pass
        else:
            isReady(console)
            output = send_command(console, cmd=command)
        f.write(output)
    f.close()
            
    logout(console)

def check_initial_dialog(console):
    print(console)
    console.write(bytes("\r\n\r\n", 'utf-8'))
    time.sleep(1)
    prompt = read_serial(console)
    if 'yes' in prompt or 'no' in prompt:
        send_command(console, 'no\n')

def main(com):
    conf = getNameOfFiles(CONF_DIR)
    if not os.path.exists(LOG_PAD):
        os.makedirs(LOG_PAD)
    for c in conf:
        print("Conectese a " + c.split(".")[0] + " y presione cualquier tecla para continuar ...")
        wait() 

        file = open(CONF_DIR + c, encoding='UTF-8')
        commands = []
        for line in file:
            commands.append(line)
        file.close()
        retry = True
        while retry:
            retry = False
            try:
                print("Conectando a " + c.split(".")[0] + " por " + com)
                console = serial.Serial(
                    port=com,
                    baudrate=9600,
                    parity="N",
                    stopbits=1,
                    bytesize=8,
                    timeout=READ_TIMEOUT
                )
                check_initial_dialog(console)

                while not check_logged_in(console):
                    pass
                sendCommands(console, commands, c.split(".")[0])
                console.close()
            except Exception as e:
                print(e)
                console.close()
                print("Error en " + com + " desea reintentar (y/n) ", end="")
                if input() != 'y':
                    retry = False
                    f = open(LOG_PAD + "/" + c.split(".")[0] + ".log")
                    f.write("error")
                    f.close()
                else:
                    retry = True


if __name__ == "__main__":
    if sys.argv[1]:
        com = sys.argv[1]
    main(com)