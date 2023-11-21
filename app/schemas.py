JOB_SCHEMA = {
    "$schema": "http://json-schema.org/schema#",
    "title": "JOB",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "name",
        "enabled",
        "cron_schedule",
        "url",
        "method",
        "type"
    ],
    "properties": {
        "name": {
            "type": "string",
            "pattern": "^[a-z0-9-_]*$"
        },
        "description": {
            "type": "string",
            "pattern": "^[a-z0-9-_]*$"
        },
        "enabled": {
            "type": "boolean"
        },
        "basic_auth": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "username",
                "password"
            ],
            "properties": {
                "username": {
                    "type": "string"
                },
                "password": {
                    "type": "string"
                }
            },
        },
        "cron_schedule": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "minute",
                "hour",
                "day",
                "month",
                "day_of_the_week"
            ],
            "properties": {
                "minute": {
                    "type": "string"
                },
                "hour": {
                    "type": "string"
                },
                "day": {
                    "type": "string"
                },
                "month": {
                    "type": "string"
                },
                "day_of_the_week": {
                    "type": "string"
                },
            },
        },
        "url": {
            "description": "The url to call",
            "type": "string",
            "format": "url"
        },
        "method": {
            "type": "string",
            "enum": ["GET", "POST", "PUT"]
        },
        "type": {
            "type": "string",
            "enum": ["JOB"]
        },
        "headers": {
            "type": "object"
        },
        "body_json": {
            "type": "object"
        },
    }
}

JOBS_SCHEMA = {
    "$schema": "http://json-schema.org/schema#",
    "type": "array",
    "items": JOB_SCHEMA
}

JOB_INFO_SCHEMA = {
    "$schema": "http://json-schema.org/schema#",
    "title": "JOB_INFO",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "name",
        "properties"
    ],
    "properties": {
        "name": {
            "type": "string"
        },
        "description": {
            "type": "string",
            "pattern": "^[a-z0-9-_]*$"
        },
        "properties": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "state",
                "status"],
            "properties": {
                "state": {
                    "type": "string",
                    "enum": ["enabled", "disabled"]
                },
                "status": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "executionCount",
                        "failureCount",
                        "faultedCount",
                        "lastExecutionTime",
                        "nextExecutionTime",
                        "lastStatusCode"
                    ],
                    "properties": {
                        "executionCount": {
                            "type": "number",
                        },
                        "failureCount": {
                            "type": "number"
                        },
                        "faultedCount": {
                            "type": "number"
                        },
                        "lastExecutionTime": {
                            "type": ["string", "null"],
                            "oneOf": [
                                {
                                    "type": "string",
                                    "format": "date-time"
                                }, {
                                    "type": "null"
                                }
                            ]
                        },
                        "nextExecutionTime": {
                            "type": ["string", "null"],
                            "oneOf": [
                                {
                                    "type": "string",
                                    "format": "date-time"
                                }, {
                                    "type": "null"
                                }
                            ]
                        },
                        "lastJsonResponse": {
                            "type": ["array", "object", "null"],
                            "oneOf": [
                                {
                                    "type": "array"
                                }, {
                                    "type": "object"
                                }, {
                                    "type": "null"
                                }
                            ]
                        },
                        "lastTextResponse": {
                            "type": ["string", "null"],
                            "oneOf": [
                                {
                                    "type": "string",
                                }, {
                                    "type": "null"
                                }
                            ]
                        },
                        "lastStatusCode": {
                            "type": ["number", "null"],
                            "oneOf": [
                                {
                                    "type": "number",
                                }, {
                                    "type": "null"
                                }
                            ]
                        },
                    }
                }
            }
        }
    }
}

JOBS_INFO_SCHEMA = {
    "$schema": "http://json-schema.org/schema#",
    "type": "array",
    "items": JOB_INFO_SCHEMA
}
