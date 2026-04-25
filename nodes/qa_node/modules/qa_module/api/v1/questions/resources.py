"""REST API ресурсы"""

# Работа с фреймворком
from flask import jsonify, make_response

# Работа с REST API
from flask_restful import Resource

# Парсеры
from .parsers import QuestionParsers

# Валидаторы
from .validators import QuestionAborts, QuestionValidators

# Работа с ORM
from qa_node import db_manager
from qa_node.data.models.question import Question


class QuestionResource(Resource):
    """Ресурс одного вопроса"""

    def get(self, question_id: int):
        # Получение вопроса из БД
        with db_manager.create_session() as db_session:
            question: Question = db_session.get(Question, question_id)
            # Проверки
            QuestionValidators.is_exists(question)

            # Вывод результата
            return jsonify(
                {"question": question.to_dict(only=["id", "name", "content", "creator_id", "is_solved", "is_closed"])}
            )

    def put(self, question_id: int):
        # Получение данных из парсера
        question_data: dict = QuestionParsers.put_parser.parse_args()

        # Изменение данных в БД
        with db_manager.create_session() as db_session:
            # Получение вопроса из БД
            question: Question = db_session.get(Question, question_id)
            # Проверки
            QuestionValidators.is_exists(question)
            QuestionValidators.is_available(question_data)

            # Изменение вопроса
            for field_name, value in question_data.items():
                if value is not None: setattr(question, field_name, value)

            # Сохранение изменений
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})

    def delete(self, question_id: int):
        # Удаление из БД
        with db_manager.create_session() as db_session:
            # Получение вопроса из БД
            question: Question = db_session.get(Question, question_id)
            # Проверки
            QuestionValidators.is_exists(question)
            QuestionValidators.is_available(question)

            # Удаление вопроса
            db_session.delete(question)
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})


class QuestionListResource(Resource):
    """Ресурс списка вопросов"""

    def get(self):
        # Получение данных из парсера
        filter_params = QuestionParsers.get_list_parser.parse_args()

        # Получение вопросов из БД
        with db_manager.create_session() as db_session:
            if filter_params["search"]:
                questions: list[Question] = db_session.query(Question).filter(
                    Question.name.ilike(f"%{filter_params["search"]}%")
                ).all()
            else:
                questions: list[Question] = db_session.query(Question).all()

            # Вывод результата
            return jsonify({"questions": [question.to_dict(only=["id", "name"]) for question in questions]})

    def post(self):
        # Получение данных из парсера
        question_data: dict = QuestionParsers.post_parser.parse_args()

        # Добавление в БД
        with db_manager.create_session() as db_session:
            # Создание вопроса
            question = Question()
            for field_name, value in question_data.items():
                setattr(question, field_name, value)

            # Добавление объекта в БД
            db_session.add(question)
            db_session.commit()

            # Вывод результата
            return make_response(jsonify({"id": question.id}), 201)
