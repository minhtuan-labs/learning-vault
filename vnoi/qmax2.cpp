#include <bits/stdc++.h>

using namespace std;

const int MAX_N = 50000;
const int MAX_M = 100000;

int max(const int& a, const int& b) {
	return (a > b) ? a : b;
}

class SegmentTree {
public:
	SegmentTree(const int& n) : _tree(4 * n, 0), _n(n) {
		init(0, 0, _n - 1, 0);
	}

	void update(const int& x, const int& y, const int& k) {
		for (int idx = x; idx <= y; idx++) update(0, 0, _n - 1, idx, k);
		//for (int i = 0; i < _tree.size(); i++) cout << _tree[i] << " ";
		//cout << endl;
	}

	int query(const int& x, const int& y) {
		return query(0, 0, _n - 1, x, y);
	}

private:
	vector<int> _tree;
	int _n;

	void init(const int& node, const int& start, const int& end, const int& value) {
		if (start == end) _tree[node] = value;
		else {
			int middle = (start + end) / 2;
			init(node * 2 + 1, start, middle, value);
			init(node * 2 + 2, middle + 1, end, value);
			_tree[node] = value;
		}
	}

	void update(const int& node, const int& start, const int& end, const int& idx, const int& k) {
		if (start == end) _tree[node] += k;
		else {
			int middle = (start + end) / 2;
			if (idx <= middle) update (node * 2 + 1, start, middle, idx, k);
			else update(node * 2 + 2, middle + 1, end, idx, k);
			_tree[node] = max(_tree[node * 2 + 1], _tree[node * 2 + 2]);
		}
	}

	int query(const int& node, const int& start, const int& end, const int& l, const int& r) {
		if ((start > r) || (end < l)) return INT_MIN;
		if ((start <= r) && (l <= end)) return _tree[node];
		int middle = (start + end) / 2;
		return max(query(2 * node + 1, start, middle, l, r), query(2 * node + 2, middle + 1, end, l, r));
	}
};

void initialize(void) {
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
}

int main(void) {
	initialize();

	int n, m, type, x, y, k;
	cin >> n >> m;

	SegmentTree segtree(n);

	for (int i = 0; i < m; i++) {
		cin >> type >> x >> y;
		if (type == 0) {
			cin >> k;
			segtree.update(x - 1, y - 1, k);
		}
		else if (type == 1) cout << segtree.query(x - 1, y - 1) << endl;
	}
	return 0;
}


