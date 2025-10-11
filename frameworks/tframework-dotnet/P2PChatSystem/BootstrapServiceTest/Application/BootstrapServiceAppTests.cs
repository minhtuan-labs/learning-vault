using BootstrapService.Services;
using P2PChatSystem.Model;
using P2PChatSystem.BootstrapService.Application;
using NUnit.Framework;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Moq;

namespace BootstrapServiceTest.Application.Tests;

 [TestFixture]
    public class BootstrapServiceAppTests
    {
        private BootstrapServiceApp _bootstrapServiceApp;
        private Mock<IPeerServiceClient> _mockPeerServiceClient;

        [SetUp]
        public void SetUp()
        {
            _mockPeerServiceClient = new Mock<IPeerServiceClient>();
            _bootstrapServiceApp = new BootstrapServiceApp(_mockPeerServiceClient.Object);
        }

        [Test]
        public async Task RegisterPeer_ShouldAddPeerToNetwork()
        {
            // Arrange
            string host = "127.0.0.1";
            int port = 8080;
            string username = "user1";
            CancellationToken cancellationToken = CancellationToken.None;

            _mockPeerServiceClient
                .Setup(client => client.updatePeers(It.IsAny<List<TPeer>>(), cancellationToken))
                .Returns(Task.CompletedTask);

            // Act
            var result = await _bootstrapServiceApp.registerPeer(host, port, username, cancellationToken);

            // Assert
            Assert.IsTrue(result);
            var peers = await _bootstrapServiceApp.getAllPeers(cancellationToken);
            Assert.AreEqual(1, peers.Count);
            Assert.AreEqual(username, peers[0].Username);
            Assert.AreEqual(host, peers[0].Host);
            Assert.AreEqual(port, peers[0].Port);

            _mockPeerServiceClient.Verify(client => client.updatePeers(It.IsAny<List<TPeer>>(), cancellationToken), Times.Once);
        }

        [Test]
        public async Task GetAllPeers_ShouldReturnAllRegisteredPeers()
        {
            // Arrange
            await _bootstrapServiceApp.registerPeer("127.0.0.1", 8080, "user1");
            await _bootstrapServiceApp.registerPeer("127.0.0.1", 8081, "user2");

            // Act
            var peers = await _bootstrapServiceApp.getAllPeers();

            // Assert
            Assert.AreEqual(2, peers.Count);
            Assert.IsTrue(peers.Exists(p => p.Username == "user1"));
            Assert.IsTrue(peers.Exists(p => p.Username == "user2"));
        }

        [Test]
        public async Task Quit_ShouldRemovePeerFromNetwork()
        {
            // Arrange
            await _bootstrapServiceApp.registerPeer("127.0.0.1", 8080, "user1");

            _mockPeerServiceClient
                .Setup(client => client.updatePeers(It.IsAny<List<TPeer>>(), It.IsAny<CancellationToken>()))
                .Returns(Task.CompletedTask);

            // Act
            var result = await _bootstrapServiceApp.quit("user1");

            // Assert
            Assert.IsTrue(result);
            var peers = await _bootstrapServiceApp.getAllPeers();
            Assert.AreEqual(0, peers.Count);

            _mockPeerServiceClient.Verify(client => client.updatePeers(It.IsAny<List<TPeer>>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        [Test]
        public async Task NotifyDisconnectedPeer_ShouldRemovePeerFromNetwork()
        {
            // Arrange
            await _bootstrapServiceApp.registerPeer("127.0.0.1", 8080, "user1");

            _mockPeerServiceClient
                .Setup(client => client.updatePeers(It.IsAny<List<TPeer>>(), It.IsAny<CancellationToken>()))
                .Returns(Task.CompletedTask);

            // Act
            var result = await _bootstrapServiceApp.notifyDisconnectedPeer("user1");

            // Assert
            Assert.IsTrue(result);
            var peers = await _bootstrapServiceApp.getAllPeers();
            Assert.AreEqual(0, peers.Count);

            _mockPeerServiceClient.Verify(client => client.updatePeers(It.IsAny<List<TPeer>>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        [Test]
        public void RegisterPeer_WithCancellation_ShouldReturnCanceledTask()
        {
            // Arrange
            string host = "127.0.0.1";
            int port = 8080;
            string username = "user1";
            var cts = new CancellationTokenSource();
            cts.Cancel();

            // Act & Assert
            Assert.ThrowsAsync<TaskCanceledException>(async () =>
                await _bootstrapServiceApp.registerPeer(host, port, username, cts.Token));
        }

        [Test]
        public void Quit_WithCancellation_ShouldReturnCanceledTask()
        {
            // Arrange
            string username = "user1";
            var cts = new CancellationTokenSource();
            cts.Cancel();

            // Act & Assert
            Assert.ThrowsAsync<TaskCanceledException>(async () =>
                await _bootstrapServiceApp.quit(username, cts.Token));
        }
    }
    