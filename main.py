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
    time.sleep(1)
    return read_serial(console)

def sendCommands(console, commands):
    check_logged_in(console)
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
                console.close()
            except Exception as e:
                print(e)
                print("Error en " + com + " desea reintentar (y/n) ", end="")
                if input() != 'y':
                    retry = False
                else:
                    retry = True


if __name__ == "__main__":
    if sys.argv[1]:
        com = sys.argv[1]
    main(com)