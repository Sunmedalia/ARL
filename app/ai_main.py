"""Independent Flask entry point for streaming AI traffic."""

from flask import Flask

from app.routes.ai import ai_blueprint


ai_app = Flask(__name__)
ai_app.config.update(
    BUNDLE_ERRORS=True,
    MAX_CONTENT_LENGTH=256 * 1024,
)
ai_app.register_blueprint(ai_blueprint)


@ai_app.get("/healthz")
def healthz():
    return {"status": "ok"}


if __name__ == "__main__":
    ai_app.run(host="127.0.0.1", port=5014, threaded=True)
