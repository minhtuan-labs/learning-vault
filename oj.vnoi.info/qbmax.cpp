#include <bits/stdc++.h>

using namespace std;

const int MAX_N = 100;
const int INFINITE = INT_MIN / 2;

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

void input(int& m, int& n, int a[MAX_N][MAX_N]) {
	cin >> m >> n;
	for (int i = 0; i < m; i++)
		for (int j = 0; j < n; j++)
			cin >> a[i][j];
}

int max(const int& a, const int& b) {
	return (a > b) ? a : b;
}

int maxValue(const int& m, const int& n, const int a[MAX_N][MAX_N]) {
	int d[MAX_N + 2][MAX_N + 2];

	for (int i = 0; i <= m + 1; i++) {
		d[i][0]	= INFINITE;
		d[i][n + 1] = INFINITE;
	}

	for (int i = 0; i <= n + 1; i++) {
		d[0][i]	= INFINITE;
		d[m + 1][i] = INFINITE;
	}

	for (int i = 1; i <= m; i++) d[i][1] = a[i - 1][0];

	for (int j = 2; j <= n; j++)
		for (int i = 1; i <= m; i++)
			d[i][j] = max(max(d[i - 1][j - 1], d[i][j - 1]), d[i + 1][j - 1]) + a[i - 1][j - 1];

	int result = INFINITE;
	for (int i = 1; i <= m; i++)
		if (result < d[i][n]) result = d[i][n];
	return result;
}

int main(void) {
	initialize();

	int m, n, a[MAX_N][MAX_N];
	input(m, n, a);

	cout << maxValue(m, n, a);
	return 0;
}


