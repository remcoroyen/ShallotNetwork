## ShallotNetwork
Created by Remco Royen, Mathias De Roover, Quinten Deliens and Guylian Molineaux in 2017 for the course 'Communication Networks: Protocols and Architectures' at the Bruface Faculty (VUB + ULB)


### Introduction

This project creates a Shallot network (Tor-like network) allowing anonymous communication. Although the presented code is simulating the network on only one computer by using port numbers instead of IP-addresses, it can easily be extended to real networks over the internet.

### Installation

This project has been tested in an Python 3.9.2 environment (but probably also works with older distributions).

To install the required Python packages, execute the following command in the project folder:

```bash
pip install -r requirements.txt
```

### Usage

To use the default network topology to send a message to 'bob' from 'alice', running the following line in the python environment is sufficient.

```bash
python main.py
```

The command-line interface will allow step-by-step tracking of the steps.

To change the default network topology, hosts and associated IP-addresses (or ports in the virtual setting), the following steps have to be taken:

1. Open "config\host.ini" and "config\topology.ini"
2. Add/remove relays and change their neighbors (under [topology])
(Always make sure there is a path (via relays) from Alice to Bob and that there are no unconnected nodes!)

Further details can be found in report\Shallot_Network_Report.pdf

### License
Our code is released under MIT License (see LICENSE file for details).