extern int cos(int, int);

int rs1 = 1;
int rs2 = 2;

int main() {
    int rd = cos(rs1, rs2);
    if(rs1 == 1){
        rs2 = 3;
    }
    return rd;
}
