# Guide to Building the MUD Architecture for Enterprises: FreeRadius

## Introduction  
MUD is a form of IoT security that looks at ways by which manufacturers explain to network deployments what L3/L4 communication patterns they designed their devices to use.

The basic concept makes use of a URL that is put out by a device using one of several mechanisms, such as DHCP, LLDP, or as part of an 802.1AR certificate in an EAP-TLS/802.1X authentication.  The URL is then resolved to go get a JSON-encoded YANG-based policy.

The goal of MUD is to *reduce* the threat surface on a device to just that of those specific services on specific systems that are expected to communicate with a Thing.

The steps in this guide are based on [instructions](https://github.com/elear/mud/blob/master/demo_code/Readme_Python_Pub_PDF.pdf) written by [Eliot Lear](https://github.com/elear) for demoing his mud controller code. The device emits a URL by means of 802.1AR certificate in an EAP-TLS/802.1X authentication, which is processed and approved by a FreeRadius server.

## Instructions
### Set Up FreeRadius Server on Ubuntu Virtual Machine
1. Ensure your system is updated:
```bash
$ sudo apt-get update  
$ sudo apt-get upgrade
```
1. In your project directory, download FreeRADIUS 3.0x Series-Stable using wget:
```bash
$ wget https://github.com/FreeRADIUS/freeradius-server/archive/release_3_0_11.tar.gz
```
1. Unzip .tar.gz file:
```bash
$ tar -xvzf release_3_0_11.tar.gz
```

1. Ensure that libtalloc and libcrypto are installed:
```bash
$ sudo apt-get install libtalloc-dev
$ sudo apt-get install libssl-dev
```
1. Enter the freeradius-server-release_3_0_11 directory:
```bash
$ cd freeradius-server-release_3_0_11
```  
Configure, make, and install:
```bash
$ ./configure
$ make
$ sudo make install
```
1. All the associated FreeRADIUS folders should be in the appropriate places now. Create a new vendor dictionary file called **dictionary.mudserver** in /usr/local/share/freeradius/ and copy and paste the text below:
```
######################################################################
VENDOR            CISCO-IOT        16122
BEGIN-VENDOR      CISCO-IOT
ATTRIBUTE         Cisco-MUD-URI    1        string
END-VENDOR CISCO-IOT  
######################################################################
```
1. Open /usr/local/share/freeradius/dictionary file and locate the lines:
```
$INCLUDE dictionary.motorola
$INCLUDE dictinary.motrola.wimax
```
**Add the following on the next line:**
```
$INCLUDE dictionary.mudserver
```
1. Create a user by adding a User-Name and Cleartext-Password. Find the following lines in /usr/local/etc/raddb/users:
```
#bob Cleartext-Password := “hello”
# Reply-Message := “Hello, %{User-Name}”
```
**Add your information below it in the following format:**
```
<username> Cleartext-Password := “<password>”
```
1.  /usr/local/etc/raddb/clients.conf must be modified if you plan to run the server on a separate host. If using localhost only, this file can remain the same.

1. Change the exec configuration in /usr/local/etc/raddb/mods-enabled/exec from wait “no” to “yes”.

1. In /usr/local/etc/raddb/sites-enabled/default, add the following code in the “authorize” section after “filter_username”:
```
if (User-Name == "%{exec:/usr/bin/python/usr/local/etc/controller/mud_controller.py ‘null’ 'U1'}.in") {
    update control {
        Auth-Type := Accept
    }
}
if (User-Name == "%{exec:/usr/bin/python /usr/local/etc/controller/mud_controller.py 'null' 'U2'}.out") {
    update control {
        Auth-Type := Accept
    }
}
```
__Be sure that no newline characters are inserted in the middle of a long file path.__
1. In the same file at the “post-auth” section, after “exec”, add the following lines:
```
if (Cisco-MUD-URI) {
    if (User-Name == "<username>") {
        update reply {
            Exec-Program = "%{exec:/usr/bin/python /usr/local/etc/controller/mud_controller.py %{Cisco- MUD-URI} 'W'}"
            Cisco-AVPair := "ACS:CiscoSecure-Defined-ACL=%{exec:/usr/bin/python /usr/local/etc/controller/mud_controller.py 'null' 'U1'}.in",
            Cisco-AVPair += "ACS:CiscoSecure-Defined-ACL=%{exec:/usr/bin/python /usr/local/etc/controller/mud_controller.py 'null' 'U2'}.out"
        }
    }
    if (User-Name == "%{exec:/usr/bin/python /usr/local/etc/controller/mud_controller.py 'null' 'U1'}.in") {
        update reply {
            User-Name = "%{exec:/usr/bin/python /usr/local/etc/controller/mud_controller.py 'null' 'U1'}",
            Cisco-AVPair := "ip:inacl#1=%{exec:/usr/bin/python /usr/local/etc/controller/mud_controller.py ‘null’ ‘R1’}”,
            Cisco-AVPair += "ip:inacl#2=permit udp any any eq 67",
            Cisco-AVPair += "ip:inacl#3=permit udp any any eq 68",
            Cisco-AVPair += "ip:inacl#4=%{exec:/usr/bin/python /usr/local/etc/controller/mud_controller.py ‘null’ ‘R3’}”,
            Reply-Message += "DACL Ingress Downloaded Successfully.”,
        }
    }
    if (User-Name == "%{exec:/usr/bin/python /usr/local/etc/controller/mud_controller.py 'null' 'U2'}.out") {
        update reply {
            User-Name = "%{exec:/usr/bin/python /usr/local/etc/controller/mud_controller.py 'null' 'U2'}.out",
            Cisco-AVPair := "ip:outacl#1=%{exec:/usr/bin/python /usr/local/etc/controller/mud_controller.py 'null' 'R2'}",
            Cisco-AVPair += "ip:outacl#2=permit udp any any eq 67",
            Cisco-AVPair += "ip:outacl#3=permit udp any any eq 68",
            Cisco-AVPair += "ip:outacl#4=%{exec:/usr/bin/python/usr/local/etc/controller/mud_controller.py 'null' 'R3'}",
            Reply-Message += "DACL Egress Downloaded Successfully."
        }
    }
}
```
__Be sure to change `<username>` to the username you have assigned in the users file.__

1. Replace the __tls.c__ file under freeradius-server-release_3_0_11/src/main/ with the tls.c file from our github. \*A patch file was originally provided but was not compatible with our tls file. A new patch is being made.

1. Under freeradius-server-release_3_0_11/share/ open __dictionary.freeradius.internal__ and locate the line:
```
ATTRIBUTE    TLS-PSK-Identity                        1933    string
```
Add below it:
```
ATTRIBUTE    TLS-Client-Cert-Subject-Alt-Name-URI    1934    string
```
1. Now,
```bash
$ cd ..
$ ./configure
$ make
$ sudo make install
```
1.  Attempt to start FreeRADIUS in debugging mode by running the following command:
```bash
$ sudo radiusd -x
```
If this does not work, make sure that FreeRADIUS is not already running as a background process. To check:
```bash
$ ps aux
```
find the pid of FreeRADIUS. If it's there,
```bash
$ kill -9 <pid of FreeRADIUS>
```

### Set Up at Enterprise Side where MUD Files are Stored
1. In your home/project directory, make a project folder entitled “enterprise_mud”
```bash
$ mkdir enterprise_mud
```
1. Underneath enterprise_mud directory, create directories “mud" and “private”
```bash
$ mkdir mud private
```
1. Follow this link to generate MUD file https://www.ofcourseimright.com/mudmaker/

1. Save and download the .json file you generated to your new mud directory

1. In the mud folder, generate key and self-signed certificate using the following commands:
```bash
$ openssl genrsa -out key.pem 2048
$ openssl req -new -x509 -key key.pem -out ck.pem
```
1. Sign and verify the MUD file using the following commands:
```bash
$ openssl cms -sign -in <name of MUD file>.json -signer ck.pem -inkey key.pem -binary -outform DER -out <name of MUD file>.p7s
$ openssl cms -verify -in <name of MUD file>.p7s -out mud.json -CAfile ck.pem -inform DER -content <name of MUD file>.json
```
The output of the second command should be “Verification successful”
If you receive error message “unable to write ‘random state,’" use elevated permissions

1. Move key.pem to the private folder and change access permissions:
```bash
$ mv key.pem ../private
$ chmod 700 ../private
$ chmod 700 ../private/key.pem
```
1. Create a directory called “controller” under /usr/local/etc
```bash
$ mkdir controller
```
1. Download and copy mud_controller.py file into /usr/local/etc/controller directory from our private github for compatibility with the mud file generator. If you have generated your own mud files that adhere to the draft specification, you may want to download Eliot Lear's controller: https://github.com/elear/mud

1. Copy ck.pem to the controller directory by running the following command from the enterprise_mud/mud directory:
```bash
$ cp ck.pem /usr/local/etc/controller
```
1. Run SimpleHTTPServer in the enterprise_mud directory:
```bash
$ python -m SimpleHTTPServer 127.0.0.1:8000
```

### Testing MUD Controller
1. With SimpleHTTPServer running, run the following command in the controller directory:
```bash
$ python mud_controller.py http://localhost:8000/mud/<name of MUD file>.json W
```

On success, the output will be “Verification successful” and three files should appear in the controller directory:
`<name of MUD fille>.json`
`<name of MUD file>.p7s`
`mud.json`

### Testing the Radius Client
1. Start the radius server in debugging mode.

1. With SimpleHTTPServer still running, enter the following command:
```bash
$ echo “User-Name=<username>, User-Password=<password>, Cisco-MUD-URI=http:// 127.0.0.1:8000/mud/<name of MUD file>.json” | /usr/local/bin/radclient -x localhost:1812 auth testing123
```
Change `<username>` and `<password>` to username and password specified in the users file.

1. On success, the output will indicate that an Access-Request Id was sent and an Access- Accept Id was received.

## Appendix
### Supplicant Authentication with Certificates
1. Generate client key
```bash
$ openssl genrsa -out light.key
```
1. Make certificate request config file __mudREQ.conf__. Copy-paste:  

```

# The main section is named req because the command we are using is req
# (openssl req ...)
[ req ]

# This specifies the default key size in bits. If not specified then 512 is
# used. It is used if the -new option is used. It can be overridden by using
# the -newkey option.
default_bits = 2048

# This is the default filename to write a private key to. If not specified the
# key is written to standard output. This can be overridden by the -keyout
# option.
default_keyfile = light.key

# If this is set to no then if a private key is generated it is not encrypted.
# This is equivalent to the -nodes command line option. For compatibility
# encrypt_rsa_key is an equivalent option.
encrypt_key = no

# This option specifies the digest algorithm to use. Possible values include
# md5 sha1 mdc2. If not present then MD5 is used. This option can be overridden
# on the command line.
default_md = sha1

# if set to the value no this disables prompting of certificate fields and just
# takes values from the config file directly. It also changes the expected
# format of the distinguished_name and attributes sections.
prompt = no

# if set to the value yes then field values to be interpreted as UTF8 strings,
# by default they are interpreted as ASCII. This means that the field values,
# whether prompted from a terminal or obtained from a configuration file, must
# be valid UTF8 strings.
utf8 = yes

# This specifies the section containing the distinguished name fields to
# prompt for when generating a certificate or certificate request. distinguished_name = my_req_distinguished_name
# this specifies the configuration file section containing a list of extensions
# to add to the certificate request. It can be overridden by the -reqexts
# command line switch. See the x509v3_config(5) manual page for details of the
# extension section format.
req_extensions = my_extensions
[ my_req_distinguished_name ] C = PT
ST = Lisboa
L = Lisboa
O = Oats In The Water CN = *.oats.org
[ my_extensions ] subjectAltName=@my_subject_alt_names
[ my_subject_alt_names ]
URI = http://localhost/mud/lighting-example.json
```


1. Generate request
```bash
$ openssl req -new light.csr -config mudREQ.conf
Generating a 2048 bit RSA private key
. . . . . . . . . . . . +++
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . +++
writing new private key to ‘oats.key’
— — — —
```
1. Optionally read request contents:
```bash
$ openssl req -in light.csr -noout -text
```   

### Create CA
1. Generate CA's key
```bash
$ openssl genrsa -out mudCA.key 2048
Generating RSA private key, 2048 bit long modulus
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . +++ . . . . . . . . . +++
e is 65537 (0x10001)
```
1. Generate self-signed certificate for CA:
```
$ openssl req -new -x509 -key mudCA.key -out mudCA.crt
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN. There are quite a few fields but you can leave some blank
For some fields there will be a default value, If you enter '.', the field will be left blank. -----
Country Name (2 letter code) [AU]:PT
State or Province Name (full name) [Some-State]:Lisboa
Locality Name (eg, city) []:Lisboa
Organization Name (eg, company) [Internet Widgits Pty Ltd]:Sz CA Organizational Unit Name (eg, section) []:SZ CA
Common Name (e.g. server FQDN or YOUR name) []: Email Address []:An optional company name []:
```

1. Create CA configuration file __ca.conf__ (copy-paste file contents):
```
# we use 'ca' as the default section because we're usign the ca command # we use 'ca' as the default section because we're usign the ca command [ ca ]
default_ca = my_ca
[ my_ca ]
# a text file containing the next serial number to use in hex. Mandatory. # This file must be present and contain a valid serial number.
serial = ./serial
# the text database file to use. Mandatory. This file must be present though # initially it will be empty.
database = ./index.txt
# specifies the directory where new certificates will be placed. Mandatory. new_certs_dir = ./newcerts
# the file containing the CA certificate. Mandatory certificate = ./mudCA.crt
# the file contaning the CA private key. Mandatory private_key = ./mudCA.key
# the message digest algorithm. Remember to not use MD5 default_md = sha1
# for how many days will the signed certificate be valid default_days = 365
# a section with a set of variables corresponding to DN fields policy = my_policy
[ my_policy ]
# if the value is "match" then the field value must match the same field in the # CA certificate. If the value is "supplied" then it must be present.
# Optional means it may be present. Any fields not mentioned are silently
# deleted.
countryName = match
stateOrProvinceName = supplied
organizationName = supplied
[ ca ]
default_ca = my_ca
```
1. Create CA extension configuration file __ca.ext.cnf__ (copy-paste file contents):
```
subjectAltName=@my_subject_alt_names
[ my_subject_alt_names ]
URI = http://localhost/mud/lighting-example.json
```
1. Set up CA record-keeping files:
```bash
$ mkdir newcerts
$ touch index.txt
$ echo '01' > serial
```
1. Sign certificate request with CA cert:
```
$ openssl ca -config ca.conf -out light.crt -extfile ca.ext.cnf -in light.csr Using configuration from ca.cnf
Check that the request matches the signature
Signature ok
The Subject's Distinguished Name is as follows countryName :PRINTABLE:'PT' stateOrProvinceName :PRINTABLE:'Lisboa'
localityName
organizationName
commonName
Certificate is to be certified until Mar 21 01:43:11 2015 GMT (365 days) Sign the certificate? [y/n]:y
:PRINTABLE:'Lisboa' :PRINTABLE:'Oats In The Water' :T61STRING:'*.oats.org'
1 out of 1 certificate requests certified, commit? [y/n]y Write out database with 1 new entries
Data Base Updated
```
1. Verify the certificate:
```bash
$ openssl verify -CAfile mudCA.crt light.crt
```
