import pandas as pd
import json
from .manager import OntologyManager

class DataImporter:
    def __init__(self, manager: OntologyManager):
        self.manager = manager

    def import_csv(self, file, entity_type: str, id_col: str = None, mapping: dict = None):
        """
        Import entities from CSV.
        mapping: dict {csv_col: property_name}
        """
        df = pd.read_csv(file)
        count = 0
        for _, row in df.iterrows():
            props = {}
            # Apply mapping if provided, else use all columns
            if mapping:
                for csv_col, prop_name in mapping.items():
                    if csv_col in row:
                        props[prop_name] = row[csv_col]
            else:
                props = row.to_dict()
            
            # Clean NaN values
            props = {k: v for k, v in props.items() if pd.notna(v)}
            
            entity_id = str(row[id_col]) if id_col and id_col in row else None
            self.manager.create_entity(entity_type, props, entity_id)
            count += 1
        return count

    def import_json(self, file, entity_type: str):
        data = json.load(file)
        count = 0
        if isinstance(data, list):
            for item in data:
                self.manager.create_entity(entity_type, item)
                count += 1
        elif isinstance(data, dict):
             self.manager.create_entity(entity_type, data)
             count += 1
        return count
