import serial
from os import listdir
from os.path import isfile, join
import sys
import time
import msvcrt as m

CONF_DIR = "./conf/"
READ_TIMEOUT = 8

def wait():
    m.getch()

def getNameOfFiles(mypath):
  onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
  return onlyfiles

def read_serial(console):
    data_bytes = console.inWaiting()
    if data_bytes:
        return console.read(data_bytes)
    else:
        return ""

def check_logged_in(console):
    console.write("\r\n\r\n")
    time.sleep(1)
    prompt = read_serial(console)
    if '>' in prompt or '#' in prompt:
        return True
    else:
        return False

def logout(console):
    print("Saliendo")
    while check_logged_in(console):
        console.write("exit\r\n")
        time.sleep(.5)

    print("Ha salido")

def send_command(console, cmd='', mode='none'):
    if mode != 'none':
        console.write("end\r\n")
        read_serial(console)
        console.write('enable\r\n')
        read_serial(console)
        if mode == 'conf':
            console.write('configure terminal\r\n')
            read_serial(console)

    console.write(cmd + '\r\n')
    time.sleep(1)
    return read_serial(console)

def sendCommands(console, commands):
    for command in commands:
        print(send_command(console, cmd=command))
    logout(console)

def main(com):
    conf = getNameOfFiles(CONF_DIR)
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
                sendCommands(console, commands)
            except:
                print("Error en " + com + " desea reintentar (y/n) ", end="")
                if input() != 'y':
                    retry = False
                else:
                    retry = True


if __name__ == "__main__":
    if sys.argv[1]:
        com = sys.argv[1]
    main(com)