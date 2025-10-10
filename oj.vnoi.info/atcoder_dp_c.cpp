#include <bits/stdc++.h>

using namespace std;

const int MAX_N = 100000;
const int MAX_K = 3;

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

void input(int& n, int happiness[MAX_N][MAX_K]) {
	cin >> n;
	for (int i = 0; i < n; i++)
		for (int k = 0; k < MAX_K; k++) cin >> happiness[i][k];
}

int maxHappiness(int n, int happiness[MAX_N][MAX_K]) {
	int d[2][MAX_K] = {0};

	for (int k = 0; k < MAX_K; k++) d[0][k] = happiness[0][k];

	int considering;
	for (int i = 1; i < n; i++) {
		for (int k1 = 0; k1 < MAX_K; k1++) {
			d[1][k1] = 0;
			for (int k2 = 0; k2 < MAX_K; k2++)
				if (k1 != k2) {
					considering = d[0][k2] + happiness[i][k1];
					if (d[1][k1] < considering) d[1][k1] = considering;
				}
		}

		for (int k1 = 0; k1 < MAX_K; k1++) d[0][k1] = d[1][k1];
	}

	int result = 0;
	for (int k = 0; k < MAX_K; k++)
		if (result < d[0][k]) result = d[0][k];
	return result;
}

int main(void) {
	initialize();

	int n, happiness[MAX_N][MAX_K];
	input(n, happiness);

	cout << maxHappiness(n, happiness);
	return 0;
}

