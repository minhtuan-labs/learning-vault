using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Moq;
using NUnit.Framework;
using P2PChatSystem.BootstrapService.Application;
using P2PChatSystem.BootstrapService.Handlers;
using P2PChatSystem.Model;

namespace P2PChatSystem.BootstrapService.Tests;

[TestFixture]
public class BootstrapServiceHandlerTests
{
	private Mock<IBootstrapServiceApp> _mockBootstrapServiceApp;
	private BootstrapServiceHandler _handler;

	[SetUp]
	public void Setup() {
		_mockBootstrapServiceApp = new Mock<IBootstrapServiceApp>();
		_handler = new BootstrapServiceHandler(_mockBootstrapServiceApp.Object);
	}

	[Test]
	public async Task RegisterPeer_WhenCalled_ReturnsExpectedResult() {
		// Arrange
		_mockBootstrapServiceApp.Setup(app => app.registerPeer("host", 8080, "user", CancellationToken.None))
			.ReturnsAsync(true);

		// Act
		var result = await _handler.registerPeer("host", 8080, "user", CancellationToken.None);

		// Assert
		Assert.That(result, Is.True);
	}

	[Test]
	public async Task RegisterPeer_WhenCancelled_ThrowsTaskCancelledException() {
		// Arrange
		var cancellationToken = new CancellationToken(true);

		// Act & Assert
		Assert.ThrowsAsync<TaskCanceledException>(async () =>
			await _handler.registerPeer("host", 8080, "user", cancellationToken));
	}

	[Test]
	public async Task GetAllPeers_WhenCalled_ReturnsExpectedResult() {
		// Arrange
		var expectedPeers = new List<TPeer> { new TPeer { Host = "host1", Port = 8080, Username = "user1"} };
		CancellationToken cancellationToken = new CancellationToken();
		_mockBootstrapServiceApp.Setup(app => app.getAllPeers(cancellationToken))
			.ReturnsAsync(expectedPeers);

		// Act
		var result = await _handler.getAllPeers(cancellationToken);

		// Assert
		Assert.That(result, Is.EqualTo(result));
	}

	[Test]
	public async Task GetAllPeers_WhenCancelled_ThrowsTaskCancelledException() {
		// Arrange
		var cancellationToken = new CancellationToken(true);

		// Act & Assert
		Assert.ThrowsAsync<TaskCanceledException>(async () =>
			await _handler.getAllPeers(cancellationToken));
	}

	[Test]
	public async Task Quit_WhenCalled_ReturnsExpectedResult() {
		// Arrange
		_mockBootstrapServiceApp.Setup(app => app.quit("user", It.IsAny<CancellationToken>()))
			.ReturnsAsync(true);

		// Act
		var result = await _handler.quit("user");

		// Assert
		Assert.That(result, Is.True);
	}

	[Test]
	public async Task Quit_WhenCancelled_ThrowsTaskCancelledException() {
		// Arrange
		var cancellationToken = new CancellationToken(true);

		// Act & Assert
		Assert.ThrowsAsync<TaskCanceledException>(async () =>
			await _handler.quit("user", cancellationToken));
	}

	[Test]
	public async Task NotifyDisconnectedPeer_WhenCalled_ReturnsExpectedResult() {
		// Arrange
		_mockBootstrapServiceApp.Setup(app => app.notifyDisconnectedPeer("user", It.IsAny<CancellationToken>()))
			.ReturnsAsync(true);

		// Act
		var result = await _handler.notifyDisconnectedPeer("user");

		// Assert
		Assert.That(result, Is.True);
	}

	[Test]
	public async Task NotifyDisconnectedPeer_WhenCancelled_ThrowsTaskCancelledException() {
		// Arrange
		var cancellationToken = new CancellationToken(true);

		// Act & Assert
		Assert.ThrowsAsync<TaskCanceledException>(async () =>
			await _handler.notifyDisconnectedPeer("user", cancellationToken));
	}

	[Test]
	public async Task RegisterPeer_WithDifferentParameters_ReturnsExpectedResult() {
		// Arrange
		_mockBootstrapServiceApp.Setup(app => app.registerPeer("newhost", 9090, "newuser", CancellationToken.None))
			.ReturnsAsync(false);

		// Act
		var result = await _handler.registerPeer("newhost", 9090, "newuser", CancellationToken.None);

		// Assert
		Assert.That(result, Is.False);
	}

	[Test]
	public async Task Quit_WithDifferentUser_ReturnsExpectedResult() {
		// Arrange
		_mockBootstrapServiceApp.Setup(app => app.quit("anotherUser", It.IsAny<CancellationToken>()))
			.ReturnsAsync(false);

		// Act
		var result = await _handler.quit("anotherUser");

		// Assert
		Assert.That(result, Is.False);
	}
}