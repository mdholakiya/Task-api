import json
import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])


def respond(status, body):
    return {"statusCode": status, "body": json.dumps(body, default=str)}


def handler(event, context):
    user_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    method = event["requestContext"]["http"]["method"]

    if method == "GET":
        items = table.query(KeyConditionExpression=Key("userId").eq(user_id))["Items"]
        return respond(200, items)

    if method == "POST":
        body = json.loads(event.get("body") or "{}")
        item = {"userId": user_id, "taskId": str(uuid.uuid4()),
                "title": body.get("title", ""), "done": False}
        table.put_item(Item=item)
        return respond(201, item)

    if method == "DELETE":
        task_id = event["pathParameters"]["id"]
        table.delete_item(Key={"userId": user_id, "taskId": task_id})
        return respond(200, {"deleted": task_id})

    return respond(405, {"error": "Method not allowed"})
