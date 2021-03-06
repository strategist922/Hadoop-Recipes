
import sys
import os
import MySQLdb
import datetime
import paramiko
import pexpect
import commands
import time

"""
Custom monitoring script

"""
__author__="nitin p kumar"

class et:

    #case 1 for all and direct central server connectivity
    use_case={}

    server_ip={}

    user_ip={}

    pass_ip={}

    source_path={}

    dest_path={}

    #case 3 for two server gateways.
    sg_ip_one={}

    sg_ip_two={}

    sg_un_one={}

    sg_un_two={}

    sg_pass_one={}

    sg_pass_two={}

    port_one={}

    port_two={}



############ display details #################
def display_details(myet,operator):
    print("Operator : %s" %operator)
    print("Server IP : %s" %myet.server_ip[operator])
    print("Username : %s" %myet.user_ip[operator])
    print("Password : %s" %myet.pass_ip[operator])
    print("Source path : %s" %myet.source_path[operator])
    print("Destionation path : %s" %myet.dest_path[operator])


########### connect to mysql ######################
def mysql_connect(mysql_host='localhost',mysql_port=3306,mysql_un='root',mysql_pw='',mysql_sock='/var/lib/mysql/mysql.sock'):
    try:
        db=MySQLdb.connect(host=mysql_host,port=mysql_port,user=mysql_un,passwd=mysql_pw,unix_socket=mysql_sock)
        return db
    except Exception ,e:
        raise

############## Mysql Disconnect ###################
def mysql_close(db):
    try:
        db.close()
    except Exception, e:
        raise

################ Mysql query Execute ###############
def execute_query(db,dbase,query):
    db.select_db(dbase)
    cursor = db.cursor()
    cursor.execute(query)
    resultset = cursor.fetchall()
    cursor.close()
    db.commit()
    return(resultset)

################ Run ssh querry ####################
def execute_cmd(myet,operator,cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(myet.server_ip[operator], username=myet.user_ip[operator],password=myet.pass_ip[operator])
    stdin, stdout, stderr=ssh.exec_command(cmd)
    #stdin.write('hadoophive\n')
    #data=stdout.readlines()
    #fh = open('','w')
    #for line in data:
    #    f.write(line.strip('\n'))
    ssh.close()
    return 0


############ Pull data from remote servers #################
def pull(myet,operator,filename="*_count.txt"):

    if not os.path.exists(myet.dest_path[operator]):
        os.system("mkdir -p %s" %myet.dest_path[operator])
        print("Directory created %s" %myet.dest_path[operator])


    if myet.use_case[operator]=='1':

        display_details(myet,operator)

        try :
            print("scp -r %s@%s:%s/%s  %s" %(myet.user_ip[operator],myet.server_ip[operator],myet.source_path[operator],filename,myet.dest_path[operator]))
            foo5=pexpect.spawn("scp -r %s@%s:%s/%s  %s" %(myet.user_ip[operator],myet.server_ip[operator],myet.source_path[operator],filename,myet.dest_path[operator]))
            foo5.expect('.ssword:*')
            print("Sending password %s" %(myet.pass_ip[operator]))
            foo5.sendline("%s" %(myet.pass_ip[operator]))
            foo5.interact()
            foo5.close()
        except Exception,e:
            print("Exception for operator %s!" %myet.user_ip[operator])
            print(e)
            pass

    #case 2
    if myet.use_case[operator]=='2':
        #kill any active ports if any
        os.system("/sbin/fuser -k %s/tcp" %myet.port_one[operator])
        #display et details
        display_details(myet,operator)

        try :
            print("/usr/bin/ssh -o HostKeyAlias=%s -f -N -l %s -L %s:%s:22 %s" %(myet.sg_ip_one[operator],myet.sg_un_one[operator],myet.port_one[operator],myet.server_ip[operator],myet.sg_ip_one[operator]))
            foo9=pexpect.spawn("/usr/bin/ssh -o HostKeyAlias=%s -f -N -l %s -L %s:%s:22 %s" %(myet.sg_ip_one[operator],myet.sg_un_one[operator],myet.port_one[operator],myet.server_ip[operator],myet.sg_ip_one[operator]))
            foo9.expect('.ssword:*')
            print("Sending password %s" %myet.sg_pass_one[operator])
            foo9.sendline("%s" %myet.sg_pass_one[operator])
            #foo1.interact()
            foo9.close()
            print("Connection made to SG1 %s" %myet.sg_ip_one[operator])
        except Exception,e:
            print("Exception for operator %s first connection!" %operator)
            print (e)
            pass

        try :
            print("spawning")
            print("/usr/bin/scp -o HostKeyAlias=%s -P %s %s@localhost:%s/%s  %s" %(myet.server_ip[operator],myet.port_one[operator],myet.user_ip[operator],myet.source_path[operator],filename,myet.dest_path[operator]))
            foo8=pexpect.spawn("/usr/bin/scp -o HostKeyAlias=%s -P %s %s@localhost:%s/%s  %s" %(myet.server_ip[operator],myet.port_one[operator],myet.user_ip[operator],myet.source_path[operator],filename,myet.dest_path[operator]))
            foo8.expect('.ssword:*')
            print("sending password %s" %myet.pass_ip[operator])
            foo8.sendline("%s" %myet.pass_ip[operator])
            foo8.interact()
            foo8.close()
        except Exception,e:
            print("Exception for operator %s final scp!" %operator)
            print(e)
            pass

    #case 3
    if myet.use_case[operator]=='3':
        #kill active ports if any
        os.system("/sbin/fuser -k %s/tcp" %myet.port_one[operator])
        os.system("/sbin/fuser -k %s/tcp" %myet.port_two[operator])
        #display et details
        display_details(myet,operator)

        try :
            print("/usr/bin/ssh -o HostKeyAlias=%s -f -N -l %s -L %s:%s:22 %s" %(myet.sg_ip_one[operator],myet.sg_un_one[operator],myet.port_one[operator],myet.sg_ip_two[operator],myet.sg_ip_one[operator]))
            foo5=pexpect.spawn("/usr/bin/ssh -o HostKeyAlias=%s -f -N -l %s -L %s:%s:22 %s" %(myet.sg_ip_one[operator],myet.sg_un_one[operator],myet.port_one[operator],myet.sg_ip_two[operator],myet.sg_ip_one[operator]))
            foo5.expect('.ssword:*')
            print("Sending password %s" %myet.sg_pass_one[operator])
            foo5.sendline("%s\r\n" %myet.sg_pass_one[operator])
            foo5.sendline("\r\n")
            #foo5.interact()
            foo5.close()
            print("Connection made to SG1 %s" %myet.sg_ip_one[operator])
        except Exception,e:
            print("Exception for operator %s first connection!" %operator)
            print (e)
            pass
        try :
            print("/usr/bin/ssh -o HostKeyAlias=%s -p %s -f -N -l %s -L %s:%s:22 localhost" %(myet.sg_ip_two[operator],myet.port_one[operator],myet.sg_un_two[operator],myet.port_two[operator],myet.server_ip[operator]))
            foo6=pexpect.spawn("/usr/bin/ssh -o HostKeyAlias=%s -p %s -f -N -l %s -L %s:%s:22 localhost" %(myet.sg_ip_two[operator],myet.port_one[operator],myet.sg_un_two[operator],myet.port_two[operator],myet.server_ip[operator]))
            foo6.expect('.ssword:*')
            foo6.sendline("%s\r\n" %myet.sg_pass_two[operator])
            #foo6.interact()
            foo6.close()
            print("Connection made to SG2 %s" %myet.sg_ip_two[operator])
        except Exception,e:
            print("Exception for operator %s second connection!" %operator)
            print (e)
            pass

        try :
            print("/usr/bin/scp -o HostKeyAlias=%s -P %s %s@localhost:%s/%s  %s" %(myet.server_ip[operator],myet.port_two[operator],myet.user_ip[operator],myet.source_path[operator],filename,myet.dest_path[operator]))
            foo7=pexpect.spawn("/usr/bin/scp -o HostKeyAlias=%s -P %s %s@localhost:%s/%s %s" %(myet.server_ip[operator],myet.port_two[operator],myet.user_ip[operator],myet.source_path[operator],filename,myet.dest_path[operator]))
            foo7.expect('.ssword:*')
            print("Sending password %s" %myet.pass_ip[operator])
            foo7.sendline("%s\r\n" %myet.pass_ip[operator])
            #foo5.sendline("\r\n")
            foo7.interact()
            foo7.close()
        except Exception,e:
            print("Exception for operator %s final scp!" %operator)
            print(e)
            pass


if __name__=="__main__" :

    operator=sys.argv[1]
    monyear=sys.argv[2]

    cmd="nohup sh /home/%s/dump_counts.sh %s &" %(operator, monyear)
    
    myet=et()
    
    print cmd
    
    try:
        runcheck = execute_cmd(myet,operator,cmd)
    except Exception,e:
        print("cannot run querry")
    time.sleep(3600)
    if (runcheck == 0):
        filename="%s_count.txt" %(operator)
        pull(myet,operator,filename)
    
    print("Done!")

