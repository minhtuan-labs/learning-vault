using TFramework;
using System.Threading;

namespace SampleServer;

public class ServiceHandler : TSampleService.IAsync
{
	public async Task sendMessage(string message, CancellationToken cancellationToken = default) {
		if (cancellationToken.IsCancellationRequested) {
			await Task.FromCanceled(cancellationToken);
			return;
		}
		Console.WriteLine("Received message: " + message);
		await Task.CompletedTask;
	}
}
