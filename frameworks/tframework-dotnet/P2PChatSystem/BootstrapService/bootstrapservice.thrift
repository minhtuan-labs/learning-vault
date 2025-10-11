namespace netstd P2PChatSystem.BootstrapService

include "p2pchatsystem_datatypes.thrift"

service TBootstrapService {
    bool registerPeer(1: string host, 2: i32 port, 3: string username),
    list<p2pchatsystem_datatypes.TPeer> getAllPeers(),
    bool quit(1: string username),
    bool notifyDisconnectedPeer(1: string username)
}

