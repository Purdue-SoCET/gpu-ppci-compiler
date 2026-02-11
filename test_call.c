int test_call(int a, int b){
    return a + b;
}

int main(){
    int a = 1;
    int b = 2;
    int c = test_call(a, b);
    if(a < b){
        test_call(b+b,a);
    }
    else{
        test_call(a+a,b);
    }
    return 0;
}
