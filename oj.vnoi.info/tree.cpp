#include <iostream>

using namespace std;

const int MAX_N = 100;

void input(int& n, int* p, int* r) {
	cout << "Nhap n = ";
	cin >> n;
	for (int i = 0; i < n; i++) cin >> p[i] >> r[i];
}

void travel(int i, int* a, int n, int* p, int* r) {
	if (i >= n) {
		// Subset tuong ung voi cac cay duoc chon
		//  - a[i] == 1 cay thu i duoc giu lai
		//  - a[i] == 0 cay thu i bi chat
		return;
	}

	a[i] = 0; // khong lua chon i vao subset
	travel(i + 1, a, n);

	a[i] = 1; // lua chon i vao subset
	travel(i + 1, a, n);
}

void process(int n, int* p, int* r) {
	int a[n];
	for (int i = 0; i < n; i++) a[i] = 0;

	travel(0, a, n, p, r);
}

int main(void) {
	int n, p[MAX_N], r[MAX_N];
	input(n, p, r);

	process(n);
	//output();
}


