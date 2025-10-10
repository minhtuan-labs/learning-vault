#include <bits/stdc++.h>

using namespace std;

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

void input(int& s1, int& s2, int& s3) {
	cin >> s1 >> s2 >> s3;
}

int main(void) {
	initialize();

	int s1, s2, s3;
	input(s1, s2, s3);

	int count[s1 + s2 + s3 + 1] = {0}, maxs = 0, counts = 0;
	for (int i = 1; i <= s1; i++)
		for (int j = 1; j <= s2; j++)
			for (int k = 1; k < s3; k++) {
				count[i + j + k]++;
				if (maxs < count[i + j + k]) {
					maxs = count[i + j + k];
					counts = i + j + k;
				}
				else if ((maxs == count[i + j + k]) && (counts > i + j + k)) counts = i + j + k;
			}

	cout << counts;
	return 0;
}


