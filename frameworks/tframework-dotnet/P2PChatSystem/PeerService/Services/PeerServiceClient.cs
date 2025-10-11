using P2PChatSystem.PeerService.Model;
using P2PChatSystem.PeerService;
using Thrift;
using Thrift.Protocol;
using Thrift.Transport.Client;

namespace P2PChatSystem.PeerService.Services;

public class PeerServiceClient
{
	private string _host;
	private int _port;
	
	public PeerServiceClient(string host, int port) {
		_host = host;
		_port = port;
	}
	
	public async Task<bool> sendMessage(string username, string message, CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<bool>(cancellationToken);
		
		bool result = false;
		TSocketTransport transport = new TSocketTransport(_host, _port, new TConfiguration());
		TBinaryProtocol.Factory protocolFactory = new TBinaryProtocol.Factory();
		try {
			// Open the transport only if it's not already open
			if (!transport.IsOpen) await transport.OpenAsync(cancellationToken);

			TProtocol protocol = protocolFactory.GetProtocol(transport);
			TPeerService.Client client = new TPeerService.Client(protocol);
			
			result = await client.sendMessage(username, message, cancellationToken);
		}
		catch (Exception ex) {
			new BootstrapServiceClient(ServiceSettings.BootstrapService_Host, ServiceSettings.BootstrapService_Port)
				.notifyDisconnectedPeer(username, cancellationToken);
			Console.WriteLine($"An error occurred: {ex.Message}");
		}
		finally {
			// Ensure transport is closed
			if (transport.IsOpen) {
				try {
					transport.Close();
				}
				catch (Exception closeEx) {
					Console.WriteLine($"An error occurred while closing the transport: {closeEx.Message}");
				}
			}
		}

		return result;
	}

	public async Task<bool> updatePeers(List<global::P2PChatSystem.Model.TPeer> peers, CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<bool>(cancellationToken);
		
		bool result = false;
		TSocketTransport transport = new TSocketTransport(_host, _port, new TConfiguration());
		TBinaryProtocol.Factory protocolFactory = new TBinaryProtocol.Factory();
		try {
			// Open the transport only if it's not already open
			if (!transport.IsOpen) await transport.OpenAsync(cancellationToken);

			TProtocol protocol = protocolFactory.GetProtocol(transport);
			TPeerService.Client client = new TPeerService.Client(protocol);
			
			result = await client.updatePeers(peers, cancellationToken);
		}
		catch (Exception ex) {
			Console.WriteLine($"An error occurred: {ex.Message}");
		}
		finally {
			// Ensure transport is closed
			if (transport.IsOpen) {
				try {
					transport.Close();
				}
				catch (Exception closeEx) {
					Console.WriteLine($"An error occurred while closing the transport: {closeEx.Message}");
				}
			}
		}

		return result;
	}
}
