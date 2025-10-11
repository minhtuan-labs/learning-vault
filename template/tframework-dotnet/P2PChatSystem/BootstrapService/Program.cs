// See https://aka.ms/new-console-template for more information

using P2PChatSystem.BootstrapService;
using Microsoft.Extensions.Configuration;
using P2PChatSystem.BootstrapService.Handlers;
using P2PChatSystem.BootstrapService.Application;
using P2PChatSystem.BootstrapService.Model;
using P2PChatSystem.BootstrapService.Services;
using Thrift;
using Thrift.Server;
using Thrift.Transport;
using Thrift.Protocol;
using Thrift.Transport.Server;

class Program
{
	private static CancellationTokenSource _cancellationTokenSource = new CancellationTokenSource();
	
	public static async Task Main(string[] args) {
		Console.CancelKeyPress += new ConsoleCancelEventHandler(OnExit);
		
		ParseServiceSettings(args);

		try {
			BootstrapServiceHandler handler = new BootstrapServiceHandler(new BootstrapServiceApp());
			TBootstrapService.AsyncProcessor processor = new TBootstrapService.AsyncProcessor(handler);

			TServerSocketTransport serverTransport =
				new TServerSocketTransport(ServiceSettings.Port, new TConfiguration());
			TBinaryProtocol.Factory protocolFactory = new TBinaryProtocol.Factory();

			TThreadPoolAsyncServer server =
				new TThreadPoolAsyncServer(processor, serverTransport, new TTransportFactory(), protocolFactory);

			Console.WriteLine("Starting the bootstrap server:");
			Console.WriteLine($" - Name: {ServiceSettings.Name}");
			Console.WriteLine($" - Host: {ServiceSettings.Host}");
			Console.WriteLine($" - Port: {ServiceSettings.Port}");

			await server.ServeAsync(_cancellationTokenSource.Token);
			//await server.ServeAsync(CancellationToken.None);
		}
		catch (Exception ex) {
			Console.WriteLine(ex.Message);
		}
	}

	static void ParseServiceSettings(string[] args) {
		Console.WriteLine("Hello!!!");
		Dictionary<string, string> arguments = ParseArguments(args);
		IConfigurationBuilder builder = new ConfigurationBuilder().SetBasePath(AppContext.BaseDirectory)
			.AddJsonFile(arguments["c"], optional: false, reloadOnChange: true);
		IConfiguration configuration = builder.Build();
		
		ServiceSettings.Name = configuration.GetValue<string>("ServiceSettings:Name");
		ServiceSettings.Host = configuration.GetValue<string>("ServiceSettings:Host");
		ServiceSettings.Port = configuration.GetValue<int>("ServiceSettings:Port");
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
		_cancellationTokenSource.Cancel();
		args.Cancel = true;
		Task.Delay(1000).Wait();
	}
}
