"""
Correctness Tests for Mobile Sparse Matrix
정확성 검증 테스트 모음
"""

"""
계산이 수학적으로 맞는지를 확인해야 할 듯

값 저장/불러오기: 넣은 값이 그대로 나오는가?
빈 칸 처리: 값을 안 넣은 곳은 0.0이 나오는가?
통계 계산: nnz(), density() 계산이 맞는가?
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sparse_matrix import MobileSparseMatrix
from src.matrix_operations import multiply, multiply_optimized, element_wise_add


def test_basic_operations():
    """기본 연산 테스트"""
    print(" 기본 연산 테스트 시작")
    
    # 3×3 행렬 생성
    matrix = MobileSparseMatrix(3, 3)
    
    # 값 설정
    matrix.set(0, 0, 1.5)
    matrix.set(1, 2, 2.7)
    matrix.set(2, 1, -3.2)
    
    # 값 확인
    assert matrix.get(0, 0) == 1.5, "값 설정/조회 오류"
    assert matrix.get(1, 2) == 2.7, "값 설정/조회 오류"
    assert matrix.get(2, 1) == -3.2, "값 설정/조회 오류"
    assert matrix.get(0, 1) == 0.0, "기본값 오류"
    
    # 통계 확인
    assert matrix.nnz() == 3, "nnz 계산 오류"
    assert abs(matrix.density() - 3/9) < 1e-10, "밀도 계산 오류"
    
    print("  기본 연산 테스트 통과")


def test_small_matrix_multiplication():
    """작은 행렬 곱셈 정확성 테스트"""
    print(" 작은 행렬 곱셈 테스트")
    
    # A = [[1, 0, 2],
    #      [0, 3, 0]]
    A = MobileSparseMatrix(2, 3)
    A.set(0, 0, 1.0)
    A.set(0, 2, 2.0)
    A.set(1, 1, 3.0)
    
    # B = [[1, 4],
    #      [2, 5], 
    #      [3, 6]]
    B = MobileSparseMatrix(3, 2)
    B.set(0, 0, 1.0)
    B.set(0, 1, 4.0)
    B.set(1, 0, 2.0)
    B.set(1, 1, 5.0)
    B.set(2, 0, 3.0)
    B.set(2, 1, 6.0)
    
    # C = A × B 계산
    C = multiply(A, B)
    
    """
    C[0,0] = A[0,0]*B[0,0] + A[0,1]*B[1,0] + A[0,2]*B[2,0]
       = 1*1 + 0*2 + 2*3 = 1 + 0 + 6 = 7 

    C[0,1] = A[0,0]*B[0,1] + A[0,1]*B[1,1] + A[0,2]*B[2,1]  
       = 1*4 + 0*5 + 2*6 = 4 + 0 + 12 = 16 
    """

    # 예상 결과: [[7, 16], [6, 15]]
    expected = [
        [(0, 0, 7.0), (0, 1, 16.0)],
        [(1, 0, 6.0), (1, 1, 15.0)]
    ]
    
    # 결과 검증
    assert abs(C.get(0, 0) - 7.0) < 1e-10, f"C[0,0] = {C.get(0, 0)}, 예상: 7.0"
    assert abs(C.get(0, 1) - 16.0) < 1e-10, f"C[0,1] = {C.get(0, 1)}, 예상: 16.0"
    assert abs(C.get(1, 0) - 6.0) < 1e-10, f"C[1,0] = {C.get(1, 0)}, 예상: 6.0"
    assert abs(C.get(1, 1) - 15.0) < 1e-10, f"C[1,1] = {C.get(1, 1)}, 예상: 15.0"
    
    print(" 작은 행렬 곱셈 테스트 통과")


def test_optimized_vs_normal():
    """최적화 버전과 일반 버전 결과 비교"""
    print("  최적화 알고리즘 일치성 테스트")
    
    # 무작위 희소행렬 생성
    A = MobileSparseMatrix(50, 40)
    B = MobileSparseMatrix(40, 30)
    
    # A에 값 설정 (밀도 ~5%)
    test_values_A = [
        (0, 5, 1.2), (3, 7, -2.1), (5, 15, 3.4),
        (10, 20, -1.7), (15, 35, 2.8), (20, 10, 4.1),
        (25, 25, -3.3), (30, 5, 1.9), (35, 30, -2.6),
        (40, 15, 3.7), (45, 38, 1.4)
    ]
    
    for row, col, val in test_values_A:
        A.set(row, col, val)
    
    # B에 값 설정
    test_values_B = [
        (5, 10, 2.1), (7, 15, -1.3), (15, 20, 1.8),
        (20, 5, -2.4), (25, 25, 3.1), (30, 12, 1.6),
        (35, 8, -1.9), (38, 28, 2.7)
    ]
    
    for row, col, val in test_values_B:
        B.set(row, col, val)
    
    # 두 방법으로 곱셈 계산
    C1 = multiply(A, B, optimize_for_battery=False)
    C2 = multiply_optimized(A, B)
    
    # 결과 비교
    assert C1.rows == C2.rows and C1.cols == C2.cols, "결과 행렬 크기 불일치"
    
    # 모든 원소 비교
    for i in range(C1.rows):
        for j in range(C1.cols):
            val1 = C1.get(i, j)
            val2 = C2.get(i, j)
            if abs(val1 - val2) > 1e-10:
                raise AssertionError(f"결과 불일치 at ({i},{j}): {val1} vs {val2}")
    
    print("  최적화 알고리즘 일치성 테스트 통과")

# 좀 까다로울 때도 제대로 될까?
def test_edge_cases():
    """경계 조건 테스트"""
    print(" 경계 조건 테스트")
    
    # 빈 행렬 곱셈
    A = MobileSparseMatrix(3, 3)  # 모든 원소가 0
    B = MobileSparseMatrix(3, 3)
    B.set(1, 1, 5.0)  # 한 원소만 설정
    
    C = multiply(A, B)
    assert C.nnz() == 0, "빈 행렬 곱셈 결과 오류"
    
    # 단위 행렬 곱셈
    I = MobileSparseMatrix(3, 3)
    I.set(0, 0, 1.0)
    I.set(1, 1, 1.0)
    I.set(2, 2, 1.0)
    
    X = MobileSparseMatrix(3, 3)
    X.set(0, 1, 2.0)
    X.set(1, 2, 3.0)
    X.set(2, 0, 4.0)
    
    result = multiply(I, X)
    
    # I × X = X 이어야 함
    assert abs(result.get(0, 1) - 2.0) < 1e-10, "단위행렬 곱셈 오류"
    assert abs(result.get(1, 2) - 3.0) < 1e-10, "단위행렬 곱셈 오류"
    assert abs(result.get(2, 0) - 4.0) < 1e-10, "단위행렬 곱셈 오류"
    
    print("  경계 조건 테스트 통과")


def run_all_correctness_tests():
    """모든 정확성 테스트 실행"""
    print(" 희소행렬 정확성 테스트 시작")
    print("=" * 50)
    
    try:
        test_basic_operations()
        test_small_matrix_multiplication()
        test_optimized_vs_normal()
        test_edge_cases()
        
        print("\n  통과 ")
        return True
        
    except Exception as e:
        print(f"\n  테스트 실패: {e}")
        return False


if __name__ == "__main__":
    success = run_all_correctness_tests()
    sys.exit(0 if success else 1)