using System.Threading;
using P2PChatSystem.BootstrapService;
using P2PChatSystem.BootstrapService.Application;
using P2PChatSystem.Model;

namespace P2PChatSystem.BootstrapService.Handlers;

public class BootstrapServiceHandler : TBootstrapService.IAsync
{
	private IBootstrapServiceApp _bootstrapServiceApp = null;

	public BootstrapServiceHandler(IBootstrapServiceApp bootstrapServiceApp) {
		_bootstrapServiceApp = bootstrapServiceApp;
	}
	
	public async Task<bool> registerPeer(string host, int port, string username, CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<bool>(cancellationToken);
		return await _bootstrapServiceApp.registerPeer(host, port, username, cancellationToken);
	}

	public async Task<List<TPeer>> getAllPeers(CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<List<TPeer>>(cancellationToken);
		return await _bootstrapServiceApp.getAllPeers(cancellationToken);
	}

	public async Task<bool> quit(string username, CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<bool>(cancellationToken);
		return await _bootstrapServiceApp.quit(username, cancellationToken);
	}

	public async Task<bool> notifyDisconnectedPeer(string username, CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) return await Task.FromCanceled<bool>(cancellationToken);
		return await _bootstrapServiceApp.notifyDisconnectedPeer(username, cancellationToken);
	}
}
