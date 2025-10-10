#include <bits/stdc++.h>

const int MAX_N = 200000;

using namespace std;

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

int main(void) {
	initialize();

	bool isPrime[MAX_N + 1];
	isPrime[0] = false;
	isPrime[1] = false;
	for (int i = 2; i <= MAX_N; i++) isPrime[i] = true;
	for (int i = 2; i <= MAX_N; i++)
		if (isPrime[i])
			for (int j = 2; j <= MAX_N / i; j++) isPrime[i * j] = false;

	int a, b;
	cin >> a >> b;

	for (int i = a; i <= b; i++)
		if (isPrime[i]) cout << i << endl;

    return 0;
}

