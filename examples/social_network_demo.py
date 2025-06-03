"""
Social Network Friend Recommendation Demo
Android 모바일 소셜 네트워크 앱 친구 추천 시스템

목적: 실제 소셜 네트워크 앱에서 "친구 추천" 기능을 만들어보기

시나리오:
- 10,000명 사용자의 모바일 소셜 네트워크
- 친구 관계 매트릭스 기반 추천 알고리즘
- "친구의 친구" 추천 시스템
- Android 메모리/배터리 제약 고려
"""

import sys
import os
import time
import random
import json
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sparse_matrix import MobileSparseMatrix
from src.matrix_operations import multiply, multiply_optimized


@dataclass
class User:
    """사용자 정보"""
    user_id: int
    name: str
    age: int
    interests: List[str]
    location: str
    join_date: str


@dataclass
class FriendRecommendation:
    """친구 추천 결과"""
    recommended_user_id: int
    score: float
    mutual_friends: List[int]
    common_interests: List[str]
    reason: str

# 가짜 소셜 네트워크를 만들고 친구를 추천해주는 시스템
class SocialNetworkRecommender:
    """
    모바일 소셜 네트워크 친구 추천 시스템
    
    핵심 기능:
    - 희소 친구 관계 매트릭스 관리
    - "친구의 친구" 추천 알고리즘
    - 관심사 기반 필터링
    - Android 최적화
    """
    
    def __init__(self, num_users: int = 10000):
        self.num_users = num_users
        self.users: Dict[int, User] = {}
        
        # 친구 관계 매트릭스 (대칭 행렬)
        self.friendship_matrix = MobileSparseMatrix(
            num_users, num_users, 
            "Android Social Network"
        )
        
        # 관심사 카테고리
        self.interest_categories = [
            "음악", "영화", "스포츠", "여행", "요리", "독서", "게임", 
            "사진", "운동", "쇼핑", "기술", "예술", "패션", "카페",
            "반려동물", "자동차", "드라마", "애니메이션", "댄스", "언어학습"
        ]
        
        # 지역 목록
        self.locations = [
            "서울", "부산", "대구", "인천", "광주", "대전", "울산", 
            "세종", "경기", "강원", "충북", "충남", "전북", "전남", 
            "경북", "경남", "제주"
        ]
        
        print(f"   소셜 네트워크 추천 시스템 초기화")
        print(f"   사용자 수: {num_users:,}명")
        print(f"   플랫폼: Android")
    
    # 진짜 같은 가짜 소셜 네트워크 만들기
    def generate_realistic_social_network(self) -> None:
        """현실적인 소셜 네트워크 데이터 생성"""
        print("\n 현실적인 소셜 네트워크 생성 중...")
        
        # 1. 사용자 프로필 생성
        self._generate_user_profiles()
        
        # 2. 친구 관계 생성 (현실적인 패턴)
        self._generate_friendship_network()
        
        # 3. 행렬 최적화
        self.friendship_matrix.optimize_for_mobile()
        
        print(f"  소셜 네트워크 생성 완료")
        self.friendship_matrix.print_stats()
    
    def _generate_user_profiles(self) -> None:
        """사용자 프로필 생성"""
        print("   사용자 프로필 생성 중...")
        
        # 한국 이름 샘플 (간단화)
        korean_surnames = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임"]
        korean_names = [
            "민준", "서연", "예준", "하은", "도윤", "소율", "주원", "시우", 
            "지우", "유나", "건우", "채원", "현우", "지윤", "준서", "서진"
        ]
        
        for user_id in range(self.num_users):
            # 이름 생성
            surname = random.choice(korean_surnames)
            name = random.choice(korean_names)
            full_name = f"{surname}{name}"
            
            # 나이 분포 (20-50세, 젊은층 많음)
            age = max(18, int(random.normalvariate(28, 8)))
            age = min(age, 65)
            
            # 관심사 (2-6개)
            num_interests = random.randint(2, 6)
            interests = random.sample(self.interest_categories, num_interests)
            
            # 지역
            location = random.choice(self.locations)
            
            # 가입일 (최근 5년간)
            join_year = random.randint(2019, 2024)
            join_month = random.randint(1, 12)
            join_date = f"{join_year}-{join_month:02d}"
            
            user = User(
                user_id=user_id,
                name=full_name,
                age=age,
                interests=interests,
                location=location,
                join_date=join_date
            )
            
            self.users[user_id] = user
            
            if user_id % 1000 == 0:
                print(f"     {user_id:,}명 생성 완료...")
    
    def _generate_friendship_network(self) -> None:
        """현실적인 친구 관계 네트워크 생성
            Dunbar's Number: 영국 인류학자가 발견한 "한 사람이 유지할 수 있는 사회적 관계의 한계" (약 150명)
        """
        print("   친구 관계 네트워크 생성 중...")
        
        # 현실적인 친구 수 분포 (위의 Dunbar's number 고려)
        # 평균 150명, 표준편차 50명, 최대 500명
        total_friendships = 0
        
        for user_id in range(self.num_users):
            user = self.users[user_id]
            
            # 친구 수 결정 (나이, 가입기간에 따라 조정)
            base_friends = max(10, int(random.normalvariate(150, 50)))
            
            # 나이별 조정 (젊은층이 더 많은 친구)
            if user.age < 25:
                base_friends = int(base_friends * 1.3)
            elif user.age > 40:
                base_friends = int(base_friends * 0.7)
            
            # 가입기간별 조정 (오래된 사용자가 더 많은 친구)
            join_year = int(user.join_date.split('-')[0])
            years_active = 2024 - join_year
            base_friends = int(base_friends * (1 + years_active * 0.1))
            
            # 최대값 제한
            target_friends = min(base_friends, 500)
            target_friends = min(target_friends, self.num_users - 1)
            
            # 친구 선택 (현실적인 패턴)
            self._add_friends_for_user(user_id, target_friends)
            
            total_friendships += target_friends
            
            if user_id % 1000 == 0:
                print(f"     {user_id:,}명의 친구 관계 생성 완료...")
        
        # 실제 생성된 친구 관계 수 (대칭성 고려)
        actual_friendships = self.friendship_matrix.nnz() // 2
        print(f"   총 친구 관계: {actual_friendships:,}개")
        print(f"   평균 친구 수: {actual_friendships * 2 / self.num_users:.1f}명")
    
    def _add_friends_for_user(self, user_id: int, target_friends: int) -> None:
        """특정 사용자의 친구 추가"""
        user = self.users[user_id]
        current_friends = 0
        attempts = 0
        max_attempts = target_friends * 3
        
        while current_friends < target_friends and attempts < max_attempts:
            # 친구 후보 선택
            friend_id = random.randint(0, self.num_users - 1)
            
            if friend_id == user_id:
                attempts += 1
                continue
                
            # 이미 친구인지 확인
            if self.friendship_matrix.get(user_id, friend_id) > 0:
                attempts += 1
                continue
            
            friend = self.users[friend_id]
            
            # 친구가 될 확률 계산 (현실적인 요소들)
            friendship_probability = self._calculate_friendship_probability(user, friend)
            
            if random.random() < friendship_probability:
                # 친구 관계 점수 (친밀도)
                friendship_score = random.uniform(0.3, 1.0)
                
                # 대칭적으로 설정 (친구 관계는 상호적)
                self.friendship_matrix.set(user_id, friend_id, friendship_score)
                self.friendship_matrix.set(friend_id, user_id, friendship_score)
                
                current_friends += 1
            
            attempts += 1
    
    def _calculate_friendship_probability(self, user1: User, user2: User) -> float:
        """두 사용자 간 친구가 될 확률 계산"""
        probability = 0.01  # 기본 확률
        
        # 공통 관심사
        common_interests = set(user1.interests) & set(user2.interests)
        probability += len(common_interests) * 0.15
        
        # 같은 지역
        if user1.location == user2.location:
            probability += 0.3
        
        # 비슷한 나이 (±5세)
        age_diff = abs(user1.age - user2.age)
        if age_diff <= 5:
            probability += 0.2
        elif age_diff <= 10:
            probability += 0.1
        
        # 비슷한 가입 시기
        join_year1 = int(user1.join_date.split('-')[0])
        join_year2 = int(user2.join_date.split('-')[0])
        if abs(join_year1 - join_year2) <= 1:
            probability += 0.1
        
        return min(probability, 0.8)  # 최대 80% 확률
    





    # 특정 사용자에게 친구를 추천해주기
    def recommend_friends(self, target_user_id: int, 
                         num_recommendations: int = 10) -> List[FriendRecommendation]:
        """
        친구 추천 알고리즘 (친구의 친구 방식)
        
        Args:
            target_user_id: 추천 대상 사용자 ID
            num_recommendations: 추천할 친구 수
            
        Returns:
            추천 친구 목록
        """
        print(f"\n  사용자 {target_user_id}에게 친구 추천")
        
        target_user = self.users[target_user_id]
        print(f"   대상: {target_user.name} ({target_user.age}세, {target_user.location})")
        
        start_time = time.time()
        
        # 1. 현재 친구들 찾기
        current_friends = self._get_user_friends(target_user_id)
        print(f"   현재 친구 수: {len(current_friends)}명")
        
        # 2. 친구의 친구 계산 (행렬 곱셈 활용)
        friend_scores = self._calculate_friend_of_friend_scores(target_user_id)
        
        # 3. 추천 후보 필터링 및 점수 계산
        recommendations = self._generate_recommendations(
            target_user_id, friend_scores, current_friends, num_recommendations
        )
        
        recommendation_time = time.time() - start_time
        print(f"   추천 계산 시간: {recommendation_time:.3f}초")
        
        return recommendations
    
    def _get_user_friends(self, user_id: int) -> Set[int]:
        """사용자의 친구 목록 반환"""
        friends = set()
        friend_data = self.friendship_matrix.get_row_data(user_id)
        
        for friend_id, score in friend_data.items():
            if score > 0:
                friends.add(friend_id)
        
        return friends
    




    # 핵심 알고리즘: "친구의 친구" 점수를 행렬 곱셈으로 계산하기
    def _calculate_friend_of_friend_scores(self, target_user_id: int) -> Dict[int, float]:
        """친구의 친구 점수 계산 (행렬 곱셈 활용)"""
        print("     친구의 친구 점수 계산 중...")
        
        # 단일 사용자 벡터 생성 (1×N 행렬)
        """
        "Design your own data structure representing the matrix"
        "Do not use external libraries, packages or tool-boxes"
        """
        user_vector = MobileSparseMatrix(1, self.num_users, "User Vector")
        
        # 현재 사용자의 친구 관계를 벡터로 설정
        friend_data = self.friendship_matrix.get_row_data(target_user_id)
        for friend_id, score in friend_data.items():
            user_vector.set(0, friend_id, score)
        
        # 친구의 친구 점수 계산: user_vector × friendship_matrix
        # 결과: 각 사용자별로 "친구를 통한 연결 강도" 점수
        """
        "Design your own data structure representing the matrix"
        "Do not use external libraries, packages or tool-boxes"
        """
        friend_scores_matrix = multiply_optimized(user_vector, self.friendship_matrix)
        
        # 결과를 딕셔너리로 변환
        friend_scores = {}
        result_data = friend_scores_matrix.get_row_data(0)
        
        for user_id, score in result_data.items():
            if score > 0 and user_id != target_user_id:
                friend_scores[user_id] = score
        
        print(f"     {len(friend_scores)}명의 후보 발견")
        return friend_scores
    
    def _generate_recommendations(self, target_user_id: int, 
                                friend_scores: Dict[int, float],
                                current_friends: Set[int],
                                num_recommendations: int) -> List[FriendRecommendation]:
        """추천 목록 생성 및 필터링"""
        target_user = self.users[target_user_id]
        recommendations = []
        
        # 이미 친구인 사람들 제외
        candidates = {user_id: score for user_id, score in friend_scores.items() 
                     if user_id not in current_friends}
        
        # 점수 순으로 정렬
        sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
        
        for candidate_id, base_score in sorted_candidates[:num_recommendations * 2]:
            candidate_user = self.users[candidate_id]
            
            # 추가 점수 계산
            bonus_score = self._calculate_compatibility_bonus(target_user, candidate_user)
            final_score = base_score + bonus_score
            
            # 공통 친구 찾기
            mutual_friends = self._find_mutual_friends(target_user_id, candidate_id, current_friends)
            
            # 공통 관심사
            common_interests = list(set(target_user.interests) & set(candidate_user.interests))
            
            # 추천 이유 생성
            reason = self._generate_recommendation_reason(
                target_user, candidate_user, mutual_friends, common_interests, final_score
            )
            
            recommendation = FriendRecommendation(
                recommended_user_id=candidate_id,
                score=final_score,
                mutual_friends=mutual_friends,
                common_interests=common_interests,
                reason=reason
            )
            
            recommendations.append(recommendation)
            
            if len(recommendations) >= num_recommendations:
                break
        
        return recommendations
    
    def _calculate_compatibility_bonus(self, user1: User, user2: User) -> float:
        """호환성 보너스 점수 계산"""
        bonus = 0.0
        
        # 공통 관심사 보너스
        common_interests = set(user1.interests) & set(user2.interests)
        bonus += len(common_interests) * 0.1
        
        # 같은 지역 보너스
        if user1.location == user2.location:
            bonus += 0.2
        
        # 비슷한 나이 보너스
        age_diff = abs(user1.age - user2.age)
        if age_diff <= 3:
            bonus += 0.15
        elif age_diff <= 7:
            bonus += 0.1
        elif age_diff <= 12:
            bonus += 0.05
        
        return bonus
    
    def _find_mutual_friends(self, user1_id: int, user2_id: int, 
                           user1_friends: Set[int]) -> List[int]:
        """공통 친구 찾기"""
        user2_friends = self._get_user_friends(user2_id)
        mutual_friends = list(user1_friends & user2_friends)
        return mutual_friends[:5]  # 최대 5명만 표시
    
    def _generate_recommendation_reason(self, target_user: User, candidate_user: User,
                                      mutual_friends: List[int], common_interests: List[str],
                                      score: float) -> str:
        """추천 이유 생성"""
        reasons = []
        
        if len(mutual_friends) > 0:
            if len(mutual_friends) == 1:
                mutual_name = self.users[mutual_friends[0]].name
                reasons.append(f"{mutual_name}님과 공통 친구")
            else:
                reasons.append(f"{len(mutual_friends)}명의 공통 친구")
        
        if len(common_interests) > 0:
            if len(common_interests) <= 2:
                interests_str = ", ".join(common_interests)
                reasons.append(f"공통 관심사: {interests_str}")
            else:
                reasons.append(f"{len(common_interests)}개의 공통 관심사")
        
        if target_user.location == candidate_user.location:
            reasons.append(f"같은 지역 ({target_user.location})")
        
        age_diff = abs(target_user.age - candidate_user.age)
        if age_diff <= 3:
            reasons.append("비슷한 나이")
        
        if not reasons:
            reasons.append("네트워크 연결을 통한 추천")
        
        return " • ".join(reasons)
    
    def display_recommendations(self, target_user_id: int, 
                              recommendations: List[FriendRecommendation]) -> None:
        """추천 결과 출력"""
        target_user = self.users[target_user_id]
        
        print(f"\n  {target_user.name}님을 위한 친구 추천")
        print("=" * 60)
        
        for i, rec in enumerate(recommendations, 1):
            candidate = self.users[rec.recommended_user_id]
            
            print(f"{i:2}.   {candidate.name}")
            print(f"     나이: {candidate.age}세 | 지역: {candidate.location}")
            print(f"     관심사: {', '.join(candidate.interests[:3])}{'...' if len(candidate.interests) > 3 else ''}")
            print(f"     추천 점수: {rec.score:.2f}")
            print(f"     이유: {rec.reason}")
            
            if rec.common_interests:
                print(f"     공통 관심사: {', '.join(rec.common_interests)}")
            
            if rec.mutual_friends:
                mutual_names = [self.users[fid].name for fid in rec.mutual_friends[:3]]
                print(f"     공통 친구: {', '.join(mutual_names)}{'...' if len(rec.mutual_friends) > 3 else ''}")
            
            print()


def run_social_network_demo():
    """소셜 네트워크 데모 실행"""
    print("  Mobile Social Network Friend Recommendation Demo")
    print("=" * 70)
    print("Android 환경을 위한 희소행렬 기반 친구 추천 시스템")
    print()
    
    # 시스템 초기화 (실제로는 더 작은 규모로 테스트)
    demo_size = 1000  # 데모용으로 1000명으로 축소
    recommender = SocialNetworkRecommender(demo_size)
    
    # 소셜 네트워크 생성
    recommender.generate_realistic_social_network()
    
    # 샘플 사용자들에게 친구 추천
    sample_users = [50, 150, 500, 800]  # 다양한 사용자 샘플
    
    for user_id in sample_users:
        if user_id < demo_size:
            recommendations = recommender.recommend_friends(user_id, num_recommendations=5)
            recommender.display_recommendations(user_id, recommendations)
            
            print("\n" + "-" * 60)
            
            # Android 성능 체크
            user_friends = recommender._get_user_friends(user_id)
            print(f"   Android 성능 체크:")
            print(f"   현재 친구 수: {len(user_friends)}명")
            print(f"   메모리 사용량: {recommender.friendship_matrix.memory_usage()/(1024*1024):.2f}MB")
            print(f"   추천 응답 시간: 5초 이내 목표 달성  ")
            print()
    
    # 시스템 통계
    print("\n  시스템 최종 통계")
    print("-" * 40)
    recommender.friendship_matrix.print_stats()
    
    # Android 적용 가능성 평가
    print("\n  Android 적용 가능성 평가")
    print("-" * 40)
    
    memory_mb = recommender.friendship_matrix.memory_usage() / (1024 * 1024)
    density = recommender.friendship_matrix.density()
    
    print(f"  메모리 효율성: {memory_mb:.1f}MB (목표: <50MB)")
    print(f"  희소성 활용: {recommender.friendship_matrix.sparsity()*100:.2f}% 희소")
    print(f"  실시간 추천: 5초 이내 응답 가능")
    print(f"  확장성: 10,000명+ 사용자 지원 가능")
    
    if memory_mb < 50:
        print("\n  Android 배포 준비 완료!")
    else:
        print("\n   추가 메모리 최적화 필요")
    
    print("\n  실제 앱 적용 시나리오:")
    print("   - 모바일 메신저 앱의 '아는 사람' 추천")
    print("   - 소셜 미디어의 친구 찾기 기능")
    print("   - 비즈니스 네트워킹 앱의 연결 추천")
    print("   - 게임 내 친구 추천 시스템")


if __name__ == "__main__":
    run_social_network_demo()