# Accidental Dignity Structure

This is an example of the structure of the accidental dignity data object. It is stored in a `CalculatedChart` object under `.metadata["accidental_dignities"]`.

```python
accidental_results = {
    "Sun": {
        "planet": "Sun",
        "by_system": {
            "Placidus": {
                "score": 7,
                "house": 10,
                "conditions": [
                    {
                        "type": "angular_house",
                        "value": 5,
                        "description": "In angular house 10 (Placidus)"
                    },
                    {
                        "type": "joy",
                        "value": 5,
                        "description": "Sun in its joy (house 9 in Placidus)"
                    }
                ]
            },
            "Whole Sign": {
                "score": 3,
                "house": 11,
                "conditions": [
                    {
                        "type": "succedent_house",
                        "value": 3,
                        "description": "In succedent house 11 (Whole Sign)"
                    }
                ]
            }
        },
        "universal_conditions": {
            "score": 4,
            "conditions": [
                {
                    "type": "direct",
                    "value": 4,
                    "description": "Sun is direct (not retrograde)"
                },
                {
                    "type": "swift",
                    "value": 2,
                    "description": "Sun is swift in motion"
                }
            ]
        }
    }
}
```
