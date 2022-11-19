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
    while not('>' in prompt or '#' in prompt):
        prompt = read_serial(console)
def wait():
    m.getch()

def getNameOfFiles(mypath):
  onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
  return onlyfiles

def read_serial(console, untilCR = True):
    if untilCR:
        output = str(console.read_until(), 'utf-8')
    else:
        output = str(console.read(999), 'utf-8')
    return output
  


def check_logged_in(console):
    console.write(bytes("\r\n", 'utf-8'))
    prompt = read_serial(console)
    if '>' in prompt or '#' in prompt:
        return True
    else:
        return False

def logout(console):
    print("Saliendo")
    while check_logged_in(console):
        console.write(bytes("exit\r\n",'utf-8'))

    print("Ha salido")

def send_command(console, cmd='', readUntilCR = True):
    #cmd = cmd.replace('\n', "")
    cmd2 = cmd.replace('\n', "")
    cmd2 = cmd2.replace('\r', "")

    console.write(bytes(cmd2 + '\r\n', 'utf-8'))
    return read_serial(console, untilCR=readUntilCR)

def sendCommands(console, commands, name):
    f = open(LOG_PAD + "/" + name + ".log", 'w')
    for command in commands:
        if command[0] == '!':
            output = " omitido ------> " + command
        elif command == "\n":
            pass
        else:
            output = send_command(console, cmd=command)
            print(output)
            #isReady(console)
        print(output)
        f.write(output)
    f.close()
            
    logout(console)

def check_initial_dialog(console):
    time.sleep(1)
    prompt = send_command(console, "", False)
    print(prompt)
    if 'yes' in prompt or 'no' in prompt:
        send_command(console, 'no', False)

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
                    time.sleep(0.2)
                    pass
                sendCommands(console, commands, c.split(".")[0])
                console.close()
            except Exception as e:
                print(e)
                try:
                    console.close()
                except:
                    pass
                print("Error en " + com + " desea reintentar (y/n) ", end="")
                if input() != 'y':
                    retry = False
                    f = open(LOG_PAD + "/" + c.split(".")[0] + ".log", 'w')
                    f.write("error")
                    f.close()
                else:
                    retry = True


if __name__ == "__main__":
    if sys.argv[1]:
        com = sys.argv[1]
    main(com)