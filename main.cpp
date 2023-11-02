/* #include <bits/stdc++.h> */
#include <iostream>
#include <vector>
#include <set>

using namespace std;
#define double long long int

struct xy{
	double x;
	double y;
};
pair<double, double> cross(xy p1, xy p2, xy p3, xy p4){
	double s1 = (p4.x - p2.x) * (p1.y - p2.y) - (p4.y - p2.y) * (p1.x - p2.x);
	double s2 = (p4.x - p2.x) * (p2.y - p3.y) - (p4.y - p2.y) * (p2.x - p3.x);
	/* s1 /= 2; */
	/* s2 /= 2; */
	if (s1 + s2 == 0){
		return make_pair(1e18, 1e18);
	}
	return make_pair((s1 + s2) * p1.x + (p3.x - p1.x) * s1, (s1 + s2) * p1.y + (p3.y - p1.y) * s1);
}
int main(){
	int N;
	cin >> N;
	vector<double> a(N), b(N), c(N), d(N);
	int ans = 1;
	set<double> X;
	set<pair<double, double>> P;
	set<int> NG;
	for (int i = 0; i < N; i++){
		cin >> a[i] >> b[i] >> c[i] >> d[i];
		if (a[i] == c[i]){
			if (X.count(a[i]) == 0){
				X.insert(a[i]);
			} else {
				NG.insert(i);
				continue;
			}
		} else {
			double A = (b[i] - d[i]);
			double B = (a[i] - c[i]) * b[i] - A * a[i];

			/* double s1 = (p4.x - p2.x) * (p1.y - p2.y) - (p4.y - p2.y) * (p1.x - p2.x); */
			/* double s2 = (p4.x - p2.x) * (p2.y - p3.y) - (p4.y - p2.y) * (p2.x - p3.x); */

			// y = Ax + B
			if (P.count(make_pair(A, B)) == 0){
				P.insert(make_pair(A, B));
			} else {
				NG.insert(i);
				continue;
			}
		}
		set<pair<double, double>> st;
		for (int j = 0; j < i; j++){
			auto R = cross(xy{a[i], b[i]}, xy{a[j], b[j]}, xy{c[i], d[i]}, xy{c[j], d[j]});
			if (R.first != 1e18){
				if (NG.count(j) == 0){
					st.insert(R);
				}
			}
		}
		ans += st.size() + 1;
	}
	cout << ans << endl;
}
