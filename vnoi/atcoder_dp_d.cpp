#include <bits/stdc++.h>

using namespace std;

const int MAX_N = 100;
const int MAX_W = 100000;

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

void input(int& n, int& w, int weight[MAX_N], int value[MAX_N]) {
	cin >> n >> w;
	for (int i = 0; i < n; i++) cin >> weight[i] >> value[i];
}

long long int maxValue(int n, int w, int weight[MAX_N], int value[MAX_N]) {
	long long int d[2][MAX_W + 1] = {0};

	for (int i = 0; i <= w; i++)
		if (weight[0] <= i) d[0][i] = value[0];

	long long int considering;
	for (int i = 1; i < n; i++) {
		for (int j = 0; j <= w; j++)
			if (j >= weight[i]) {
				considering = d[0][j - weight[i]] + (long long int)value[i];
				if (d[1][j] < considering) d[1][j] = considering;
			}
			else d[1][j] = d[0][j];
		for (int j = 0; j <= w; j++) d[0][j] = d[1][j];
	}

	return d[0][w];
}

int main(void) {
	initialize();

	int n, w, weight[MAX_N], value[MAX_N];
	input(n, w, weight, value);

	cout << maxValue(n, w, weight, value);
	return 0;
}


