# Copyright Jan Newmarch
# Berkeley license
import struct
import json
import socket
import re

MCAST_GRP = '239.255.255.250'
MCAST_PORT = 1982
SRC_PORT = 8080  # my random port

CR_LF = "\r\n"

def get_ip_port():
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
  sock.bind(('', SRC_PORT))
  sock.sendto(("M-SEARCH * HTTP/1.1\r\n\
  HOST: 239.255.255.250:1982\r\n\
  MAN: \"ssdp:discover\"\r\n\
  ST: wifi_bulb\r\n").encode(), (MCAST_GRP, MCAST_PORT))
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

def sendto(ip, port, command):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
  sock.connect((ip, port))
  sock.send((command + CR_LF).encode())
  response = sock.recv(10240)
  #print(response)

  # the response is a JSON string, parse it and return
  # the "result" field
  dict = json.loads(response)
  sock.close()
  # print("Response was ", response)
  return(dict["result"])

def get_prop(prop, ip, port):
  # hard code the JSON string
  command = '{"id":1,"method":"get_prop","params":["' + prop + '"]}'
  response = sendto(ip, port, command)
  return response

def set_prop(prop, params, ip, port):
  # hard code the JSON string
  command = '{"id":1,"method":"set_' + prop +\
            '", "params":' + params +\
            '}'
  # print(command)
  response = sendto(ip, port, command)
  return response

def set_power(state, ip, port):
  params = '["' + state + '", "smooth", 500]'
  response = set_prop('power', params, ip, port)
  return response

def set_rgb(state, ip, port):
    params = '[' + str(state) + ', "smooth", 500]'
    response = set_prop('rgb', params, ip, port)
    return response

def set_bright(state, ip, port):
  params = '[' + str(state) + ', "smooth", 500]'
  response = set_prop('bright', params, ip, port)
  return response

def set_hsv(hue, sat, ip, port):
  params = '[' + str(hue) + ', ' + str(sat) + ', "smooth", 500]'
  response = set_prop('hsv', params, ip, port)
  return response


if __name__ == "__main__":

    Colors = {
        'red': 16711680,
        'blue': 255,
        'white': 16777215
    }

    print('Starting')
    (ip, port) = get_ip_port()
    if (ip, port) == (None, None):
        print('Can\'t get address of light')
        exit(1)
    print('IP is ', ip, ' port is ', port)

    # sample set commands:
    # success = set_power("off", ip, port)
    # print('Power set is', success[0])

    # success = set_bright(90, ip, port)
    # print('Brightness set is', success[0])

    # name = set_name('Bedroom', ip, port)
    # print('Name is ', name[0])

    # sample get commands:
    # power = get_prop("power", ip, port)
    # print('Power is', power[0])

    setHsv = set_hsv(0, 0, ip, port)
    print("HSV IS: ", setHsv[0])

    prop = input("Enter prop:")
    while prop != '-1':
        if prop == "on" or prop == "off":
            success = set_power(prop, ip, port)
            print("Power is set to ", success[0])
        elif "set color" in prop:
            m = prop.split('set color ')
            success = set_rgb(Colors.get(m[1]), ip, port)
            print("Success", success[0])
        elif "set bright" in prop:
            m = prop.split('set bright ')
            success = set_bright(m[1], ip, port)
            print("Success", success[0])
        success = get_prop(prop, ip, port)
        print("Prop is ", success[0])
        prop = input("Enter prop: ")

    # getting multiple properties at once.
    # Be careful with the quotes, words need to be separated by "," !
    # prop_list = get_prop('power", "bright', ip, port)
    # print("Property list is", prop_list)