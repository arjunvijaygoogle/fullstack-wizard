# Navi

Project Navi

# API endpoints

Postman Collection Link - [here](https://www.postman.com/orange-rocket-81485/workspace/project-navi-backend/collection/27998902-361c7dcc-cca2-4a0d-ab02-833f52ec3ad1?action=share&creator=27998902) <br/>
These endpoints allow you to create a new conversation and post new prompts in these conversations.

## GET
[/conversations](#get-conversations) <br/>
[/conversations/{conversation_id}/messages](#get-conversationsconversation_idmessages) <br/>

## POST
[/conversations](#post-conversations) <br/>
[/conversations/{conversation_id}/messages](#post-conversationsconversation_idmessages) <br/>
___

### GET /conversations
Get all the conversations for a particular user.

**Parameters**

|          Name | Required |  Type   | Description                                                                                                                                                           |
| -------------:|:--------:|:-------:| --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|     `userEmail` | required | string  | Email ID of the User                                    |

**Response**

```
[
    {
        "createdAt": "2024-07-13T11:59:55.466Z",
        "id": "29f43313-93f8-4eb0-8cc9-d85df7xxxxxx",
        "llmName": "string",
        "userEmail": "user@example.com"
    }
]

or any implemented error from https://buffer.com/developers/api/errors

{
    "code": 1000,
    "error": "An error message"
}
```

### GET /conversations/{conversation_id}/messages
Get all the messages for a given conversation id.

**Response**

```
[
    {
        "conversationId": "29f43313-93f8-4eb0-8cc9-d85df7875f05",
        "createdAt": "2024-07-13T12:00:01.118Z",
        "id": "c4ca922b-f399-47d9-bd98-b4da5002320f",
        "prompt": "Sample Prompt",
        "response": "Sample response from the LLM"
    }
]

or any implemented error from https://buffer.com/developers/api/errors

{
    "code": 1000,
    "error": "An error message"
}
```

### POST /conversations
Get a new conversation ID.

**Response**

```
7123cba2-1910-447d-aa54-d4a5f5xxxxxx

or any implemented error from https://buffer.com/developers/api/errors

{
    "code": 1000,
    "error": "An error message"
}
```

### POST /conversations/{conversation_id}/messages
Post the prompt in the given conversation and get response from the LLM.

**Request Body**
```
{
    "prompt": "Sample Prompt",
    "userEmail": "user@example.com",
    "llmName": "llm name"
}
```

**Response**

```
{
    "conversationId": "7e2bc15f-9f77-45b0-bf24-eb8066a9b6e7",
    "createdAt": "2024-07-15T08:17:23.536Z",
    "id": "7b69a596-1f2a-41a9-9ce0-926521bd9b18",
    "prompt": "Sample Prompt",
    "response": "Sample response from the LLM"
}

or any implemented error from https://buffer.com/developers/api/errors

{
    "code": 1000,
    "error": "An error message"
}
```