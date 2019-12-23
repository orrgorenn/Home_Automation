# Copyright Orr Goren
import struct
import json
import socket
import re

BULB_IP = '239.255.255.250'
BULB_PORT = 1982
SRC_PORT = 80
CR_LF = "\r\n"

Colors = {
    'red': 16711680,
    'blue': 255,
    'white': 16777215
}

def createSocket():
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
  sock.bind(('', SRC_PORT))
  sock.sendto(("M-SEARCH * HTTP/1.1" + CR_LF +
  "HOST: 239.255.255.250:1982" + CR_LF +
  "MAN: \"ssdp:discover\"" + CR_LF +
  "ST: wifi_bulb" + CR_LF).encode(), (BULB_IP, BULB_PORT))
  sock.close()

  sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  # ensure this socket is listening on the same
  # port as the multicast went on
  sock_recv.bind(('', SRC_PORT))
  response = sock_recv.recv(10240)
  sock_recv.close()

  # match on a line like "Location: yeelight://192.168.1.25:55443"
  # to pull ip out of group(1), port out of group(2)
  prog = re.compile("Location: yeelight://(\d*\.\d*\.\d*\.\d*):(\d*).*")
  for line in response.splitlines():
    result = prog.match(line.decode())
    if result != None:
      ip = result.group(1)
      port = result.group(2)
      return (ip, int(port))
  return (None, None)

def sendSocket(ip, port, command):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
  sock.connect((ip, port))
  sock.send((command + CR_LF).encode())
  response = sock.recv(10240)
  dict = json.loads(response)
  sock.close()
  return(dict["result"])

# def getProperty(prop, ip, port):
#   command = '{"id":1, "method":"get_prop", "params":["' + prop + '"]}'
#   response = sendTo(ip, port, command)
#   return response

def set_cmd(prop, state, ip, port):
  params = '["' + state + '", "smooth", 500]'
  command = '{"id": 1, "method": "set_' + prop + '", "params": "' + params + '"}'
  response = sendSocket(ip, port, command)
  return response

if __name__ == "__main__":

    print('Starting App...')
    (ip, port) = createSocket()
    if (ip, port) == (None, None):
        print('Can\'t find Yeelight bulb.')
        exit(1)
    print('Found Yeelight - IP:', ip, ' | Port: ', port)

    prop = input("Enter command: (to terminate send -1)")
    while prop != "-1":
        if "set power" in prop:
            m = prop.split('set power ')
            success = set_cmd('power', m[1], ip, port)
            print("Power is set to ", success[0])
        elif "set color" in prop:
            m = prop.split('set color ')
            # verify color exists, if not make white
            if m[1] not in Colors:
                m[1] = "white"
            success = set_cmd('rgb', Colors.get(m[1]), ip, port)
            print("Successfully change color to " + m[1], success[0])
        elif "set bright" in prop:
            m = prop.split('set bright ')
            # varify correct brightness value
            if m[1] < 0 or m[1] > 100:
                m[1] = 0
            success = set_cmd('bright', m[1], ip, port)
            print("Successfully changed brightness to " + m[1] + "%", success[0])
        elif "set hue" in prop:
            m = prop.split('set hue ')
            # varify correct hue value
            if m[1] < 0 or m[1] > 359:
                m[1] = 0
            success = set_cmd('hue', m[1], ip, port)
            print("Successfully changed HUE value to " + m[1], success[0])
        elif "set sat" in prop:
            m = prop.split('set sat ')
            # varify correct saturation value
            if m[1] < 0 or m[1] > 100:
                m[1] = 0
            success = set_cmd('sat', m[1], ip, port)
            print("Successfully changed SATURATION value to " + m[1], success[0])
        prop = input("Enter command: (to terminate send -1)")
    exit(1)