#include <bits/stdc++.h>

using namespace std;

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

void input(int& n, int& k, int** h) {
	cin >> n >> k;
	*h = new int[n];
	for (int i = 0; i < n; i++) cin >> (*h)[i];
}

int abs(int a) {
	return (a > 0) ? a : -a;
}

int cost(int n, int k, int* h) {
	if (n == 1) return 0;

	int d[n] = {0}, mincost, cost;

	for (int i = 1; i < n; i++) {
		mincost = INT_MAX;
		for (int j = 1; j <= k; j++) 
			if (i >= j) {
				cost = d[i - j] + abs(h[i] - h[i - j]);
				if (mincost > cost) mincost = cost;
			}
		d[i] = mincost;
	}

	return d[n - 1];
}

int main(void) {
	initialize();

	int n, k, *h;
	input(n, k, &h);

	cout << cost(n, k, h);
	return 0;
}


