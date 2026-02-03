import json

class ResultParsingModule:
    """
    Module for parsing complex graph data into natural language.
    """
    @staticmethod
    def parse_query_results(results: list[dict]) -> str:
        """
        Converts a list of query result dictionaries into a natural language string.
        """
        if not results:
            return "未找到相关数据。"
        
        lines = []
        for i, row in enumerate(results, 1):
            row_str = ", ".join([f"{k}: {v}" for k, v in row.items()])
            lines.append(f"{i}. {row_str}")
        
        return "\n".join(lines)

    @staticmethod
    def parse_entity_details(details: dict) -> str:
        """
        Converts entity details into a readable description.
        """
        eid = details.get("id", "Unknown")
        props = details.get("properties", {})
        rels = details.get("relations", [])
        
        description = f"实体 ID: {eid}\n"
        
        if props:
            description += "属性:\n"
            for k, v in props.items():
                # Clean up predicate names if they are URIs
                prop_name = k.split("/")[-1] if "/" in k else k
                description += f"  - {prop_name}: {v}\n"
        
        if rels:
            description += "关系:\n"
            for rel in rels:
                pred = rel["predicate"].split("/")[-1] if "/" in rel["predicate"] else rel["predicate"]
                obj = rel["object"].split("/")[-1] if "/" in rel["object"] else rel["object"]
                description += f"  - 与 {obj} 存在 {pred} 关系\n"
                
        return description

    @staticmethod
    def format_for_llm(context: str, results: str) -> str:
        """
        Formats the parsed results for the LLM prompt.
        """
        return f"""
基于以下查询结果和上下文信息，请回答用户的问题：

[查询结果]
{results}

[上下文]
{context}
"""
