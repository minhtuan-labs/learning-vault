using System.Threading;
using P2PChatSystem.PeerService;
using P2PChatSystem.PeerService.Application;
using P2PChatSystem.Model;

namespace P2PChatSystem.PeerService.Handlers;

public class PeerServiceHandler : TPeerService.IAsync
{
	private PeerServiceApp _peerServiceApp = null;
	
	public PeerServiceHandler(PeerServiceApp peerServiceApp) {
		_peerServiceApp = peerServiceApp;
	}

	public async Task<bool> sendMessage(string @username, string @message, CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<bool>(cancellationToken);
		return await _peerServiceApp.sendMessage(username, message, cancellationToken);
	}

	public async Task<bool> updatePeers(List<global::P2PChatSystem.Model.TPeer> @peers, CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<bool>(cancellationToken);
		return await _peerServiceApp.updatePeers(peers, cancellationToken);
	}
}
