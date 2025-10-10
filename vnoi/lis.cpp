#include <bits/stdc++.h>

using namespace std;

const int MAX_N = 30000;

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

void input(int& n, int a[MAX_N]) {
	cin >> n;
	for (int i = 0; i < n; i++) cin >> a[i];
}

int search(int d[MAX_N], int sized, int a) {
	int left = 0, right = sized - 1, middle;
	while (left <= right) {
		middle = (left + right) / 2;
		if (d[middle] < a) left = middle + 1;
		else if (a < d[middle]) right = middle - 1;
		else return middle;
	}
	return left;
}

int maxIncreasingSeq(int n, int a[MAX_N]) {
	int d[MAX_N], sized = 0, pos;
	for (int i = 0; i < n; i++) {
		pos = search(d, sized, a[i]);
		d[pos] = a[i];
		if (pos >= sized) sized++;
	}
	return sized;
}

int main(void) {
	initialize();

	int n, a[MAX_N];
	input(n, a);

	cout << maxIncreasingSeq(n, a);
	return 0;
}

