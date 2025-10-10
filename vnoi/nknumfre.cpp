#include <bits/stdc++.h>

using namespace std;

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

void input(int& a, int& b) {
	cin >> a >> b;
}

int reverse(int k) {
	int result = 0;
	while (k > 0) {
		result = result * 10 + k % 10;
		k /= 10;
	}
	return result;
}

int nice(int k) {
	int h = reverse(k);
	return (__gcd(h, k) == 1) ? 1 : 0;
}

int main(void) {
	initialize();

	int a, b;
	input(a, b);

	int count = 0;
	for (int i = a; i <= b; i++) count += nice(i);

	cout << count;
	return 0;
}

