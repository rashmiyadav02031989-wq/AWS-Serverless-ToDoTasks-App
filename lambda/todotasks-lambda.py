import json
import boto3
import uuid
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Tasks')


def lambda_handler(event, context):
    method = event["requestContext"]["http"]["method"]

    try:
        # GET /tasks
        if method == "GET":
            response = table.scan()

            return {
                "statusCode": 200,
                "headers": cors_headers(),
                "body": json.dumps(response["Items"])
            }

        # POST /tasks
        elif method == "POST":
            body = json.loads(event["body"])

            task = body.get("task")

            if not task:
                return {
                    "statusCode": 400,
                    "headers": cors_headers(),
                    "body": json.dumps({"message": "Task is required"})
                }

            item = {
                "taskId": str(uuid.uuid4()),
                "task": task,
                "completed": False
            }

            table.put_item(Item=item)

            return {
                "statusCode": 201,
                "headers": cors_headers(),
                "body": json.dumps(item)
            }

        # DELETE /tasks/{taskId}
        elif method == "DELETE":
            task_id = event["pathParameters"]["taskId"]

            table.delete_item(
                Key={
                    "taskId": task_id
                }
            )

            return {
                "statusCode": 200,
                "headers": cors_headers(),
                "body": json.dumps({
                    "message": "Task deleted"
                })
            }

        # PUT /tasks/{taskId}
        elif method == "PUT":
            task_id = event["pathParameters"]["taskId"]

            body = json.loads(event["body"])
            completed = body.get("completed")

            table.update_item(
                Key={
                    "taskId": task_id
                },
                UpdateExpression="SET completed = :c",
                ExpressionAttributeValues={
                    ":c": completed
                }
            )

            return {
                "statusCode": 200,
                "headers": cors_headers(),
                "body": json.dumps({
                    "message": "Task updated"
                })
            }

        else:
            return {
                "statusCode": 405,
                "headers": cors_headers(),
                "body": json.dumps({
                    "message": "Method not allowed"
                })
            }

    except Exception as e:
        print("ERROR:", str(e))

        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({
                "message": str(e)
            })
        }


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
    }
