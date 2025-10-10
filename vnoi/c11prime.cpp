#include <bits/stdc++.h>

using namespace std;

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

int getExponent(long long int n, long long int p) {
	int exp = 0;
	while (n % p == 0) {
		n /= p;
		exp++;
	}

	return (n == (long long int)1) ? exp : 0;
}

int main(void) {
	initialize();

	long long int n;
	cin >> n;

	if (n <= 3) {
		cout << 0;
		return 0;
	}

	long long int p, sqrtn = (long long int)sqrt((long long int)n);
	int q;
	for (p = 2; (p <= sqrtn) && (n % p != 0); p++);
	if (n % p == 0) {
		q = getExponent(n, p);
		if (q > 1) cout << p << " " << q;
		else cout << 0;
	}
	else cout << 0;

	return 0;
}

