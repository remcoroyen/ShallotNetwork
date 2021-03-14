# ShallotNetwork


	SHALLOT NETWORK
===============================

The shallot network is built using Python 3.6.3.


A) Libraries installation guide
---------------------------------

 - Cryptography:
In the command line type: "pip install cryptography"
(Or "py -3 -m pip install cryptography" or "pip3 install cryptography" when running multiple versions of Python)

 - pycrypto:
In the command line type: "pip install PyCryptoDome"
(Or "py -3 -m pip install PyCryptoDome"  or "pip3 install PyCryptoDome" when running multiple versions of Python)


OPTIONAL: B) Network initialisation
---------------------------------

1. Open "config\host.ini" and "config\topology.ini"
2. Add/remove relays and change their neighbors (under [topology])
(Always make sure there is a path (via relays) from Alice to Bob and that there are no unconnected nodes!)


B) Running the network
---------------------------------

From the command line, run "Shallot_Network.py" (using Python version 3!)


