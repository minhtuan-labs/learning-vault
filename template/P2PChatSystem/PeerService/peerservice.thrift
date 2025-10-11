namespace netstd P2PChatSystem.PeerService

include "p2pchatsystem_datatypes.thrift"

service TPeerService {
    bool sendMessage(1: string username, 2: string message),
    bool updatePeers(1: list<p2pchatsystem_datatypes.TPeer> peers),
}

