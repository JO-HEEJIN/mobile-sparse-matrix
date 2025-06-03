"""
단일 함수 테스트: test_small_matrix_multiplication()
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sparse_matrix import MobileSparseMatrix
from src.matrix_operations import multiply


def test_small_matrix_multiplication():
    """작은 행렬 곱셈 정확성 테스트"""
    print("작은 행렬 곱셈 테스트")
    
    # A = [[1, 0, 2],
    #      [0, 3, 0]]
    print("행렬 A 생성:")
    print("[[1, 0, 2],")
    print(" [0, 3, 0]]")
    
    A = MobileSparseMatrix(2, 3)
    A.set(0, 0, 1.0)
    A.set(0, 2, 2.0)
    A.set(1, 1, 3.0)
    
    print(f"A 통계: nnz={A.nnz()}, 밀도={A.density()*100:.2f}%")
    
    # B = [[1, 4],
    #      [2, 5], 
    #      [3, 6]]
    print("\n행렬 B 생성:")
    print("[[1, 4],")
    print(" [2, 5],")
    print(" [3, 6]]")
    
    B = MobileSparseMatrix(3, 2)
    B.set(0, 0, 1.0)
    B.set(0, 1, 4.0)
    B.set(1, 0, 2.0)
    B.set(1, 1, 5.0)
    B.set(2, 0, 3.0)
    B.set(2, 1, 6.0)
    
    print(f"B 통계: nnz={B.nnz()}, 밀도={B.density()*100:.2f}%")
    
    # 수동 계산 설명
    print("\n수동 계산:")
    print("C[0,0] = A[0,0]*B[0,0] + A[0,1]*B[1,0] + A[0,2]*B[2,0]")
    print("       = 1*1 + 0*2 + 2*3 = 1 + 0 + 6 = 7")
    print("C[0,1] = A[0,0]*B[0,1] + A[0,1]*B[1,1] + A[0,2]*B[2,1]")
    print("       = 1*4 + 0*5 + 2*6 = 4 + 0 + 12 = 16")
    print("C[1,0] = A[1,0]*B[0,0] + A[1,1]*B[1,0] + A[1,2]*B[2,0]")
    print("       = 0*1 + 3*2 + 0*3 = 0 + 6 + 0 = 6")
    print("C[1,1] = A[1,0]*B[0,1] + A[1,1]*B[1,1] + A[1,2]*B[2,1]")
    print("       = 0*4 + 3*5 + 0*6 = 0 + 15 + 0 = 15")
    
    print("\n예상 결과: [[7, 16], [6, 15]]")
    
    # C = A × B 계산
    print("\n희소행렬 곱셈 실행...")
    C = multiply(A, B)
    
    print(f"\n실제 결과:")
    print(f"C[0,0] = {C.get(0, 0)}")
    print(f"C[0,1] = {C.get(0, 1)}")
    print(f"C[1,0] = {C.get(1, 0)}")
    print(f"C[1,1] = {C.get(1, 1)}")
    
    print(f"\nC 통계: nnz={C.nnz()}, 밀도={C.density()*100:.2f}%")
    
    # 결과 검증
    print("\n결과 검증:")
    
    def check_value(expected, actual, position):
        diff = abs(actual - expected)
        if diff < 1e-10:
            print(f"PASS C{position} = {actual:.1f} (예상: {expected:.1f}) - 통과")
            return True
        else:
            print(f"FAIL C{position} = {actual:.1f} (예상: {expected:.1f}) - 실패 (차이: {diff})")
            return False
    
    success = True
    success &= check_value(7.0, C.get(0, 0), "[0,0]")
    success &= check_value(16.0, C.get(0, 1), "[0,1]")
    success &= check_value(6.0, C.get(1, 0), "[1,0]")
    success &= check_value(15.0, C.get(1, 1), "[1,1]")
    
    return success


if __name__ == "__main__":
    print("단일 함수 테스트 실행")
    print("=" * 50)
    
    try:
        success = test_small_matrix_multiplication()
        
        if success:
            print("\n 통과" )

        else:
            print("\n일부 검증 실패")
            
    except Exception as e:
        print(f"\n테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()