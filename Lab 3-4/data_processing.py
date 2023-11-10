# Python program to read
# json file

import json
from typing import List

class GraphConcept(object):
    def __init__(self, uri, description, key_words = {}):
        self.name = uri.split("/")[-1]
        self.uri = uri
        self.description = description
        self.key_words = key_words

    def to_dict(self):
        return {
            'name': self.name,
            'uri': self.uri,
            'description': self.description,
            'key_words': self.key_words
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['uri'], data['description'], data['key_words'])

    def __str__(self):
        return f"{self.name} | {self.uri} | {self.description} | {self.key_words}\n"

def get_data(filename:str) -> List[GraphConcept]:
    f = open(filename)
    data = json.load(f)
    f.close()
    results = data["results"]
    bindings = results["bindings"]
    entries = []
    for binding in bindings:
        uri = binding["c1"]["value"]
        description = binding["c2"]["value"].replace("<b>", "").replace("</b>", "").replace(",","").replace(".","").replace(":","").lower()
        entry = GraphConcept(uri, description)
        entries.append(entry)
    return entries

stop_words = {"am", "can", "down", "from", "as", "be", "are", "too", "through", "does", "a", "but", "now", "some", "an", "we", "below", "against", "here", "did", "how", "yourselves", "was", "above", "him", "it", "which", "himself", "its", "most", "the", "re", "or", "while", "your", "if", "yours", "she", "her", "other", "any", "off", "few", "is", "of", "there", "than", "why", "has", "so", "in", "only", "have", "itself", "for", "under", "own", "were", "those", "out", "very", "until", "hers", "after", "up", 
"they", "their", "not", "doing", "no", "them", "where", "ourselves", "themselves", "our", "on", "that", "nor", "ours", "at", "again", "same", "over", "just", "because", "who", "before", "by", "more", "being", "had", "this", "with", "should", "what", "during", "herself", "and", "these", "such", "further", "do", "yourself", "his", "into", "once", "each", "all", "then", "both", "when", "he", "me", "whom", "i", "my", "you", "to", "myself", "about", "been", "will", "between"}

def create_inverted_index(entries:List[GraphConcept]) -> dict:
    invert_index = {}
    for entry in entries:
        words = entry.description.split()
        entry.key_words = {w:1 for w in words if w not in stop_words and len(w) > 3 and (not all(char.isdigit() for char in w))}
        for word in entry.key_words:
            if word not in invert_index:
                invert_index[word] = 1
            else: 
                invert_index[word] += 1
    sorted_index = {k: v for k, v in sorted(invert_index.items(), key=lambda item: item[1])}
    return sorted_index

# write function that sets the frequency of each word as thay are in the inverted index
def update_frequencies(entries:List[GraphConcept], inverted_index:dict):
    for entry in entries:
        for word in entry.key_words:
            entry.key_words[word] = inverted_index[word]
    

def write_to_file(entries:List[GraphConcept], filename:str):
    converted = [w.to_dict() for w in entries]
    with open(filename, 'w') as convert_file: 
        convert_file.write(json.dumps(converted))

def merge_duplicates(entries:List[GraphConcept]) -> List[GraphConcept]:
    merged_graph_concepts = {}
    for concept in entries:
        if concept.name not in merged_graph_concepts.keys():
            merged_graph_concepts[concept.name] = concept
        else:
            len1 = len(merged_graph_concepts[concept.name].description)
            len2 = len(concept.description)
            if len1 < len2:
                merged_graph_concepts[concept.name].description = concept.description
            for word in concept.key_words:
                if word not in merged_graph_concepts[concept.name].key_words:
                    merged_graph_concepts[concept.name].key_words[word] = concept.key_words[word]
                else:
                    merged_graph_concepts[concept.name].key_words[word] = max(concept.key_words[word], merged_graph_concepts[concept.name].key_words[word])

    return list(merged_graph_concepts.values())


#################################################################

entries = get_data('raw_data_from_dbpedia.json')
invert_index = create_inverted_index(entries)
update_frequencies(entries, invert_index)
entries = sorted(entries, key=lambda x: x.name)

unique_graph_concepts = merge_duplicates(entries)

all_key_words = {}
for concept in unique_graph_concepts:
    all_key_words.update(concept.key_words)

for i in range(10):
    print(unique_graph_concepts[i].key_words)

write_to_file(unique_graph_concepts, 'converted_data.json')

all_key_words_sorted = dict(sorted(all_key_words.items(), key=lambda item: item[1]))
sum_of_values = sum(all_key_words_sorted.values())
all_key_words_sorted_with_freq = {key: (value, value/sum_of_values) for key, value in all_key_words_sorted.items()}

for concept in unique_graph_concepts:
    for key in concept.key_words:
        concept.key_words[key] = all_key_words_sorted_with_freq[key]

print(unique_graph_concepts[0])
write_to_file(unique_graph_concepts, 'unique_graph_concepts_with_freq.json')
print(len(unique_graph_concepts))
# base: concepts + key words
# вивести дотичні поняття