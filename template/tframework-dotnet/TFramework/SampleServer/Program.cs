// See https://aka.ms/new-console-template for more information

using SampleServer;
using TFramework;
using Thrift;
using Thrift.Server;
using Thrift.Transport;
using Thrift.Protocol;
using Thrift.Transport.Server;

ServiceHandler handler = new ServiceHandler();
TSampleService.AsyncProcessor processor = new TSampleService.AsyncProcessor(handler);

TServerSocketTransport serverTransport = new TServerSocketTransport(9090, new TConfiguration());
TBinaryProtocol.Factory protocolFactory = new TBinaryProtocol.Factory();

TThreadPoolAsyncServer server = new TThreadPoolAsyncServer(processor, serverTransport, new TTransportFactory(), protocolFactory);

Console.WriteLine("Starting the async server...");

await server.ServeAsync(CancellationToken.None);

server.Stop();
serverTransport.Close();
