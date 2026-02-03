import logging
from rdflib import Graph, Namespace, URIRef, Literal, RDF
from ontology_tool.core.manager import OntologyManager
from ontology_tool.core.exporter import RDFExporter
import time

logger = logging.getLogger(__name__)

class OntologyQueryModule:
    """
    Module for querying ontology data using SPARQL.
    """
    def __init__(self, manager: OntologyManager):
        self.manager = manager
        self.ns = Namespace("http://example.org/ontology/")
        self._rdf_graph = None
        self._last_load_time = 0
        self._cache_ttl = 60  # Cache for 60 seconds

    def _get_rdf_graph(self) -> Graph:
        """
        Loads the graph into rdflib and caches it.
        """
        current_time = time.time()
        if self._rdf_graph is None or (current_time - self._last_load_time) > self._cache_ttl:
            logger.info("Loading RDF graph for querying...")
            exporter = RDFExporter(self.manager)
            turtle_data = exporter.export_turtle()
            g = Graph()
            g.parse(data=turtle_data, format="turtle")
            self._rdf_graph = g
            self._last_load_time = current_time
        return self._rdf_graph

    def query_sparql(self, sparql_query: str) -> list[dict]:
        """
        Executes a SPARQL query and returns the results as a list of dictionaries.
        """
        start_time = time.time()
        try:
            g = self._get_rdf_graph()
            results = g.query(sparql_query)
            
            parsed_results = []
            for row in results:
                row_dict = {}
                for var in results.vars:
                    val = row[var]
                    if isinstance(val, URIRef):
                        # Strip namespace for readability
                        row_dict[str(var)] = str(val).replace(str(self.ns), "")
                    else:
                        row_dict[str(var)] = str(val)
                parsed_results.append(row_dict)
            
            execution_time = time.time() - start_time
            logger.info(f"SPARQL query executed in {execution_time:.3f}s")
            return parsed_results
        except Exception as e:
            logger.error(f"Error executing SPARQL query: {e}")
            raise

    def query_by_type(self, type_name: str) -> list[dict]:
        """
        Simple query to get all entities of a specific type.
        """
        query = f"""
        PREFIX ex: <http://example.org/ontology/>
        SELECT ?id ?prop ?value
        WHERE {{
            ?id a ex:{type_name} .
            ?id ?prop ?value .
        }}
        """
        return self.query_sparql(query)

    def get_entity_details(self, entity_id: str) -> dict:
        """
        Gets all properties and relations for a specific entity.
        """
        query = f"""
        PREFIX ex: <http://example.org/ontology/>
        SELECT ?prop ?value
        WHERE {{
            ex:{entity_id} ?prop ?value .
        }}
        """
        results = self.query_sparql(query)
        details = {"id": entity_id, "properties": {}, "relations": []}
        
        for row in results:
            prop = row["prop"]
            value = row["value"]
            # Check if value is another entity (simplified check)
            if "/" not in str(value) or "http" not in str(value): # it's likely a literal or relative URI
                details["properties"][prop] = value
            else:
                details["relations"].append({"predicate": prop, "object": value})
        
        return details
