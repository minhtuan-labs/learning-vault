#include <bits/stdc++.h>

using namespace std;

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

void input(string& a, string& b) {
	getline(cin, a);
	getline(cin, b);
}

int max(const int& a, const int& b) {
	return (a > b) ? a : b;
}

int maxSubStr(const string& a, const string& b) {
	int lena = a.length(), lenb = b.length(), d[2][lenb];

	for (int j = 0; j < lenb; j++)
		if (a[0] == b[j]) d[0][j] = 1;
		else d[0][j] = 0;

	for (int i = 1; i < lena; i++) {
		if (a[i] == b[0]) d[1][0] = 1;
		else d[1][0] = d[0][0];

		for (int j = 1; j < lenb; j++)
			if (a[i] == b[j]) d[1][j] = d[0][j - 1] + 1;
			else d[1][j] = max(d[0][j], d[1][j - 1]);

		for (int j = 0; j < lenb; j++) d[0][j] = d[1][j];
	}

	return d[0][lenb - 1];
}

int main(void) {
	initialize();

	string a, b;
	input(a, b);

	cout << maxSubStr(a, b);
	return 0;
}


