from notion_client import Client
from config import NOTION_SECRET, DATABASE_ID

notion = Client(auth=NOTION_SECRET)


def create_task_for_user(task_name, user_notion_id):
    try:
        return notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                'Name': {
                    'title': [
                        {
                            'text': {
                                'content': task_name,
                            }
                        }
                    ]
                },
                "Assign": {
                    "people": [
                        {"id": user_notion_id}
                    ]
                }
            }
        )

    except Exception as e:
        print("Failed to create task:", e)
        return None


def get_tasks_assigned_to_user(user_notion_id):
    try:
        response = notion.databases.query(**{
            "database_id": DATABASE_ID,
            "filter": {
                "and": [
                    {
                        "property": "Assign",
                        "people": {
                            "contains": user_notion_id
                        }
                    },
                    {
                        "and": [
                            {
                                "property": "Status",
                                "status": {
                                    "does_not_equal": "Готово"
                                }
                            },
                            {
                                "property": "Status",
                                "status": {
                                    "does_not_equal": "Отмена"
                                }
                            }
                        ]
                    }
                ]
            }
        })
        return response['results']  # Возвращает список задач
    except Exception as e:
        print("Failed to retrieve tasks:", e)
        return []


