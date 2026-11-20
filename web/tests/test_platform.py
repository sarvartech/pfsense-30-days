
import pytest
from fastapi.testclient import TestClient

from app.content import get_catalog
from app.main import app
from app.security import hash_password, verify_password


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def register(client, email, password="parol12345"):
    return client.post(
        "/register",
        data={"name": "Test", "email": email, "password": password, "password2": password},
        follow_redirects=False,
    )


def test_password_hashing():
    h = hash_password("secret-pass")
    assert verify_password("secret-pass", h)
    assert not verify_password("wrong", h)
    assert not verify_password("x", "garbage")


def test_catalog_loads_without_errors():
    cat = get_catalog()
    assert not cat.errors, cat.errors
    assert "pfsense" in cat.courses and "tarmoq-asoslari" in cat.courses
    assert len(cat.courses["pfsense"].available_lessons) == 60
    assert {"linux-basics", "ospf-triangle", "bgp-basic", "wireguard-p2p", "vlan-switching"} <= set(cat.labs)
    # dars sahifalaridagi lablar katalogda mavjud
    for c in cat.courses.values():
        for lsn in c.lessons:
            if lsn.lab:
                assert lsn.lab in cat.labs, (c.slug, lsn.slug)


def test_public_pages(client):
    assert client.get("/").status_code == 200
    assert client.get("/courses/pfsense").status_code == 200
    r = client.get("/courses/pfsense/kun-01")
    assert r.status_code == 200 and "FreeBSD" in r.text
    # nisbiy lab.md/lecture.md havolalari platforma URL ga aylantirilgan
    r = client.get("/courses/pfsense/kun-01-lab")
    assert 'href="/courses/pfsense/kun-01"' in r.text
    assert client.get("/courses/tarmoq-asoslari/osi-tcpip").status_code == 200
    assert client.get("/labs").status_code == 200
    assert client.get("/courses/nope").status_code == 404
    assert client.get("/courses/pfsense/nope").status_code == 404


def test_mermaid_rendered(client):
    r = client.get("/courses/tarmoq-asoslari/osi-tcpip")
    assert '<pre class="mermaid">' in r.text


def test_auth_quiz_progress_flow(client):
    assert client.get("/dashboard", follow_redirects=False).status_code == 303
    r = register(client, "talaba@example.com")
    assert r.status_code == 303
    assert register(client, "talaba@example.com").status_code == 400  # takroriy

    lesson = get_catalog().courses["tarmoq-asoslari"].get_lesson("osi-tcpip")
    answers = {f"q{i}": str(q.answer) for i, q in enumerate(lesson.quiz)}
    r = client.post("/courses/tarmoq-asoslari/osi-tcpip/quiz", data=answers)
    assert r.status_code == 200 and "dars tugallandi" in r.text
    r = client.get("/dashboard")
    assert "Tarmoq asoslari" in r.text

    # boshqa Origin dan POST rad etiladi (CSRF)
    r = client.post("/logout", headers={"origin": "https://evil.example"})
    assert r.status_code == 403
    client.post("/logout")
    r = client.post("/login", data={"email": "talaba@example.com", "password": "xato-parol"})
    assert r.status_code == 400


def test_admin_access(client):
    client.cookies.clear()
    register(client, "admin@example.com")
    assert client.get("/admin").status_code == 200
    client.post("/logout")
    register(client, "oddiy@example.com")
    assert client.get("/admin").status_code == 403


def test_term_auth_denies_without_lab(client):
    r = client.get("/internal/term-auth", headers={"x-forwarded-uri": "/term/abcdef1234/"})
    assert r.status_code == 403
    client.post("/logout")
    r = client.get("/internal/term-auth", headers={"x-forwarded-uri": "/term/abcdef1234/"})
    assert r.status_code == 401


def test_lab_start_disabled_without_agent(client):
    register(client, "lab@example.com")
    r = client.post("/labs/start", data={"topology": "linux-basics"}, follow_redirects=True)
    assert r.status_code == 200
    assert "chirilgan" in r.text
