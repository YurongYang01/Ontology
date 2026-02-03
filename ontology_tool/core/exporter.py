from rdflib import Graph, URIRef, Literal, RDF, RDFS, Namespace
from .manager import OntologyManager

class RDFExporter:
    def __init__(self, manager: OntologyManager):
        self.manager = manager

    def export_turtle(self) -> str:
        g = Graph()
        EX = Namespace("http://example.org/ontology/")
        g.bind("ex", EX)

        entities, relations = self.manager.load_graph()

        # Add entities
        for eid, data in entities.items():
            # Sanitize ID
            safe_id = URIRef(EX[eid.replace(" ", "_")])
            # Type
            g.add((safe_id, RDF.type, URIRef(EX[data["type"]])))
            # Properties
            for k, v in data["properties"].items():
                g.add((safe_id, URIRef(EX[k]), Literal(v)))

        # Add relations
        for rel in relations:
            src = URIRef(EX[rel["from"].replace(" ", "_")])
            dst = URIRef(EX[rel["to"].replace(" ", "_")])
            pred = URIRef(EX[rel["rel"]])
            g.add((src, pred, dst))

        return g.serialize(format="turtle")
