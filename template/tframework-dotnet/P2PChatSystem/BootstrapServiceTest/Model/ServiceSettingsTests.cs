using NUnit.Framework;
using P2PChatSystem.BootstrapService.Model;

namespace P2PChatSystem.BootstrapService.Tests;

[TestFixture]
public class ServiceSettingsTests
{
	[SetUp]
	public void Setup() {
		// Thiết lập giá trị mặc định trước mỗi test
		ServiceSettings.Name = null;
		ServiceSettings.Host = null;
		ServiceSettings.Port = 0;
	}

	[Test]
	public void Name_WhenSet_ReturnsExpectedValue() {
		// Arrange
		string expectedName = "TestService";

		// Act
		ServiceSettings.Name = expectedName;

		// Assert
		Assert.That(ServiceSettings.Name, Is.EqualTo(expectedName));
	}

	[Test]
	public void Host_WhenSet_ReturnsExpectedValue() {
		// Arrange
		string expectedHost = "localhost";

		// Act
		ServiceSettings.Host = expectedHost;

		// Assert
		Assert.That(ServiceSettings.Host, Is.EqualTo(expectedHost));
	}

	[Test]
	public void Port_WhenSet_ReturnsExpectedValue() {
		// Arrange
		int expectedPort = 8080;

		// Act
		ServiceSettings.Port = expectedPort;

		// Assert
		Assert.That(ServiceSettings.Port, Is.EqualTo(expectedPort));
	}

	[Test]
	public void MultipleProperties_WhenSet_ReturnExpectedValues() {
		// Arrange
		string expectedName = "TestService";
		string expectedHost = "localhost";
		int expectedPort = 8080;

		// Act
		ServiceSettings.Name = expectedName;
		ServiceSettings.Host = expectedHost;
		ServiceSettings.Port = expectedPort;

		// Assert
		Assert.That(ServiceSettings.Name, Is.EqualTo(expectedName));
		Assert.That(ServiceSettings.Host, Is.EqualTo(expectedHost));
		Assert.That(ServiceSettings.Port, Is.EqualTo(expectedPort));
	}

	[Test]
	public void Name_WhenSetToNull_ReturnsNull() {
		// Arrange
		string expectedName = null;

		// Act
		ServiceSettings.Name = expectedName;

		// Assert
		Assert.That(ServiceSettings.Name, Is.Null);
	}

	[Test]
	public void Host_WhenSetToEmptyString_ReturnsEmptyString() {
		// Arrange
		string expectedHost = "";

		// Act
		ServiceSettings.Host = expectedHost;

		// Assert
		Assert.That(ServiceSettings.Host, Is.EqualTo(expectedHost));
	}

	[Test]
	public void Port_WhenSetToNegativeValue_ReturnsNegativeValue() {
		// Arrange
		int expectedPort = -1;

		// Act
		ServiceSettings.Port = expectedPort;

		// Assert
		Assert.That(ServiceSettings.Port, Is.EqualTo(expectedPort));
	}

	[Test]
	public void Port_WhenSetToMaximumIntValue_ReturnsMaximumIntValue() {
		// Arrange
		int expectedPort = int.MaxValue;

		// Act
		ServiceSettings.Port = expectedPort;

		// Assert
		Assert.That(ServiceSettings.Port, Is.EqualTo(expectedPort));
	}

	[Test]
	public void Name_WhenChanged_ReturnsNewValue() {
		// Arrange
		string initialName = "InitialName";
		string expectedName = "NewName";

		// Act
		ServiceSettings.Name = initialName;
		ServiceSettings.Name = expectedName;

		// Assert
		Assert.That(ServiceSettings.Name, Is.EqualTo(expectedName));
	}

	[Test]
	public void Host_WhenChanged_ReturnsNewValue() {
		// Arrange
		string initialHost = "initialhost";
		string expectedHost = "newhost";

		// Act
		ServiceSettings.Host = initialHost;
		ServiceSettings.Host = expectedHost;

		// Assert
		Assert.That(ServiceSettings.Host, Is.EqualTo(expectedHost));
	}

	[TearDown]
	public void TearDown() {
		// Đặt lại các giá trị về mặc định sau mỗi test
		ServiceSettings.Name = null;
		ServiceSettings.Host = null;
		ServiceSettings.Port = 0;
	}
}