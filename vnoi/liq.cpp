#include <bits/stdc++.h>

using namespace std;

const int MAX_N = 1000;

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

void input(int& n, int* a) {
	cin >> n;
	for (int i = 0; i < n; i++) cin >> a[i];
}

int maxIncreasingSeq(int n, int* a) {
	int d[n] = {1}, mis = 1;
	for (int i = 1; i < n; i++) {
		for (int j = 0; j < i; j++)
			if ((a[j] < a[i]) && (d[i] < d[j] + 1)) d[i] = d[j] + 1;
		if (mis < d[i]) mis = d[i];
	}
	return mis;
}

int main(void) {
	initialize();

	int n, a[MAX_N];
	input(n, a);

	cout << maxIncreasingSeq(n, a);
	return 0;
}

