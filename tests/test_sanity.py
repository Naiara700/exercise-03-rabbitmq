import yaml

def test_compose_has_four_services():
    with open("docker-compose.yml") as f:
        compose = yaml.safe_load(f)
    assert len(compose.get("services", {})) >= 4

def test_consumer_exists():
    from pathlib import Path
    assert Path("consumer/main.py").exists()
