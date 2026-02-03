try:
    from langchain_core.pydantic_v1 import BaseModel, Field
except ImportError:
    from pydantic import BaseModel, Field
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from .manager import OntologyManager
import os

class EntityModel(BaseModel):
    id: str = Field(description="Unique identifier for the entity")
    type: str = Field(description="Entity type (e.g. Person, Organization)")
    properties: dict = Field(description="Entity properties")

class RelationModel(BaseModel):
    source_id: str = Field(description="Source entity ID")
    target_id: str = Field(description="Target entity ID")
    type: str = Field(description="Relation type")
    properties: dict = Field(default={}, description="Relation properties")

class ExtractionResult(BaseModel):
    entities: List[EntityModel]
    relations: List[RelationModel]

class LLMExtractor:
    def __init__(self, manager: OntologyManager, model_name="deepseek-chat"):
        if ChatOpenAI is None:
            raise ImportError("Missing dependency: install 'langchain-openai'")
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base="https://api.deepseek.com",
            temperature=0
        )
        self.manager = manager
        self.parser = PydanticOutputParser(pydantic_object=ExtractionResult)

    def extract_from_text(self, text: str):
        prompt = PromptTemplate(
            template="""Extract knowledge graph entities and relations from the following text.
            
            Text: {text}
            
            {format_instructions}
            """,
            input_variables=["text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        chain = prompt | self.llm | self.parser
        try:
            result = chain.invoke({"text": text})
            
            # Save to ontology
            for ent in result.entities:
                self.manager.create_entity(ent.type, ent.properties, ent.id)
            
            for rel in result.relations:
                self.manager.create_relation(rel.source_id, rel.type, rel.target_id, rel.properties)
                
            return result
        except Exception as e:
            print(f"Extraction failed: {e}")
            return None
