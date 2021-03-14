## ShallotNetwork
Created by Remco Royen, Mathias De Roover, Quinten Deliens and Guylian Molineaux for the course 'Communication Networks: Protocols and Architectures' at the Bruface Faculty (VUB + ULB)


### Introduction

This project creates a 'virtual' Shallot network allowing ... .

### Installation

The shallot network is built using Python 3.6.3.

 - Cryptography:
In the command line type: "pip install cryptography"
(Or "py -3 -m pip install cryptography" or "pip3 install cryptography" when running multiple versions of Python)

 - pycrypto:
In the command line type: "pip install PyCryptoDome"
(Or "py -3 -m pip install PyCryptoDome"  or "pip3 install PyCryptoDome" when running multiple versions of Python)


OPTIONAL: Network initialisation

1. Open "config\host.ini" and "config\topology.ini"
2. Add/remove relays and change their neighbors (under [topology])
(Always make sure there is a path (via relays) from Alice to Bob and that there are no unconnected nodes!)

### Usage
From the command line, run "Shallot_Network.py" (using Python version 3!)

### License
Our code is released under MIT License (see LICENSE file for details).