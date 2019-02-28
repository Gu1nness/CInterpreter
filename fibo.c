int main() {
    int i = 1, n = 127, t1=0, t2=1, nextTerm;

    while(i<=n) {
        nextTerm = t1 + t2;
        t1 = t2;
        t2 = nextTerm;
        i++;
    }
    return t1;
}
