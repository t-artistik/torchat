To avoid any potential confusion: This product is produced **independently** from the Tor® anonymity software, I am not related with or sponsored by torproject.org. TorChat is making use of the Tor® client software and the Windows version comes bundled with original Tor binaries but TorChat itself is a completely separate project developed by different people. TorChat is released as Free Software (GPL).

# TorChat has moved to GitHub #
**+++ Feb-05, 2012: This project has been moved to github https://github.com/prof7bit/TorChat +++**

**There are new files in the download section at github: https://github.com/prof7bit/TorChat/downloads**

**Further development of TorChat will continue at github, effective immediately. below is the old project page for historic reasons.**

---

If you like this software then maybe you want to buy me a **beer**. Simply click this button [![](http://www.paypal.com/en_US/i/btn/btn_donate_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&currency_code=EUR&lc=US&no_shipping=1&amp;tax=0;&bn=PP-DonationsBF&business=7bit@arcor.de&item_name=Buy+the+author+of+TorChat+a+beer!) to call for the waiter.

Alternatively there is also a BitCoin address: 18hmynLnHC44XiGiiPqfuTL3M4xPeJ5KqW

---

# TorChat #
TorChat is a peer to peer instant messenger with a completely decentralized design, built on top of Tor's location hidden services, giving you extremely strong anonymity while being very easy to use without the need to install or configure anything.

TorChat just runs from an USB drive on any Windows PC. (It can run on Linux and Mac too, in fact it was developed on Linux with cross platform usability in mind from the very first moment on, but the installation on other platforms than Windows is a bit more complicated at the moment)

Tor location hidden services basically means:
  * Nobody will be able to find out **where** you are.
  * If they are already observing you and sniff your internet connection they will **not** be able to find out
    * **what** you send or receive (everything is end-to-end encrypted)
    * to **whom** you are sending or receiving from
    * **where** your contacts are located

General information about Tor
  * [official site of the Tor project](http://www.torproject.org/)
  * [Tor Hidden Services](http://www.torproject.org/docs/hidden-services.html.en)
  * [Tor at Wikipedia](http://en.wikipedia.org/wiki/Tor_%28anonymity_network%29)

The Tor binary which is bundled with TorChat is taken from the official Tor-0.2.2.34 installer. You can binary compare the tor.exe with the official one to verify this or replace it with your own version of tor.exe if you like.

### Encryption ###
All TorChat traffic is encrypted end-to-end.


There are some misunderstandings floating around regarding Tor and encryption. Whenever I mention Tor and encryption in the same sentence the immediate reflex response of many people is: _"But Tor provides no encryption!"_ This statement is true for most applications but not for all. The most commonly known usage of Tor is to use it as an anonymizer for traffic between the anonymous user and a publicly available service in the Internet and while the traffic will travel encrypted through the Tor network it MUST at some point leave the Tor network and enter the unencrypted internet to reach its final destination. This is the origin of the above mentioned _"Tor provides no encryption"_ and it is undoubtedly true for this most widely known and practiced application of Tor and users should understand it.

However, there exists another and less commonly known mode of operation in which two Tor clients can initiate a **fully encrypted peer-to-peer** connection **between each other** that will **not** leave the Tor network at any point! This is what TorChat is using. Both clients build a normal 3 node circuit from each end to some random tor node in the middle to "meet" there and connect their circuits with each other. Upon connection another layer of encryption is established reaching through from one client to the other, building one uninterrupted encrypted tunnel through all 6 nodes between the two end points. This means all **TorChat traffic is end2end encrypted**. There are **no exit nodes** involved in this mode, at no point other than your and your buddies own computer will the traffic ever leave the Tor network.

This less known Tor mode is called **Tor hidden services**, you can read more about it on the above link. It effectively allows true hidden peer-to-peer networks, there are just not many softwares that make any use of its peer-to-peer capability, most use it more in a traditional client-server manner, TorChat is one of the few (and at the moment I don't know of any other).

### Authentication ###
TorChat buddies authenticate themselves by proving that they are reachable though their .onion address.

The Tor hidden service protocol by itself has no built-in authentication mechanism for incoming connections but it can guarantee that when you initiate an outgoing connection to a given .onion address you can never end up at the wrong counterpart, the one who answers the connection is the one who is in possession of the private key belonging to this address (the private\_key file in the hidden\_service folder).

Therefore TorChat will not trust any incoming connection and instead immediately try to open an outgoing connection to **call back** any incoming buddy on the address he pretends to be. A random cookie will then be sent out by both clients on their (trusted) outgoing connection that must be correctly answered on the incoming connection. Only after the answer is found to be correct the incoming connection can be trusted, the status of the buddy will be displayed as on-line and incoming messages from this buddy will be accepted.

It is essential that you don't lose the private\_key file belonging to your ID because the one who finds it will be able to pretend to be you. Using a tool like [TrueCrypt](http://www.truecrypt.org/) is a good idea when you intend to use TorChat on a portable USB drive as these devices can easily be lost or stolen.

# Installation #
### Windows ###
There basically is no need for any installation or configuration. It just **runs out of the box**, all batteries are included. Download and unzip the complete archive to somewhere on your harddisk or USB-Drive. The program is inside the folder "bin". Just doubleclick the blue earth symbol named "torchat" or "torchat.exe" to start the application and you should be online soon. See below for more detailed instructions on the usage.

**If you update** from an older version then do the following: Make sure both versions are not running and then copy the following three files from your old version over to the new version into the exact same locations:
  * bin\**buddy-list.txt**
  * bin\Tor\hidden\_service\**hostname**
  * bin\Tor\hidden\_service\**private\_key**

Now start the new version, make sure it is running and if everything is OK you should completely delete the old version.

buddy-list.txt contains the buddy list (obviously) and the two hidden service files are your TorChat ID (don't ever let these files come into the hands of anybody else, whoever owns these files would be able to pretend to be you!)

### Linux ###
The .deb package depends on python (>= 2.5, << 3.0) and python-wxgtk2.8 (aka wxPython) and tor. These should be easily satisfiable by any standard Debian or Ubuntu distribution, even older ones. Just make sure you have the latest official python from the 2.x branch installed, torchat will then find the correct version.

Download the torchat-x.x.x.x.deb package and do

`sudo dpkg -i torchat-x.x.x.x.deb`

where x.x.x.x should be replaced by the current version number. After that you can start it from the commandline with the command `torchat` or from the start menu of your desktop environment.

On non Debian based distributions make sure you have the above mentioned dependencies installed, then download the source distribution of TorChat, unzip it somewhere into your home folder and just execute it from within the src directory with the command

`python2 torchat.py`

or on older systems:

`python2.7 torchat.py`

or

`python2.6 torchat.py`

but do not try to run it with python 3.x, I have not yet made it compatible and Python 2.7 will still be around for a long time.

you can also try to use the tool `alien` to convert the `.deb` into an `.rpm` package and install it on a RedHad based system (untested, but I don't see why this should not work).

A package for **Arch Linux** has been made available here: http://aur.archlinux.org/packages.php?ID=23814

# It doesn't work? #
Please let me know about every unexpected behaviour, but first check the following list of things that are often done wrong:
  * Your firewall is blocking connections of tor.exe and torchat.exe: You must allow these two applications to open listening sockets and connect each other on 127.0.0.1 and also allow tor.exe to open outgoing connections to the internet.
  * You somehow managed to crash it and somehow an instance of tor.exe is still running. Kill it all with the task manager and try again. Normal is: **two** processes of torchat.exe (a very small one and a bigger one) and **one** process of tor.exe, everything else is not normal.
  * You are trying to run two copies of it on the same computer at the same time. This will not work! (It can be made to work but it needs some advanced configuration tweaks)
  * You started a copy of it with the **same ID** on a different computer at the same time. This cannot work. Never! You can use each ID only **once** at the same time, its strictly one-to-one connections, not one-to-many. To get a fresh ID you can either unzip a fresh copy from the download archive or delete the contents of the hidden\_service folder.

You can reach me via [E-Mail](mailto:prof7bit@gmail.com) or of course via TorChat, just use the "Ask Bernd" menu option and I will be added to your buddy list. My native language is **German**, but you can also talk to me in **English**.

# Usage #
This is how it should look like:

![http://torchat.googlecode.com/svn/trunk/torchat/screenshot.png](http://torchat.googlecode.com/svn/trunk/torchat/screenshot.png)

You will see a window with your contact list. One of the contacts is labled "myself". This 16 numbers and letters are **your** unique address inside the Tor-Network, this (myself) contact is always there and cannot be deleted. Wait a few minutes until the icon becomes green. Give this address (your TorChat ID) to your friends so that they can add you to their list **or** add your friends address to your list. It all basically behaves like you would expect from an instant messenger.

After starting TorChat it can sometimes take up to 15 Minutes until you will become available. If you see a blue ball next to one of the contacts this means it is in the middle of the conection handshake (it has already connected and is now waiting for the contact to connect you back). It should be less than a few minutes in this state and then be fully connected. If it does not go away for a long time for **some** of your contacts but others on your list work this might mean that **they** have some configuration problem or an outdated version, if you cannot see your own (myself) contact coming online then the problem is on your side. As soon as the myself-contact is green you **know** for sure that **your** TorChat is fully working!

You can run TorChat from an USB-Drive and no matter where you are, you always have the same address as long as you don't delete the files in the folder bin\Tor\hidden\_service. The contents of this folder are **your** **key**. They must always be kept **secret**. If someone wants to **impersonate** your identity he **must** and **will** try to steal the contents of this folder from you. Keep this always in mind. It would probably be a good idea to use TorChat in conjunction with something like [TrueCrypt](http://www.truecrypt.org/) or at least a password protected USB-Drive to **protect** your key file.

# China #
All known entries into the Tor network (including most known bridges) are currently blocked in China, this means you need a friend outside of China who runs a private (unpublished) bridge. A bridge is basically just an ordinary entry node with the exception that it does **not** show up in the public list of Tor nodes. The bridge should be unpublished because they cannot block something they don't know about. A published bridge would be blocked 1-2 weeks after it has been published and then it would be worthless.

### bridge ###
The helping friend needs to setup a Tor node with the following configuration:
```
SocksPort 0
ORPort 443
BridgeRelay 1
Exitpolicy reject *:*
PublishServerDescriptor 0
```
The last line is important to make it more robust against the Chinese censorship: The existence of this bridge will not be published anywhere, so it is not easy for them to learn about its existence. The port 443 is chosen because it is the same as https which is an extremely common and unsuspicious port and also the tor traffic looks exactly like legitimate https.

Please note that your friend will need to have a static IP address for this unpublished bridge to work. It should be run on a dedicated server that has its own IP address. Your friend should also consult the torproject website for additional information about setting up bridges, unpublished bridges, Tor and the China problem.

### TorChat using a bridge ###
After the helping friend has setup his Tor bridge as outlined above and given you the IP address you can add it to your TorChat configuration. Open your Tor\**torrc.txt** with notepad and add the following lines at the end of the file:
```
UseBridges 1
TunnelDirConns 1
bridge xxx.xxx.xxx.xxx:443
```
where the line `bridge xxx.xxx.xxx.xxx:443` would be given to you by your friend (it is IP address and port of your friend's bridge) and then (re)start TorChat. It should now be able to connect and everything should work fine.

If you have more than one friend with a bridge (recommended) or have additional bridge addresses from other sources then you can simply add more such bridge lines to the above configuration. You can add as many bridge lines as you want, the more the better. **Use TorChat to secretly and safely exchange more working (unblocked) bridge addresses with your Chinese friends!**

The connection to the bridge and everything you send through it is always encrypted, the owner of the bridge has no chance of ever finding out what and with whom you are communicating, its just a relay into the Tor network, like any other ordinary entry node, the only difference is it is not publicly known and not listed anywhere.

# Deployment of a preconfigured TorChat #
For maximum comfort when trying to torify one of your IM buddies (your grandma for example) who can't be bothered with adding cryptic character sequences to the buddy list you can download a fresh copy of TorChat, unzip and start it and add yourself to the buddy list of this new instance (note that you can only run one of them at the same time on the same computer). Then zip it again and give it to this person.

You can even prepare a whole bunch of such copies by adding each of them to each other's buddy-list with names next to the IDs and then supply a whole group of people all at once with readily configured copies of TorChat.

**If you are a journalist** you can prepare a version of TorChat with your own ID already on the list but with an **empty** hidden\_service folder and put this for download on your website or otherwise make it publicly available so that everybody (including whistle blowers) can (even if they have zero computer skills) simply unzip it and doubleclick on torchat.exe to instantly chat with you and send files in perfect anonymity from anywhere in the world!

You can also use this method to preconfigure and test a TorChat client like explained in the China section above and after making sure everything works correctly you can give it to your friend in China (be sure to use encrypted email or meet him personally to not reveal the IDs and the private\_key to the Chinese authorities).

Please never ever combine the last two methods (whistle blower + china bridge) in one TorChat because the fact that someone connects to **your** dedicated private bridge would directly expose his IP **to you**.


---


# Contact information #
Bernd Kreuss (author of TorChat)
  * E-Mail: [prof7bit@googlemail.com](mailto:prof7bit@googlemail.com)
  * E-Mail: [7bit@arcor.de](mailto:7bit@arcor.de)
  * TorChat: utvrla6mjdypbyw6

```
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1.4.6 (GNU/Linux)

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
z0+1r7Yc
=G8ZP
-----END PGP PUBLIC KEY BLOCK-----

```

If you want to buy me a beer:

[![](http://www.paypal.com/en_US/i/btn/btn_donate_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&currency_code=EUR&lc=US&no_shipping=1&amp;tax=0;&bn=PP-DonationsBF&business=7bit@arcor.de&item_name=Buy+the+author+of+TorChat+a+beer!)

If you want to buy the original Tor authors from torproject.org a beer (they deserve it even more) then please go here: https://www.torproject.org/donate/donate.html.en