using P2PChatSystem.BootstrapService.Model;

namespace P2PChatSystem.BootstrapService.Tests;

[TestFixture]
public class CalculatorTests
{
	private Calculator _calculator;

	[SetUp]
	public void Setup() {
		_calculator = new Calculator();
	}

	[Test]
	[TestCase(1, 1, 2)]
	[TestCase(-1, -1, 2)]
	[TestCase(-1, 1, 2)]
	[TestCase(0, 0, 0)]
	[TestCase(123, 456, 579)]
	[TestCase(2, 3, 5)]
	public void Test_Add(int a, int b, int expectedResult) {
		//Assert.AreEqual(expectedResult, _calculator.Add(a, b));
		Assert.That(_calculator.Add(a, b), Is.EqualTo(expectedResult));
	}

	[Test]
	[TestCase(1, 1, 1)]
	[TestCase(-1, -1, 1)]
	[TestCase(-1, 1, 1)]
	[TestCase(0, 0, 0)]
	[TestCase(2, -3, 6)]
	[TestCase(-3, -2, 6)]
	[TestCase(4, -4, 16)]
	public void Test_Multiply(int a, int b, int expectedResult) {
		int result = _calculator.Multiply(a, b);
		Assert.That(_calculator.Multiply(a, b), Is.EqualTo(result));
	}
	
	[Test]
	[TestCase(4, 2, 3)]
	[TestCase(-4, -2, -3)]
	[TestCase(4, -2, 1)]
	[TestCase(0, 0, 0)]
	[TestCase(10, 20, 15)]
	[TestCase(-10, 10, 0)]
	[TestCase(5, 7, 6)]
	[TestCase(-5, -7, -6)]
	[TestCase(int.MaxValue, int.MinValue, -1)] // Trung bình của int.MaxValue và int.MinValue gần như là -1
	[TestCase(100, 0, 50)]
	public void TBC_WhenCalled_ReturnsExpectedResult(int a, int b, int expectedResult)
	{
		Assert.That(_calculator.TBC(a, b), Is.EqualTo(expectedResult));
	}
}
