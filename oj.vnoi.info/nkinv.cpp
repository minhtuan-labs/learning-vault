#include <bits/stdc++.h>

using namespace std;

const int MAX_N = 60000;

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

void input(int& n, int a[MAX_N]) {
	cin >> n;
	for (int i = 0; i < n; i++) cin >> a[i];
}

int nkinv(const int& n, const int a[MAX_N]) {
	int result = 0;
	vector<int> incSeq;
	vector<int>::iterator pos;
	for (int i = 0; i < n; i++) {
		pos = upper_bound(incSeq.begin(), incSeq.end(), a[i]);
		if (pos == incSeq.end()) incSeq.push_back(a[i]);
		else {
			result += incSeq.end() - pos;
			incSeq.insert(pos, a[i]);
		}
	}
	return result;
}

int main(void) {
	initialize();

	int n, a[MAX_N];
	input(n, a);

	cout << nkinv(n, a);
	return 0;
}


