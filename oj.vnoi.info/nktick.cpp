#include <bits/stdc++.h>

using namespace std;

const int MAX_N = 60000;
const int MAX_T = 30000;

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

void input(int& n, int** t, int** r) {
	cin >> n;
	*t = new int[n + 1];
	*r = new int[n + 1];
	for (int i = 1; i <= n; i++) cin >> (*t)[i];
	for (int i = 1; i <= n - 1; i++) cin >> (*r)[i];
}

int min(const int& a, const int& b) {
	return (a < b) ? a : b;
}

int minServing(const int& n, const int* t, const int* r) {
	int* d = new int[n + 1];
	d[0] = 0;
	d[1] = t[1];
	for (int i = 2; i <= n; i++)
		d[i] = min(d[i - 1] + t[i], d[i - 2] + r[i - 1]);
	return d[n];
}

int main(void) {
	initialize();

	int n, *t, *r;
	input(n, &t, &r);

	cout << minServing(n, t, r);
	return 0;
}


