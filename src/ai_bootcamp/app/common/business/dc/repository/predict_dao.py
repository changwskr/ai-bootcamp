import sqlite3
from typing import Any, Dict, List, Optional


class PredictDAO:
    """예측 관련 데이터 접근 객체 (DAO)"""

    def __init__(self, db_path: str = "predict.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 예측 결과 테이블 생성
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    label TEXT NOT NULL,
                    score REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model_version TEXT DEFAULT 'baseline'
                )
            """
            )

            # 모델 정보 테이블 생성
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS model_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    version TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """
            )

            # 기본 모델 정보 생성
            cursor.execute(
                """
                INSERT OR IGNORE INTO model_info (model_name, model_type, version)
                VALUES (?, ?, ?)
            """,
                ("baseline", "text_classifier", "1.0.0"),
            )

            conn.commit()

    def save_prediction(
        self, text: str, label: str, score: float, model_version: str = "baseline"
    ) -> int:
        """예측 결과 저장"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO predictions (text, label, score, model_version)
                VALUES (?, ?, ?, ?)
            """,
                (text, label, score, model_version),
            )
            conn.commit()
            return cursor.lastrowid

    def get_prediction_by_id(self, prediction_id: int) -> Optional[Dict[str, Any]]:
        """ID로 예측 결과 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, text, label, score, created_at, model_version
                FROM predictions WHERE id = ?
            """,
                (prediction_id,),
            )

            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "text": row[1],
                    "label": row[2],
                    "score": row[3],
                    "created_at": row[4],
                    "model_version": row[5],
                }
            return None

    def get_recent_predictions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 예측 결과 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, text, label, score, created_at, model_version
                FROM predictions 
                ORDER BY created_at DESC 
                LIMIT ?
            """,
                (limit,),
            )

            return [
                {
                    "id": row[0],
                    "text": row[1],
                    "label": row[2],
                    "score": row[3],
                    "created_at": row[4],
                    "model_version": row[5],
                }
                for row in cursor.fetchall()
            ]

    def get_model_info(self) -> Optional[Dict[str, Any]]:
        """현재 활성 모델 정보 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT model_name, model_type, version, created_at
                FROM model_info WHERE is_active = 1
                ORDER BY created_at DESC LIMIT 1
            """
            )

            row = cursor.fetchone()
            if row:
                return {
                    "model_name": row[0],
                    "model_type": row[1],
                    "version": row[2],
                    "created_at": row[3],
                }
            return None

    def update_model_info(self, model_name: str, model_type: str, version: str) -> bool:
        """모델 정보 업데이트"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 기존 모델 비활성화
            cursor.execute("UPDATE model_info SET is_active = 0")

            # 새 모델 정보 추가
            cursor.execute(
                """
                INSERT INTO model_info (model_name, model_type, version)
                VALUES (?, ?, ?)
            """,
                (model_name, model_type, version),
            )

            conn.commit()
            return True

    def get_prediction_stats(self) -> Dict[str, Any]:
        """예측 통계 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 전체 예측 수
            cursor.execute("SELECT COUNT(*) FROM predictions")
            total_predictions = cursor.fetchone()[0]

            # 라벨별 예측 수
            cursor.execute(
                """
                SELECT label, COUNT(*) as count
                FROM predictions 
                GROUP BY label
            """
            )
            label_counts = dict(cursor.fetchall())

            # 평균 점수
            cursor.execute("SELECT AVG(score) FROM predictions")
            avg_score = cursor.fetchone()[0] or 0.0

            return {
                "total_predictions": total_predictions,
                "label_counts": label_counts,
                "average_score": round(avg_score, 3),
            }
