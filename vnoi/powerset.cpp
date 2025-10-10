#include <iostream>

using namespace std;

void input(int& n) {
	cout << "Nhap n = ";
	cin >> n;
}

void travel(int i, int* a, int n) {
	if (i >= n) {
		// In ra tap con tuong ung voi mang a[i]
		cout << "{";
		int count = 0;
		for (int i = 0; i < n; i++) {
			if (a[i] == 1) {
				count++;
				if (count >= 2) cout << ", " << i + 1;
				else cout << i + 1;
			}
		}
		cout << "}" << endl;
		return;
	}

	a[i] = 0; // khong lua chon i vao subset
	travel(i + 1, a, n);

	a[i] = 1; // lua chon i vao subset
	travel(i + 1, a, n);
}

void process(int n) {
	int a[n];
	for (int i = 0; i < n; i++) a[i] = 0;

	travel(0, a, n);
}

int main(void) {
	int n;
	input(n);

	process(n);
	//output();
}


