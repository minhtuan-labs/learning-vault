#include <bits/stdc++.h>

using namespace std;

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

vector<int> getLPS(const string& pattern) {
	int len = pattern.length(), i = 1, j = 0;
	vector<int> lps(len, 0);

	while (i < len) {
		// tính lps[i]
		if (pattern[i] == pattern[j]) {
			j++;
			lps[i] = j;
			i++;
		}
		else if (j != 0) j = lps[j - 1];
		else {
			lps[i] = 0;
			i++;
		}
	}

	return lps;
}

vector<int> kmp(const string& text, const string& pattern) {
	int lentext = text.length(), lenpattern = pattern.length();
	vector<int> lps = getLPS(pattern), result;
	int i = 0, j = 0;

	while (i < lentext) {
		if (text[i] == pattern[j]) {
			i++;
			j++;
		}
		if (j == lenpattern) {
			result.push_back(i - j + 1);
			j = lps[j - 1];
		}
		else if ((i < lentext) && (text[i] != pattern[j])) {
			if (j != 0) j = lps[j - 1];
			else i++;
		}
	}
	return result;
}

void input(string& a, string& b) {
	cin >> a >> b;
}

int main(void) {
	initialize();

	string a, b;
	input(a, b);

	vector<int> positions = kmp(a, b);
	for (vector<int>::iterator ppos = positions.begin(); ppos != positions.end(); ppos++) cout << *ppos << " ";

	return 0;
}


