
# Index Component Template 삭제
DELETE _component_template/item_v1_component

# Index Component Template 생성
PUT _component_template/item_v1_component
{
  "template": {
    "settings": {
      "analysis": {
        "tokenizer": {
          "nori_tokenizer": {
            "type": "nori_tokenizer"
          }
        },
        "analyzer": {
          "nori_analyzer": {
            "type": "custom",
            "tokenizer": "nori_tokenizer"
          }
        },
        "normalizer": {
          "lowercase_normalizer": {
            "type": "custom",
            "char_filter": [],
            "filter": ["lowercase"]
          }
        }
      }
    },
    "mappings": {
      "dynamic_templates": [
        {
          "strings_as_keyword": {
            "match_mapping_type": "string",
            "mapping": {
              "type": "keyword"
            }
          }
        }
      ],
      "properties": {
        "created_at": {
          "type": "date"
        },
        "title": {
          "type": "text",
          "analyzer": "nori_analyzer",
          "copy_to": "title_suggest"
        },
        "title_suggest": {
          "type": "completion",
          "analyzer": "simple"
        }
      }
    }
  }
}

# Create article index template
PUT _index_template/item_v1_template
{
  "index_patterns": ["item_v1_*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1
    },
    "mappings": {},
    "aliases": {
      "item_v1": {}
    }
  },
  "composed_of": ["item_v1_component"],
  "version": 1,
  "_meta": {
    "description": "Template for item index"
  }
}
