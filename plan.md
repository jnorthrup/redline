c++23, liobcurl+ssl, boost::json, cmake-only build files checked in, llvm19 and apple-silly custom footprint right now

implement cleanly 
{
  "openapi": "3.0.0",
  "info": {
    "title": "Generic AI Model API",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://api.example.com/v1"
    }
  ],
  "components": {
    "securitySchemes": {
      "bearerAuth": {
        "type": "http",
        "scheme": "bearer"
      }
    },
    "schemas": {
      "ModelInfo": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string"
          },
          "status": {
            "type": "string",
            "enum": ["ready", "loading", "error"]
          }
        }
      },
      "Completion": {
        "type": "object",
        "required": ["prompt"],
        "properties": {
          "prompt": {
            "type": "string"
          },
          "max_tokens": {
            "type": "integer"
          },
          "temperature": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          }
        }
      },
      "CompletionResponse": {
        "type": "object",
        "properties": {
          "text": {
            "type": "string"
          },
          "usage": {
            "type": "object",
            "properties": {
              "total_tokens": {
                "type": "integer"
              }
            }
          }
        }
      },
      "Error": {
        "type": "object",
        "properties": {
          "error": {
            "type": "object",
            "properties": {
              "message": {
                "type": "string"
              },
              "type": {
                "type": "string"
              },
              "code": {
                "type": "string"
              }
            }
          }
        }
      }
    }
  },
  "paths": {
    "/models": {
      "get": {
        "summary": "List available models",
        "operationId": "listModels",
        "security": [
          {
            "bearerAuth": []
          }
        ],
        "responses": {
          "200": {
            "description": "List of models",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "data": {
                      "type": "array",
                      "items": {
                        "$ref": "#/components/schemas/ModelInfo"
                      }
                    }
                  }
                }
              }
            }
          },
          "401": {
            "description": "Unauthorized",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Error"
                }
              }
            }
          }
        }
      }
    },
    "/completions": {
      "post": {
        "summary": "Create completion",
        "operationId": "createCompletion",
        "security": [
          {
            "bearerAuth": []
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/Completion"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/CompletionResponse"
                }
              }
            }
          },
          "400": {
            "description": "Bad request",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Error"
                }
              }
            }
          }
        }
      }
    }
  }
}