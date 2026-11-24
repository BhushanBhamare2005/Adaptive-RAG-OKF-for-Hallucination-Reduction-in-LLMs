from app.services import file_storage


def test_existing_supabase_bucket_is_not_created_again(monkeypatch):
    class Response:
        status_code = 200

        def raise_for_status(self):
            raise AssertionError("Existing buckets should not trigger a create request.")

    calls = []
    monkeypatch.setattr(file_storage, "_supabase_config", lambda: ("https://storage.example", "secret"))
    monkeypatch.setattr(file_storage.httpx, "get", lambda *args, **kwargs: (calls.append("get"), Response())[1])
    monkeypatch.setattr(
        file_storage.httpx,
        "post",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("Bucket already exists.")),
    )

    file_storage.ensure_storage_bucket()

    assert calls == ["get"]


def test_missing_supabase_bucket_is_created(monkeypatch):
    class Response:
        def __init__(self, status_code):
            self.status_code = status_code

        def raise_for_status(self):
            if self.status_code >= 400:
                raise AssertionError(f"Unexpected HTTP status: {self.status_code}")

    calls = []

    def get(*_args, **_kwargs):
        calls.append("get")
        return Response(404)

    def post(*_args, **kwargs):
        calls.append(("post", kwargs["json"]["id"]))
        return Response(200)

    monkeypatch.setattr(file_storage, "_supabase_config", lambda: ("https://storage.example", "secret"))
    monkeypatch.setattr(file_storage.httpx, "get", get)
    monkeypatch.setattr(file_storage.httpx, "post", post)

    file_storage.ensure_storage_bucket()

    assert calls == ["get", ("post", file_storage.SUPABASE_BUCKET)]
