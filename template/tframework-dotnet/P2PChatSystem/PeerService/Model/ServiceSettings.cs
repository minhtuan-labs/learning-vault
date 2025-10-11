using Microsoft.Extensions.Configuration;

namespace P2PChatSystem.PeerService.Model;

public static class ServiceSettings
{
	public static string Name { get; set; }
	public static string Host { get; set; }
	public static int Port { get; set; }
	public static string Username { get; set; }
	public static string BootstrapService_Host { get; set; }
	public static int BootstrapService_Port { get; set; }

	public static void ParseServiceSettings(Dictionary<string, string> arguments) {
		IConfigurationBuilder builder = new ConfigurationBuilder().SetBasePath(AppContext.BaseDirectory)
			.AddJsonFile(arguments["c"], optional: false, reloadOnChange: true);
		IConfiguration configuration = builder.Build();

		Name = configuration.GetValue<string>("ServiceSettings:Name");
		Host = configuration.GetValue<string>("ServiceSettings:Host");
		Port = configuration.GetValue<int>("ServiceSettings:Port");
		Username = configuration.GetValue<string>("ServiceSettings:Username");
		BootstrapService_Host = configuration.GetValue<string>("ServiceSettings:BootstrapService:Host");
		BootstrapService_Port = configuration.GetValue<int>("ServiceSettings:BootstrapService:Port");
	}
}