#include <bits/stdc++.h>

using namespace std;

const int MAX_N = 100000;

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

void input(int& n, int a[MAX_N + 1], int& t, int b[MAX_N]) {
	cin >> n;
	a[0] = 0;
	for (int i = 1; i <= n; i++) cin >> a[i];
	cin >> t;
	for (int i = 0; i < t; i++) cin >> b[i];
}

void swap(int& a, int& b) {
	int temp = a;
	a = b;
	b = temp;
}

void quicksort(const int& l, const int& r, int b[MAX_N], int order[MAX_N]) {
	int i = l, j = r, middle = b[order[(l + r) / 2]];
	while (i < j) {
		while (b[order[i]] < middle) i++;
		while (middle < b[order[j]]) j--;
		if (i <= j) {
			swap(order[i], order[j]);
			i++;
			j--;
		}
	}
	if (i < r) quicksort(i, r, b, order);
	if (l < j) quicksort(l, j, b, order);
}

int main(void) {
	initialize();

	int n, a[MAX_N + 1], t, b[MAX_N];
	input(n, a, t, b);

	int d[MAX_N], order[MAX_N], competency[MAX_N];
	for (int i = 0; i < n; i++) d[i] = a[i + 1] - a[i];
	for (int i = 0; i < t; i++) order[i] = i;
	quicksort(0, t - 1, b, order);

	int j = 0;
	for (int i = 0; i < t; i++) {
		while ((j < n) && (b[order[i]] >= d[j])) j++;
		competency[order[i]] = j;
	}

	for (int i = 0; i < t; i++) cout << competency[i] << endl;
	return 0;
}
