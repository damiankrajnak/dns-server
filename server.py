import socket
import re
import sys

if (len(sys.argv) != 2):
    sys.exit('INVALID NUMBER OF ARGUMENTS')

HOST = '127.0.0.1'                # Standard loopback interface address (localhost)
try:
    PORT = int(sys.argv[1])           # Port to listen on (non-privileged ports are > 1023)
except:
    sys.exit('SOMETHING WENT WRONG')
if ((PORT < 0) or (PORT > 65535)):
    sys.exit('PORT OUT OF RANGE')

http = 'HTTP/1.1'

############        ERRORS       ############

ret200 = '200 OK'
err400 = '400 Bad Request'
err404 = '404 Not Found'
err405 = '405 Method Not Allowed'
err500 = '500 Internal Server Error'

############        REGEXes       ############

get_regex_1st = 'GET \/resolve\?name=.+?&type=(A|PTR) HTTP\/1.1'
get_regex_2nd = 'GET \/resolve\?type=(A|PTR)&name=.+? HTTP\/1.1'
name_regex = 'name=.+?(&| )'
ip_regex = 'name=[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}(&| )'
domain_regex = '.+\.[a-z]+\s*:\s*(A|PTR)\s*'
addr_regex = '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\s*:\s*(A|PTR)\s*'
type_regex = 'type=(A|PTR)(&| )'


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    s.bind((HOST, PORT))
    while True:
        s.listen()
        conn, addr = s.accept()
        with conn:
            data = conn.recv(1024)
            if not data:
                break
            newdata = data.decode('utf-8')
            splitdata = newdata.split('\r\n')
            splitdata = splitdata[0]
            
            if ((splitdata.split(' ', 1)[0]) == 'GET'):
            
                if (re.fullmatch('GET \/resolve\?name=.+?&type=(A|PTR) HTTP\/1\.1', splitdata)) or (re.fullmatch('GET \/resolve\?type=(A|PTR)&name=.+? HTTP\/1\.1', splitdata)):
                    
                    type = re.search(type_regex, newdata)
                    type = type[0]
                    type = type[:-1]
                    type = type[5:]
                    if(type != 'A') and (type != 'PTR'):
                        response = http + ' ' + err400 + '\r\n\r\n'
                        response = response.encode('utf-8')
                        conn.sendall(response)
                        conn.close()
                        continue
                    
                    ###   name is IP an adress   ###
                    
                    if(re.search(ip_regex, newdata)):
                        if(type == 'A'):
                            response = http + ' ' + err400 + '\r\n\r\n'
                            response = response.encode('utf-8')
                            conn.sendall(response)
                            conn.close()
                            continue
                        name = re.search(ip_regex, newdata)
                        name = name[0]
                        name = name[:-1]
                        name = name[5:]
                        try:
                            socket.inet_aton(name)
                        except socket.error:
                            response = http + ' ' + err400 + '\r\n\r\n'
                            response = response.encode('utf-8')
                            conn.sendall(response)
                            conn.close()
                            continue
                        try:
                            name2 = socket.gethostbyaddr(name)
                            name2 = name2[0]
                        except:
                            response = http + ' ' + err404 + '\r\n\r\n'
                            response = response.encode('utf-8')
                            conn.sendall(response)
                            conn.close()
                            continue
                            
                    ###   name is not an IP adress   ###
                    
                    elif(re.search(name_regex, newdata)):
                        if(type == 'PTR'):
                            response = http + ' ' + err400 + '\r\n\r\n'
                            response = response.encode('utf-8')
                            conn.sendall(response)
                            conn.close()
                            continue
                        name = re.search(name_regex, newdata)
                        name = name[0]
                        name = name[:-1]
                        name = name[5:]
                        try:
                            name2 = socket.gethostbyname(name)
                        except:
                            response = http + ' ' + err404 + '\r\n\r\n'
                            response = response.encode('utf-8')
                            conn.sendall(response)
                            conn.close()
                            continue
                    
                    else:
                        response = http + ' ' + err400 + '\r\n\r\n'
                        response = response.encode('utf-8')
                        conn.sendall(response)
                        conn.close()
                        continue
                        
                    
                    response = http + ' ' + ret200 + '\r\n\r\n' + name + ':' + type + '=' + name2 + '\r\n'
                    response = response.encode('utf-8')
                    conn.sendall(response)
                    conn.close()
                    continue
                else:
                    response = http + ' ' + err400 + '\r\n\r\n'
                    response = response.encode('utf-8')
                    conn.sendall(response)
                    conn.close()
                    continue
            elif ((splitdata.split(' ', 1)[0]) == 'POST'):
                if(re.fullmatch('POST \/dns-query HTTP\/1\.1', splitdata)):
                    splitdata = newdata.split('\r\n\r\n')
                    splitdata = splitdata[1]
                    splitdata = splitdata.split('\n')
                    rows = ''
                    end = False
                    output = False
                    for i in splitdata:
                        if(re.fullmatch(addr_regex, i)):
                            name = i.split(':', 1)[0]
                            name = name.strip()
                            type = i.split(':', 1)[1]
                            type = type.strip()
                            if (type == 'A'):
                                continue
                            else:
                                try:
                                    socket.inet_aton(name)
                                except socket.error:
                                    continue
                                try:
                                    name2 = socket.gethostbyaddr(name)
                                    name2 = name2[0]
                                except:
                                    continue
                                rows += name + ':' + type + '=' + name2 + '\r\n'
                                output = True
                        elif(re.fullmatch(domain_regex, i)):
                            name = i.split(':', 1)[0]
                            name = name.strip()
                            type = i.split(':', 1)[1]
                            type = type.strip()
                            if (type == 'PTR'):
                                continue
                            else:
                                try:
                                    name2 = socket.gethostbyname(name)
                                except:
                                    continue
                                rows += name + ':' + type + '=' + name2 + '\r\n'
                                output = True
                        else:
                            continue
                    if(end == True):
                        continue
                    if(output == True):
                        response = http + ' ' + ret200 + '\r\n\r\n' + rows
                        response = response.encode('utf-8')
                        conn.sendall(response)
                        conn.close()
                        continue
                    else:
                        response = http + ' ' + err400 + '\r\n\r\n'
                        response = response.encode('utf-8')
                        conn.sendall(response)
                        conn.close()
                        continue
                else:
                    response = http + ' ' + err400 + '\r\n\r\n'
                    response = response.encode('utf-8')
                    conn.sendall(response)
                    conn.close()
                    continue
            else:
                response = http + ' ' + err405 + '\r\n\r\n'
                response = response.encode('utf-8')
                conn.sendall(response)
                conn.close()
                continue


##############      TO DO      #############
# 1. PORT
# 2. makefile
# 3. prázdne riadky v queries.txt
