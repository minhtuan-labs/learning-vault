using P2PChatSystem.Model;

namespace P2PChatSystem.PeerService.Application;

public class PeerServiceApp
{
	private Dictionary<string, TPeer> _peers = new Dictionary<string, TPeer>();

	public PeerServiceApp() {
		_peers.Clear();
	}

	public async Task<bool> sendMessage(string username, string message, CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<bool>(cancellationToken);
		Console.WriteLine($@"From {username}: {message}");
		return true;
	}

	public async Task<bool> updatePeers(List<TPeer> newPeers, CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<bool>(cancellationToken);
		_peers.Clear();
		foreach (var peer in newPeers) _peers.Add(peer.Username, peer);
		Console.WriteLine("The pool of peers has been updated.");
		return true;
	}

	public async Task<TPeer> getPeer(string username, CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<TPeer>(cancellationToken);
		if (_peers.ContainsKey(username)) return _peers[username];
		return null;
	}
}
