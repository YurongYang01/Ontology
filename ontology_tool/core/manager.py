"""
Core ontology logic shared across the tool.
Wraps the original script logic into a reusable class structure.
"""
import json
import uuid
import yaml
from pathlib import Path
from datetime import datetime, timezone

class OntologyManager:
    def __init__(self, graph_path="memory/ontology/graph.jsonl", schema_path="memory/ontology/schema.yaml"):
        self.graph_path = Path(graph_path)
        self.schema_path = Path(schema_path)
        self.graph_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.graph_path.exists():
            self.graph_path.touch()

    def _append_op(self, record: dict):
        with open(self.graph_path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def _generate_id(self, type_name: str) -> str:
        prefix = type_name.lower()[:4]
        suffix = uuid.uuid4().hex[:8]
        return f"{prefix}_{suffix}"

    def load_graph(self) -> tuple[dict, list]:
        entities = {}
        relations = []
        if not self.graph_path.exists():
            return entities, relations
        
        with open(self.graph_path) as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                    
                op = record.get("op")
                if op == "create":
                    entity = record["entity"]
                    entities[entity["id"]] = entity
                elif op == "update":
                    eid = record["id"]
                    if eid in entities:
                        entities[eid]["properties"].update(record.get("properties", {}))
                        entities[eid]["updated"] = record.get("timestamp")
                elif op == "delete":
                    entities.pop(record["id"], None)
                elif op == "relate":
                    relations.append({
                        "from": record["from"],
                        "rel": record["rel"],
                        "to": record["to"],
                        "properties": record.get("properties", {})
                    })
        return entities, relations

    def create_entity(self, type_name: str, properties: dict, entity_id: str = None) -> dict:
        entity_id = entity_id or self._generate_id(type_name)
        timestamp = datetime.now(timezone.utc).isoformat()
        entity = {
            "id": entity_id,
            "type": type_name,
            "properties": properties,
            "created": timestamp,
            "updated": timestamp
        }
        self._append_op({"op": "create", "entity": entity, "timestamp": timestamp})
        return entity

    def create_relation(self, from_id: str, rel_type: str, to_id: str, properties: dict = {}):
        timestamp = datetime.now(timezone.utc).isoformat()
        record = {
            "op": "relate",
            "from": from_id,
            "rel": rel_type,
            "to": to_id,
            "properties": properties,
            "timestamp": timestamp
        }
        self._append_op(record)
        return record

    def get_stats(self):
        entities, relations = self.load_graph()
        return {
            "entity_count": len(entities),
            "relation_count": len(relations),
            "entity_types": list(set(e["type"] for e in entities.values())),
            "relation_types": list(set(r["rel"] for r in relations))
        }

    def clear_graph(self):
        if self.graph_path.exists():
            self.graph_path.unlink()
            self.graph_path.touch()
