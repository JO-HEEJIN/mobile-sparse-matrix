"""
Mobile Sparse Matrix Implementation
Android Snapdragon 최적화 희소행렬


Author: Heejin Jo
Platform: Android ARM64
Target: Social Network Friend Recommendation System
"""




"""
문제가 이거였음

1. Consider a matrix where the number of zeroes is much greater than the number of nonzero elements, but the nonzero elements are randomly distributed throughout the matrix. Design your own data structure representing the matrix assuming the size can be possibly very large and write code to multiply two such matrices. Use any language of your choice for any platform. Do not use external libraries, packages or tool-boxes (except STL for C++).

* Please use float type for data. For size of matrices, you can just use integer type.

일단 sparce matrix 를 설명한 듯 그러면 그 계산을 메모리 효율적으로 할 수 있게 진행하자. 왜냐하면 아마도 희소행렬 곱셈이 얼마나 효율적인가? 를 보고 싶어하는 거 같으니

이 스크립트의 목적: 메모리를 아껴쓰면서 빠르게 동작하는 행렬 저장소
두 희소행렬 계산하는 건 따로 파일을 만들자.

그러려면 우선 

matrix = [[0, 0, 0, 5, 0],
          [0, 0, 0, 0, 0], 
          [3, 0, 0, 0, 7]] 

이 형식으로 가면 안 될 거 같다. 

_data = {
    0: {3: 5.0},        # 0행 3열에 5
    2: {0: 3.0, 4: 7.0} # 2행 0열에 3, 2행 4열에 7
}
일단 이런 접근 방식을 사용해보자.


"""



import sys
import time
from typing import Dict, List, Tuple, Optional, Iterator


class MobileSparseMatrix:
    """
    모바일 환경 최적화 희소행렬
    
    특징:
    - 메모리 효율적 저장 (딕셔너리 + 리스트 하이브리드)
    - ARM 프로세서 캐시 친화적 접근
    - Android 메모리 제약 고려 (512MB 이하)
    - 배터리 효율적 연산
    """
    
    def __init__(self, rows: int, cols: int, platform: str = "Android ARM64"):
        """
        희소행렬 초기화
        
        Args:
            rows: 행 수
            cols: 열 수  
            platform: 타겟 플랫폼 (문서화용)
        """
        if rows <= 0 or cols <= 0:
            raise ValueError("행렬 크기는 양수여야 합니다")
        
        self.rows = rows
        self.cols = cols
        self.platform = platform
        
        # 이게 이제 위에서 말한 핵심 자료구조: 행-기반 딕셔너리
        # {row: {col: value}} 구조로 2단계 해시
        self._data: Dict[int, Dict[int, float]] = {}
        
        # 성능 모니터링
        self._nnz_count = 0  # 0이 아닌 원소 개수
        self._memory_peak = 0
        self._last_access_time = time.time()
        
        print(f" MobileSparseMatrix 생성: {rows}×{cols} on {platform}")
    
    # 특정 위치에 값 저장하는 함수, 행렬 밖 위치면 에러 발생하게 하고 값이 거의 0이면 저장하지 말고 메모리 절약을 위해 이미 있던 값인지 확인
    def set(self, row: int, col: int, value: float) -> None:
        """
        행렬 원소 설정
        
        Args:
            row: 행 인덱스 (0-based)
            col: 열 인덱스 (0-based)  
            value: 설정할 값
        """
        # 범위 검사
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise IndexError(f"인덱스 범위 초과: ({row}, {col})")
        
        # 0에 가까운 값은 저장 노노 
        if abs(value) < 1e-12:
            self._remove_if_exists(row, col)
            return
        
        # 기존 값이 있는지 확인하고
        old_exists = self._has_value(row, col)
        
        # 그런 뒤 값 저장
        if row not in self._data:
            self._data[row] = {}
        
        self._data[row][col] = value
        
        # 개수 업데이트
        if not old_exists:
            self._nnz_count += 1
        
        # 주기적 메모리 체크 (모바일 환경에서 중요)
        if self._nnz_count % 1000 == 0:
            self._check_memory_usage()
    
    # 특정 위치의 값 가져오는 함수, 찾아보고 없으면 빈 공간으로 간주
    def get(self, row: int, col: int) -> float:
        """
        행렬 원소 조회
        
        Args:
            row: 행 인덱스
            col: 열 인덱스
            
        Returns:
            해당 위치의 값 (없으면 0.0)
        """
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise IndexError(f"인덱스 범위 초과: ({row}, {col})")
        
        if row in self._data and col in self._data[row]:
            return self._data[row][col]
        return 0.0
    

    """ 그리고 이제 통계 정보를 넣어야겠다. 예를 들어, 100개 칸 중 5개만 차있으면 밀도=5%, 희소성=95% """
    def nnz(self) -> int:
        """0이 아닌 원소 개수 반환"""
        return self._nnz_count
    
    def density(self) -> float:
        """행렬 밀도 계산 (0이 아닌 원소 비율)"""
        total_elements = self.rows * self.cols
        return self._nnz_count / total_elements if total_elements > 0 else 0.0
    
    def sparsity(self) -> float:
        """희소성 계산 (0인 원소 비율)"""
        return 1.0 - self.density()
    



    # 실제로는 메모리를 얼마나 쓰는거지?
    def memory_usage(self) -> int:
        """
        추정 메모리 사용량 (바이트)
        
        Returns:
            대략적인 메모리 사용량
        """
        # 딕셔너리 오버헤드 + 실제 데이터
        dict_overhead = len(self._data) * 64  # 딕셔너리 엔트리당 추정
        value_storage = self._nnz_count * (8 + 8 + 8)  # int + int + float
        return dict_overhead + value_storage
    



    
    def get_row_data(self, row: int) -> Dict[int, float]:
        """
        특정 행의 모든 0이 아닌 원소 반환
        
        Args:
            row: 행 인덱스
            
        Returns:
            {col: value} 딕셔너리
        """
        if not (0 <= row < self.rows):
            raise IndexError(f"행 인덱스 범위 초과: {row}")
        
        return self._data.get(row, {}).copy()
    
    def get_nonzero_elements(self) -> Iterator[Tuple[int, int, float]]:
        """
        모든 0이 아닌 원소를 (row, col, value) 형태로 순회
        
        Yields:
            (row, col, value) 튜플
        """
        for row, row_data in self._data.items():
            for col, value in row_data.items():
                yield (row, col, value)
    
    def _has_value(self, row: int, col: int) -> bool:
        """내부용: 해당 위치에 값이 있는지 확인"""
        return row in self._data and col in self._data[row]
    
    def _remove_if_exists(self, row: int, col: int) -> None:
        """내부용: 값이 있으면 제거"""
        if self._has_value(row, col):
            del self._data[row][col]
            self._nnz_count -= 1
            
            # 빈 행 제거 (메모리 절약)
            if not self._data[row]:
                del self._data[row]
    
    def _check_memory_usage(self) -> None:
        """내부용: 메모리 사용량 모니터링"""
        current_memory = self.memory_usage()
        if current_memory > self._memory_peak:
            self._memory_peak = current_memory
        
        # 메모리 경고 (512MB 제한의 10% = 50MB)
        if current_memory > 50 * 1024 * 1024:
            print(f" 메모리 사용량 경고: {current_memory / (1024*1024):.1f}MB")
    




    # 모바일에서 더 빠르게 동작하도록 청소하게 하는 함수
    def optimize_for_mobile(self) -> None:
        """
        모바일 환경 최적화
        - 메모리 정리
        - 가비지 컬렉션
        """
        print("📱 모바일 최적화 실행 중...")
        
        # 빈 행 제거
        empty_rows = [row for row, row_data in self._data.items() if not row_data]
        for row in empty_rows:
            del self._data[row]
        
        # 메모리.. 사용량 재계산이 필요할 듯
        self._check_memory_usage()
        
        print(f"최적화 완료: {self.nnz()}개 원소, {self.memory_usage()/(1024*1024):.2f}MB")
    
    def print_stats(self) -> None:
        """행렬 통계 정보 출력"""
        print(f"\n MobileSparseMatrix 통계:")
        print(f"   크기: {self.rows} × {self.cols}")
        print(f"   0이 아닌 원소: {self.nnz():,}")
        print(f"   밀도: {self.density()*100:.4f}%")
        print(f"   희소성: {self.sparsity()*100:.4f}%")
        print(f"   메모리 사용량: {self.memory_usage()/(1024*1024):.2f}MB")
        print(f"   플랫폼: {self.platform}")
    
    def __str__(self) -> str:
        """문자열 표현"""
        return f"MobileSparseMatrix({self.rows}×{self.cols}, nnz={self.nnz()})"
    
    def __repr__(self) -> str:
        """개발자용 표현"""
        return f"MobileSparseMatrix(rows={self.rows}, cols={self.cols}, nnz={self.nnz()})"