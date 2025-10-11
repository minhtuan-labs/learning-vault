using P2PChatSystem.BootstrapService.Services;
using P2PChatSystem.Model;

namespace P2PChatSystem.BootstrapService.Application;

public interface IBootstrapServiceApp
{
	public Task<bool> registerPeer(string host, int port, string username,
		CancellationToken cancellationToken = default);
	public Task<List<TPeer>> getAllPeers(CancellationToken cancellationToken = default);
	public Task<bool> quit(string username, CancellationToken cancellationToken = default);
	public Task<bool> notifyDisconnectedPeer(string username, CancellationToken cancellationToken = default);
}

public class BootstrapServiceApp : IBootstrapServiceApp
{
	private Dictionary<string, TPeer> _peers = new Dictionary<string, TPeer>();

	public BootstrapServiceApp() {
		_peers.Clear();
	}

	public async Task<bool> registerPeer(string host, int port, string username, CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<bool>(cancellationToken);
		TPeer peer = new TPeer();
		peer.Host = host;
		peer.Port = port;
		peer.Username = username;
		_peers[username] = peer;
		foreach (var un in _peers.Keys) await new PeerServiceClient(_peers[un].Host, _peers[un].Port).updatePeers(new List<TPeer>(_peers.Values), cancellationToken);
		Console.WriteLine($"The new peer <{username}, {host}, {port}> has joined the network.");
		return true;
	}

	public async Task<List<TPeer>> getAllPeers(CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<List<TPeer>>(cancellationToken);
		return new List<TPeer>(_peers.Values);
	}

	public async Task<bool> quit(string username, CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<bool>(cancellationToken);
		if (_peers.Remove(username)) {
			foreach (var un in _peers.Keys) await new PeerServiceClient(_peers[un].Host, _peers[un].Port).updatePeers(new List<TPeer>(_peers.Values), cancellationToken);
			Console.WriteLine($"The peer <{username}> has quited the network.");
			return true;
		}

		return false;
	}

	public async Task<bool> notifyDisconnectedPeer(string username, CancellationToken cancellationToken = default) {
		return await quit(username, cancellationToken);
	}
}
