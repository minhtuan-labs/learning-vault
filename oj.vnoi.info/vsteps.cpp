#include <bits/stdc++.h>

using namespace std;

const int MAX_N = 10000;
const int MODULO = 14062008;

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

void input(int& n, int& k, vector<int>& v) {
	cin >> n >> k;
	int a;
	for (int i = 0; i < k; i++) {
		cin >> a;
		v.push_back(a);
	}
}

int search(const int i, vector<int> v, int d[MAX_N]) {
	vector<int>::iterator p = lower_bound(v.begin(), v.end(), i);
	if ((p == v.end()) || (*p != i)) return 0;
	else return d[i];
}

int main(void) {
	initialize();

	int n, k, d[MAX_N];
	vector<int> v;
	input(n, k, v);

	d[0] = 1;
	for (int i = 1; i < n; i++)
		if (search(i, v, d) == 0) d[i] = 0;
		else {
			if (i == 1) d[1] = search(i, v, d);
			else d[i] = (search(i - 1, v, d) + search(i - 2, v, d)) % MODULO;
		}
	cout << d[n - 1];
	return 0;
}


