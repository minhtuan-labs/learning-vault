using P2PChatSystem.BootstrapService;
using P2PChatSystem.PeerService.Model;
using P2PChatSystem.Model;
using Thrift;
using Thrift.Protocol;
using Thrift.Transport.Client;

namespace P2PChatSystem.PeerService.Services;

public class BootstrapServiceClient
{
	private string _host;
	private int _port;

	public BootstrapServiceClient(string host, int port) {
		_host = host;
		_port = port;
	}
	
	public async Task<bool> registerPeer(string host, int port, string username, CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<bool>(cancellationToken);

		bool result = false;
		TSocketTransport transport = new TSocketTransport(_host, _port, new TConfiguration());
		TBinaryProtocol.Factory protocolFactory = new TBinaryProtocol.Factory();
		try {
			// Open the transport only if it's not already open
			if (!transport.IsOpen) await transport.OpenAsync(cancellationToken);

			TProtocol protocol = protocolFactory.GetProtocol(transport);
			TBootstrapService.Client client = new TBootstrapService.Client(protocol);

			result = await client.registerPeer(host, port, username, cancellationToken);
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

	public async Task<List<TPeer>> getAllPeers(CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<List<TPeer>>(cancellationToken);

		List<TPeer> result = null;
		TSocketTransport transport = new TSocketTransport(_host, _port, new TConfiguration());
		TBinaryProtocol.Factory protocolFactory = new TBinaryProtocol.Factory();
		try {
			// Open the transport only if it's not already open
			if (!transport.IsOpen) await transport.OpenAsync(cancellationToken);

			TProtocol protocol = protocolFactory.GetProtocol(transport);
			TBootstrapService.Client client = new TBootstrapService.Client(protocol);

			result = await client.getAllPeers(cancellationToken);
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

	public async Task<bool> quit(string username, CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<bool>(cancellationToken);

		bool result = false;
		TSocketTransport transport = new TSocketTransport(_host, _port, new TConfiguration());
		TBinaryProtocol.Factory protocolFactory = new TBinaryProtocol.Factory();
		try {
			// Open the transport only if it's not already open
			if (!transport.IsOpen) await transport.OpenAsync(cancellationToken);

			TProtocol protocol = protocolFactory.GetProtocol(transport);
			TBootstrapService.Client client = new TBootstrapService.Client(protocol);

			result = await client.quit(username, cancellationToken);
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

	public async Task<bool> notifyDisconnectedPeer(string username, CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<bool>(cancellationToken);

		bool result = false;
		TSocketTransport transport = new TSocketTransport(_host, _port, new TConfiguration());
		TBinaryProtocol.Factory protocolFactory = new TBinaryProtocol.Factory();
		try {
			// Open the transport only if it's not already open
			if (!transport.IsOpen) await transport.OpenAsync(cancellationToken);

			TProtocol protocol = protocolFactory.GetProtocol(transport);
			TBootstrapService.Client client = new TBootstrapService.Client(protocol);

			result = await client.notifyDisconnectedPeer(username, cancellationToken);
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