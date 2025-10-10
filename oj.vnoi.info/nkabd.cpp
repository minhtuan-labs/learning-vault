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

int rich(int k) {
	if (k == 1) return 0;
	int sum = 1, j;
	for (int i = 2; i <= sqrt(k); i++)
		if (k % i == 0) {
			j = k / i;
			sum += i;
			if (i != j) sum += j;
			if (sum > k) return 1;
		}
	return 0;
}

int main(void) {
	initialize();

	int a, b;
	input(a, b);

	int count = 0;
	for (int i = a; i <= b; i++) count += rich(i);

	cout << count;
	return 0;
}


