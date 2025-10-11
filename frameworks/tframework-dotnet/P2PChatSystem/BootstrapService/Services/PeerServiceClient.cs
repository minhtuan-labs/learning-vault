using System.Collections.Concurrent;
using P2PChatSystem.PeerService;
using Thrift;
using Thrift.Protocol;
using Thrift.Transport;
using Thrift.Transport.Client;

namespace P2PChatSystem.BootstrapService.Services;

public interface IPeerServiceClient
{
	public Task<bool> sendMessage(string username, string message, CancellationToken cancellationToken = default);
	public Task<bool> updatePeers(List<global::P2PChatSystem.Model.TPeer> peers,
		CancellationToken cancellationToken = default);
}

public class PeerServiceClient : IPeerServiceClient
{
	private string _host;
	private int _port;

	public PeerServiceClient(string host, int port) {
		_host = host;
		_port = port;
	}

	public async Task<bool> sendMessage(string username, string message,
		CancellationToken cancellationToken = default) {
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

	public async Task<bool> updatePeers(List<global::P2PChatSystem.Model.TPeer> peers,
		CancellationToken cancellationToken = default) {
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

/*public class PeerServiceConnectionPool
{
	private readonly string _host;
	private readonly int _port;
	private readonly int _maxPoolSize;
	private readonly ConcurrentBag<(TPeerService.Client Client, TTransport Transport)> _pool;

	public PeerServiceConnectionPool(string host, int port, int maxPoolSize = 10) {
		_host = host;
		_port = port;
		_maxPoolSize = maxPoolSize;
		_pool = new ConcurrentBag<(TPeerService.Client Client, TTransport Transport)>();
	}

	public (TPeerService.Client Client, TTransport Transport) GetClient() {
		if (_pool.TryTake(out var item)) return item;

		// Create a new connection if the pool is not full
		if (_pool.Count < _maxPoolSize) {
			TSocketTransport transport = new TSocketTransport(_host, _port, new TConfiguration());
			TBinaryProtocol.Factory protocolFactory = new TBinaryProtocol.Factory();
			TProtocol protocol = protocolFactory.GetProtocol(transport);
			TPeerService.Client client = new TPeerService.Client(protocol);

			// Open the transport
			transport.OpenAsync().Wait();

			return (client, transport);
		}
		else throw new InvalidOperationException("No available connections in the pool and pool limit reached.");
	}

	public void ReleaseClient(TPeerService.Client client, TTransport transport) {
		if (transport.IsOpen) _pool.Add((client, transport));
		else transport.Close();
	}

	public void Dispose() {
		foreach (var (client, transport) in _pool) transport.Close();
	}
}*/