// See https://aka.ms/new-console-template for more information

using P2PChatSystem.PeerService.Services;
using Microsoft.Extensions.Configuration;
using P2PChatSystem.PeerService.Application;
using P2PChatSystem.PeerService.Model;
using P2PChatSystem.Model;
using P2PChatSystem.PeerService.Handlers;
using P2PChatSystem.PeerService;
using Thrift;
using Thrift.Server;
using Thrift.Transport;
using Thrift.Protocol;
using Thrift.Transport.Server;

class Program
{
	private static PeerServiceApp _peerServiceApp;
	private static CancellationTokenSource _cancellationTokenSource = new CancellationTokenSource();
	
	public static async Task Main(string[] args) {
		Console.CancelKeyPress += new ConsoleCancelEventHandler(OnExit);
		
		ServiceSettings.ParseServiceSettings(ParseArguments(args));
		new BootstrapServiceClient(ServiceSettings.BootstrapService_Host, ServiceSettings.BootstrapService_Port).registerPeer(ServiceSettings.Host, ServiceSettings.Port, ServiceSettings.Username);
		
		RunHandler();
		StartChat();
		_cancellationTokenSource.Cancel();
	}
	
	static void RunHandler() {
		try {
			_peerServiceApp = new PeerServiceApp();
			PeerServiceHandler handler = new PeerServiceHandler(_peerServiceApp);
			TPeerService.AsyncProcessor processor = new TPeerService.AsyncProcessor(handler);

			TServerSocketTransport serverTransport =
				new TServerSocketTransport(ServiceSettings.Port, new TConfiguration());
			TBinaryProtocol.Factory protocolFactory = new TBinaryProtocol.Factory();

			TThreadPoolAsyncServer server =
				new TThreadPoolAsyncServer(processor, serverTransport, new TTransportFactory(), protocolFactory);

			Console.WriteLine("Starting the peer:");
			Console.WriteLine($" - Name: {ServiceSettings.Name}");
			Console.WriteLine($" - Host: {ServiceSettings.Host}");
			Console.WriteLine($" - Port: {ServiceSettings.Port}");
			Console.WriteLine($" - Username: {ServiceSettings.Username}");
			
			Task.Run(() => server.ServeAsync(_cancellationTokenSource.Token), _cancellationTokenSource.Token);
			//await server.ServeAsync(CancellationToken.None);
		}
		catch (Exception ex) {
			Console.WriteLine(ex.Message);
		}
	}

	static void StartChat() {
		string username, message;
		int pos;
		TPeer peer;
		while (true) {
			message = Console.ReadLine();
			if (message != null) {
				if (message.StartsWith("/quit")) {
					new BootstrapServiceClient(ServiceSettings.BootstrapService_Host,
							ServiceSettings.BootstrapService_Port)
						.quit(ServiceSettings.Username);
					return;
				}
				else if (message.StartsWith("@")) {
					pos = message.IndexOf(" ");
					username = message.Substring(1, pos - 1);
					message = message.Substring(pos + 1);
					peer = _peerServiceApp.getPeer(username).Result;
					if (peer != null) new PeerServiceClient(peer.Host, peer.Port).sendMessage(ServiceSettings.Username, message);
					else Console.WriteLine($"{username} is not online!!!"); 
				}
				else Console.WriteLine("Your message should be in the format \"/quit\" or \"@<username> <message>.");
			}
			else {
				new BootstrapServiceClient(ServiceSettings.BootstrapService_Host,
						ServiceSettings.BootstrapService_Port)
					.quit(ServiceSettings.Username);
				return;
			}
		}
	}
	
	static Dictionary<string, string> ParseArguments(string[] args) {
		Dictionary<string, string> arguments = new Dictionary<string, string>();
		arguments.Clear();

		for (int i = 0; i < args.Length; i++) {
			if (args[i].StartsWith("-")) {
				if (i + 1 < args.Length && !args[i + 1].StartsWith("-")) {
					arguments[args[i].TrimStart('-')] = args[i + 1];
					i++;
				}
				else arguments[args[i].TrimStart('-')] = string.Empty;
			}
		}

		return arguments;
	}

	protected static void OnExit(object sender, ConsoleCancelEventArgs args) {
		new BootstrapServiceClient(ServiceSettings.BootstrapService_Host, ServiceSettings.BootstrapService_Port)
			.quit(ServiceSettings.Username);
		_cancellationTokenSource.Cancel();
		args.Cancel = true;
		Task.Delay(1000).Wait();
	}
}