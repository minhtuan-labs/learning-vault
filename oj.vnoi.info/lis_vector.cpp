#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int longestIncreasingSubsequence(vector<int>& arr) {
    vector<int> lis;

    for (int x : arr) {
        auto pos = lower_bound(lis.begin(), lis.end(), x);
        if (pos == lis.end()) {
            lis.push_back(x);  // Them phan tu vào cuoi neu nó lon nhat
        } else {
            *pos = x;  // Thay the phan tu tai vi trí tìm thay
        }
    }

    return lis.size();  // Kích thuoc cua lis là do dài cua LIS
}

int main() {
    int N;
    cin >> N;
    vector<int> arr(N);

    for (int i = 0; i < N; i++) {
        cin >> arr[i];
    }

    int result = longestIncreasingSubsequence(arr);
    cout << result << endl;

    return 0;
}

