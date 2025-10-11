// See https://aka.ms/new-console-template for more information

using TFramework;
using Thrift;
using Thrift.Protocol;
using Thrift.Transport.Client;

TSocketTransport transport = new TSocketTransport("localhost", 9090, new TConfiguration());
TBinaryProtocol.Factory protocolFactory = new TBinaryProtocol.Factory();
string message;

try {
	// Open the transport only if it's not already open
	if (!transport.IsOpen) {
		await transport.OpenAsync(CancellationToken.None);
	}

	TProtocol protocol = protocolFactory.GetProtocol(transport);
	TSampleService.Client client = new TSampleService.Client(protocol);

	Console.WriteLine("Enter message and send...");
	while (true) {
		Console.Write("Message: ");
		message = Console.ReadLine();
		if (message != "/quit") {
			await client.sendMessage(message, CancellationToken.None);
		}
		else break;
	}

	Console.WriteLine("The connection to the server is closed.");
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
