"""
Mobile-Optimized Sparse Matrix Operations
Android 환경 최적화 희소행렬 연산

핵심 기능:
- 희소행렬 곱셈
- 메모리 효율적 알고리즘
- 배터리 절약 최적화
"""



"""
행렬 곱셈의 수학적 원리는 
C[i][j] = Σ(k=0 to n) A[i][k] × B[k][j]
C의 (i,j) 위치 값은 A의 i번째 행과 B의 j번째 열을 곱해서 모두 더한 것

총 3단계로 나눴음
1. 준비작업
2. 실제 곱셈은 이중루프로
3. 결과 저장

"""

import time
from typing import Dict, Set
from .sparse_matrix import MobileSparseMatrix


def multiply(A: MobileSparseMatrix, B: MobileSparseMatrix, 
            optimize_for_battery: bool = True) -> MobileSparseMatrix:
    """
    두 희소행렬의 곱셈: C = A × B
    
    Args:
        A: 왼쪽 행렬 (m × k)
        B: 오른쪽 행렬 (k × n)  
        optimize_for_battery: 배터리 최적화 모드
        
    Returns:
        결과 행렬 C (m × n)
        
    Raises:
        ValueError: 행렬 크기가 곱셈에 적합하지 않은 경우
    """
    # 크기 검증
    if A.cols != B.rows:
        raise ValueError(f"행렬 곱셈 불가: A({A.rows}×{A.cols}) × B({B.rows}×{B.cols})")
    
    print(f"   희소행렬 곱셈 시작: ({A.rows}×{A.cols}) × ({B.rows}×{B.cols})")
    print(f"   A 밀도: {A.density()*100:.3f}%, B 밀도: {B.density()*100:.3f}%")
    


    # 계산이 느리니 일단 행렬 곱셈이 얼마나 빨리 끝나는지 측정해야 할 듯
    start_time = time.time()
    
    # 결과 행렬 생성
    C = MobileSparseMatrix(A.rows, B.cols, f"Result of {A.platform}")
    
    # 배터리 최적화: 진행률 표시 간격 조정
    progress_interval = 100 if optimize_for_battery else 10
    



    # 각 결과 행 계산
    for i in range(A.rows):
        # 진행률 표시 (배터리 절약을 위해 간헐적으로 해야 할 듯)
        if i % progress_interval == 0 and i > 0:
            progress = (i / A.rows) * 100
            elapsed = time.time() - start_time
            print(f"   진행률: {progress:.1f}% ({elapsed:.2f}초 경과)")
        
        # A의 i번째 행 데이터 가져오기
        A_row_data = A.get_row_data(i)
        if not A_row_data:  # 빈 행이면 스킵
            continue
        
        # 결과 행 계산을 위한 임시 딕셔너리 (메모리 효율적)
        result_row: Dict[int, float] = {}
        
        # A[i][k] × B[k][:] 계산
        for k, A_ik in A_row_data.items():
            # B의 k번째 행 데이터 가져오기
            B_row_data = B.get_row_data(k)
            if not B_row_data:  # 빈 행이면 스킵
                continue
            
            # A[i][k] × B[k][j] 계산
            for j, B_kj in B_row_data.items():
                if j not in result_row:
                    result_row[j] = 0.0
                result_row[j] += A_ik * B_kj
        
        # 결과를 C에 저장 (0에 가까운 값 제외)
        for j, value in result_row.items():
            if abs(value) > 1e-12:  # 수치 오차 제거
                C.set(i, j, value)
        
        # 배터리 최적화: 주기적 메모리 정리
        if optimize_for_battery and i % 500 == 0:
            C.optimize_for_mobile()
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"   곱셈 완료: {execution_time:.3f}초")
    print(f"   결과 밀도: {C.density()*100:.3f}%")
    print(f"   메모리 사용량: {C.memory_usage()/(1024*1024):.2f}MB")
    
    return C





""" 더욱 빠른 곱셈 (성능 최우선)을 하면
    어떤 행/열이 실제 계산에 필요한지 미리 파악하고
    A의 열번호와 B의 행번호가 겹치는 부분만 계산만 하고
    실제로 몇 번 곱셈했는지도 세자
"""

def multiply_optimized(A: MobileSparseMatrix, B: MobileSparseMatrix) -> MobileSparseMatrix:
    """
    고성능 최적화 버전 희소행렬 곱셈
    
    최적화 기법:
    - 사전 필터링으로 불필요한 계산 제거
    - 메모리 접근 패턴 최적화
    - 일단은 ARM 프로세서 캐시 효율성 고려
    """
    if A.cols != B.rows:
        raise ValueError(f"행렬 곱셈 불가: A({A.rows}×{A.cols}) × B({B.rows}×{B.cols})")
    
    print(f" 최적화 희소행렬 곱셈 시작")
    start_time = time.time()
    
    # 1. 사전 분석: 어떤 행/열이 실제 계산에 필요한지 파악
    A_active_rows = set(A._data.keys())  # A에서 0이 아닌 원소가 있는 행
    B_active_rows = set(B._data.keys())  # B에서 0이 아닌 원소가 있는 행
    
    # A의 열과 B의 행이 겹치는 부분만 계산 (교집합)
    active_inner_dims = A_active_rows.intersection(
        set(range(A.cols))
    ).intersection(B_active_rows)
    
    print(f"   최적화: {len(active_inner_dims)}/{A.cols} 내부 차원만 계산")
    
    # 2. 결과 행렬 생성
    C = MobileSparseMatrix(A.rows, B.cols, f"Optimized {A.platform}")
    
    # 3. 최적화된 곱셈 실행
    operations_count = 0
    
    for i in A_active_rows:  # A에서 실제 데이터가 있는 행만
        A_row_data = A.get_row_data(i)
        result_row: Dict[int, float] = {}
        
        for k in A_row_data.keys():  # A[i]에서 0이 아닌 열만
            if k not in active_inner_dims:  # B[k]가 비어있으면 스킵
                continue
                
            A_ik = A_row_data[k]
            B_row_data = B.get_row_data(k)
            
            for j, B_kj in B_row_data.items():
                if j not in result_row:
                    result_row[j] = 0.0
                result_row[j] += A_ik * B_kj
                operations_count += 1
        
        # 결과 저장
        for j, value in result_row.items():
            if abs(value) > 1e-12:
                C.set(i, j, value)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"   최적화 곱셈 완료: {execution_time:.3f}초")
    print(f"   실제 연산 수: {operations_count:,}")
    print(f"   연산/초: {operations_count/execution_time:,.0f}")
    
    return C


def element_wise_add(A: MobileSparseMatrix, B: MobileSparseMatrix) -> MobileSparseMatrix:
    """
    두 희소행렬의 원소별 덧셈: C = A + B
    
    Args:
        A, B: 같은 크기의 희소행렬
        
    Returns:
        결과 행렬 C
    """
    if A.rows != B.rows or A.cols != B.cols:
        raise ValueError(f"행렬 크기 불일치: A({A.rows}×{A.cols}), B({B.rows}×{B.cols})")
    
    C = MobileSparseMatrix(A.rows, A.cols, f"Sum of {A.platform}")
    
    # A의 모든 원소 추가
    for row, col, value in A.get_nonzero_elements():
        C.set(row, col, value)
    
    # B의 원소 덧셈
    for row, col, value in B.get_nonzero_elements():
        current_value = C.get(row, col)
        C.set(row, col, current_value + value)
    
    return C